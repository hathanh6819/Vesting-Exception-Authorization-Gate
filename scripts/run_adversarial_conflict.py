#!/usr/bin/env python3
"""Assess schedule 2 conflict evidence and prove it cannot be consumed."""

import getpass
import json

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = "0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91"
BENEFICIARY = "0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def write(client, method, args):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("WRITE " + method + " tx=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(tx, status=TransactionStatus.FINALIZED, interval=3000, retries=500, full_transaction=False)
    leaders = receipt.get("consensus_data", {}).get("leader_receipt", [])
    summary = [{"execution_result": item.get("execution_result"), "result": item.get("result"), "vote": item.get("vote")} for item in leaders]
    print("FINALIZED " + method + " result=" + str(receipt.get("result_name")) + " leaders=" + canonical(summary), flush=True)
    return str(tx)


def main():
    account = create_account(getpass.getpass("Beneficiary test private key: ").strip())
    if str(account.address).lower() != BENEFICIARY.lower():
        raise RuntimeError("CHECKPOINT FAILED: signer is not beneficiary")
    client = create_client(chain=studionet, account=account)
    before_balance = int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY]))
    pending = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if pending["review"] != "PENDING" or int(pending["decision_revision"]) != 1:
        raise RuntimeError("CHECKPOINT FAILED: conflict revision is not pending")
    assess_tx = write(client, "assess_exception", [2, 1])
    conflict = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if conflict["review"] != "CONFLICT" or conflict["findings"].get("conflicting_obligations") is not True:
        raise RuntimeError("CHECKPOINT FAILED: expected structured CONFLICT")
    if int(conflict["released"]) != 0 or int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY])) != before_balance:
        raise RuntimeError("CHECKPOINT FAILED: conflict changed accounting")
    print("CHECKPOINT OK: conflict publishes findings and releases nothing", flush=True)
    snapshot = canonical(conflict)
    consume_tx = write(client, "consume_exception", [2, 1])
    after = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    if canonical(after) != snapshot or int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY])) != before_balance:
        raise RuntimeError("CHECKPOINT FAILED: conflict consume mutated state")
    print("CHECKPOINT OK: conflict consume rolls back without state or balance change", flush=True)
    print("CONFLICT_PHASE_COMPLETE transactions=" + canonical({"assess": assess_tx, "blocked_consume": consume_tx}), flush=True)


if __name__ == "__main__":
    main()
