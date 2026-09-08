#!/usr/bin/env python3
"""Run the beneficiary-side Studionet lifecycle. Prompts for the test key; never stores it."""

import getpass
import json

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = "0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91"
BENEFICIARY = "0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
RECEIVER = "0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6"
SCHEDULE_ID = 1
REVISION = 1
SUPPLY = 1_000_000_000


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def checkpoint(condition, label):
    if not condition:
        raise RuntimeError("CHECKPOINT FAILED: " + label)
    print("CHECKPOINT OK: " + label, flush=True)


def read(client, method, args=None):
    value = client.read_contract(address=CONTRACT, function_name=method, args=args or [])
    print("READ " + method + "=" + canonical(value), flush=True)
    return value


def write(client, method, args):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("WRITE " + method + " tx=" + str(tx), flush=True)
    try:
        receipt = client.wait_for_transaction_receipt(
            tx, status=TransactionStatus.FINALIZED, interval=3000,
            retries=500, full_transaction=False,
        )
        print("FINALIZED " + method + "=" + canonical(receipt), flush=True)
    except Exception as error:
        print("FINALIZATION_NOTICE " + method + "=" + repr(error), flush=True)
    return str(tx)


def conservation(client):
    info = read(client, "get_info")
    schedule = read(client, "get_schedule", [SCHEDULE_ID])
    beneficiary = int(read(client, "balance_of", [BENEFICIARY]))
    receiver = int(read(client, "balance_of", [RECEIVER]))
    total = int(info["treasury"]) + int(schedule["amount"]) - int(schedule["released"]) + beneficiary + receiver
    checkpoint(total == SUPPLY, "treasury + remaining locked + observed liquid balances equals fixed supply")


def main():
    secret = getpass.getpass("Beneficiary test private key: ").strip()
    account = create_account(secret)
    checkpoint(str(account.address).lower() == BENEFICIARY.lower(), "private key matches bound beneficiary")
    client = create_client(chain=studionet, account=account)

    before = read(client, "get_schedule", [SCHEDULE_ID])
    checkpoint(before["review"] == "PENDING" and int(before["decision_revision"]) == REVISION, "current pending revision loaded")
    checkpoint(before["beneficiary"].lower() == BENEFICIARY.lower(), "schedule beneficiary identity matches signer")
    checkpoint(int(read(client, "balance_of", [BENEFICIARY])) == 0, "beneficiary starts with zero released VEST")

    txs = {"assess": write(client, "assess_exception", [SCHEDULE_ID, REVISION])}
    assessed = read(client, "get_schedule", [SCHEDULE_ID])
    checkpoint(assessed["review"] == "ELIGIBLE", "canonical cancellation is eligible")
    checkpoint(len(assessed["receipt"]) == 64, "assessment publishes bounded receipt digest")

    txs["consume"] = write(client, "consume_exception", [SCHEDULE_ID, REVISION])
    consumed = read(client, "get_schedule", [SCHEDULE_ID])
    checkpoint(consumed["review"] == "CONSUMED" and consumed["exception_used"] is True, "authorization consumed once")
    checkpoint(int(consumed["released"]) == 25_000, "exact 25 percent policy cap released")
    checkpoint(int(read(client, "balance_of", [BENEFICIARY])) == 25_000, "beneficiary liquid balance credited atomically")

    replay_before = canonical(consumed)
    txs["replay"] = write(client, "consume_exception", [SCHEDULE_ID, REVISION])
    checkpoint(canonical(read(client, "get_schedule", [SCHEDULE_ID])) == replay_before, "replay leaves schedule unchanged")

    txs["transfer"] = write(client, "transfer", [RECEIVER, 1_000])
    checkpoint(int(read(client, "balance_of", [BENEFICIARY])) == 24_000, "sender debited after transfer")
    checkpoint(int(read(client, "balance_of", [RECEIVER])) == 1_000, "receiver credited after transfer")
    conservation(client)
    print("LIFECYCLE_COMPLETE transactions=" + canonical(txs), flush=True)


if __name__ == "__main__":
    main()
