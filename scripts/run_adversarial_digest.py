#!/usr/bin/env python3
"""Prove stale revisions and mismatched evidence fail closed on Studionet."""

import getpass
import json

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = "0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91"
BENEFICIARY = "0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
WRONG_DIGEST = "f" * 64


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def write(client, method, args):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("WRITE " + method + " args=" + canonical(args) + " tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(
        tx, status=TransactionStatus.FINALIZED, interval=3000,
        retries=500, full_transaction=False,
    )
    leaders = receipt.get("consensus_data", {}).get("leader_receipt", [])
    summary = [
        {"execution_result": item.get("execution_result"), "result": item.get("result"), "vote": item.get("vote")}
        for item in leaders
    ]
    print("FINALIZED " + method + " result=" + str(receipt.get("result_name")) + " leaders=" + canonical(summary), flush=True)
    return str(tx)


def main():
    account = create_account(getpass.getpass("Beneficiary test private key: ").strip())
    if str(account.address).lower() != BENEFICIARY.lower():
        raise RuntimeError("CHECKPOINT FAILED: signer is not beneficiary")
    client = create_client(chain=studionet, account=account)
    initial = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    balance = int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY]))
    revision = int(initial["decision_revision"])
    if initial["review"] != "PENDING" or revision < 2 or initial["decision"]["digest"] != WRONG_DIGEST:
        raise RuntimeError("CHECKPOINT FAILED: wrong-digest revision is not pending")

    txs = {}
    before = canonical(initial)
    txs["stale_assess"] = write(client, "assess_exception", [2, revision - 1])
    if canonical(client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])) != before:
        raise RuntimeError("CHECKPOINT FAILED: stale assessment mutated state")
    print("CHECKPOINT OK: stale revision rolls back without mutation", flush=True)

    txs["digest_mismatch"] = write(client, "assess_exception", [2, revision])
    unresolved = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if unresolved["review"] != "UNRESOLVED" or unresolved["findings"] != {"reason": "DIGEST_MISMATCH"}:
        raise RuntimeError("CHECKPOINT FAILED: expected UNRESOLVED / DIGEST_MISMATCH")
    if int(unresolved["released"]) != 0 or int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY])) != balance:
        raise RuntimeError("CHECKPOINT FAILED: digest mismatch changed accounting")
    print("CHECKPOINT OK: validator fetches bytes, recomputes SHA-256, and fails closed", flush=True)

    unresolved_snapshot = canonical(unresolved)
    txs["same_revision_retry"] = write(client, "assess_exception", [2, revision])
    retried = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if canonical(retried) != unresolved_snapshot:
        raise RuntimeError("CHECKPOINT FAILED: deterministic retry changed unresolved state")
    print("CHECKPOINT OK: same-revision retry remains deterministically unresolved", flush=True)

    txs["blocked_consume"] = write(client, "consume_exception", [2, revision])
    if canonical(client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])) != unresolved_snapshot:
        raise RuntimeError("CHECKPOINT FAILED: unresolved consume mutated state")
    if int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY])) != balance:
        raise RuntimeError("CHECKPOINT FAILED: unresolved consume changed balance")
    print("CHECKPOINT OK: unresolved authorization cannot be consumed", flush=True)
    print("DIGEST_PHASE_COMPLETE transactions=" + canonical(txs), flush=True)


if __name__ == "__main__":
    main()
