#!/usr/bin/env python3
"""Run the live v3 beneficiary lifecycle using the ignored local test wallet."""

import json
from pathlib import Path

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = "0x6ABc04f05FB0e5450De3F17DDeE449A52a537022"
BENEFICIARY = "0x260d102F611c8A100e3f9036Cf51544d148ee293"
SCHEDULE_ID = 1
REVISION = 1


def local_secret():
    values = {}
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values["BENEFICIARY_PRIVATE_KEY"]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def read(client, method, args=None):
    value = client.read_contract(address=CONTRACT, function_name=method, args=args or [])
    print("READ " + method + "=" + canonical(value), flush=True)
    return value


def write(client, method, args):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("WRITE " + method + " tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(
        tx, status=TransactionStatus.FINALIZED, interval=3000,
        retries=500, full_transaction=False,
    )
    result = receipt.get("consensus_data", {}).get("leader_receipt", [{}])[0].get("genvm_result", {}).get("result", {})
    print("FINALIZED " + method + "=" + canonical(dict(hash=str(tx), status=receipt.get("status_name"), result=receipt.get("result_name"), execution=result)), flush=True)
    return str(tx)


def main():
    account = create_account(local_secret())
    assert str(account.address).lower() == BENEFICIARY.lower()
    client = create_client(chain=studionet, account=account)
    before = read(client, "get_schedule", [SCHEDULE_ID])
    assert before["review"] == "PENDING" and int(before["decision_revision"]) == REVISION
    txs = {"assess": write(client, "assess_exception", [SCHEDULE_ID, REVISION])}
    assessed = read(client, "get_schedule", [SCHEDULE_ID])
    assert assessed["review"] == "ELIGIBLE" and len(assessed["receipt"]) == 64
    txs["consume"] = write(client, "consume_exception", [SCHEDULE_ID, REVISION])
    consumed = read(client, "get_schedule", [SCHEDULE_ID])
    balance = int(read(client, "balance_of", [BENEFICIARY]))
    assert consumed["review"] == "CONSUMED" and consumed["exception_used"] is True
    assert int(consumed["released"]) == 25000 and balance == 25000
    txs["replay"] = write(client, "consume_exception", [SCHEDULE_ID, REVISION])
    replay_state = read(client, "get_schedule", [SCHEDULE_ID])
    assert replay_state == consumed
    print("TRANSACTIONS=" + canonical(txs), flush=True)


if __name__ == "__main__":
    main()
