#!/usr/bin/env python3
"""Prove outsider calls fail closed before the authority records schedule 2 evidence."""

import getpass
import json
import time

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = "0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91"
OUTSIDER = "0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6"
COMMIT = "aaa490637743723cee4cbb4e3abb95d6d348d3c2"
PATH = "fixtures/adversarial/schedule-2-conflict.json"
DIGEST = "71975755b0f983527a9acc99b785f0106d9e8de01b8f663846fa44e2143e91cc"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def write(client, method, args):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("WRITE " + method + " tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(
        tx, status=TransactionStatus.FINALIZED, interval=3000,
        retries=300, full_transaction=False,
    )
    print("FINALIZED " + method + " result=" + str(receipt.get("result_name")) + " leader=" + canonical(receipt.get("consensus_data", {}).get("leader_receipt", [])), flush=True)
    return str(tx)


def main():
    secret = getpass.getpass("Outsider test private key: ").strip()
    account = create_account(secret)
    if str(account.address).lower() != OUTSIDER.lower():
        raise RuntimeError("CHECKPOINT FAILED: key is not the designated outsider")
    client = create_client(chain=studionet, account=account)
    before = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if before["review"] != "NONE" or int(before["decision_revision"]) != 0:
        raise RuntimeError("CHECKPOINT FAILED: schedule 2 is not fresh")
    txs = {}
    txs["outsider_record"] = write(client, "record_cancellation", [2, "OUTSIDER-MUST-FAIL", COMMIT, PATH, DIGEST, int(time.time()) + 86400])
    after_record = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if canonical(after_record) != canonical(before):
        raise RuntimeError("CHECKPOINT FAILED: outsider record mutated state")
    print("CHECKPOINT OK: ONLY_DAO path leaves schedule unchanged", flush=True)
    txs["outsider_assess"] = write(client, "assess_exception", [2, 0])
    after_assess = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if canonical(after_assess) != canonical(before):
        raise RuntimeError("CHECKPOINT FAILED: outsider assess mutated state")
    print("CHECKPOINT OK: ONLY_BENEFICIARY path leaves schedule unchanged", flush=True)
    print("PHASE1_COMPLETE transactions=" + canonical(txs), flush=True)


if __name__ == "__main__":
    main()
