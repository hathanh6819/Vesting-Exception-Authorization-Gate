#!/usr/bin/env python3
"""Complete live recovery, one-shot consumption, replay and conservation checks."""

import getpass
import json

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT = "0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91"
BENEFICIARY = "0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
RECEIVER = "0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6"
CORRECT_DIGEST = "7398b0d81dfb322201788a098ad36d9e1edbd5883c2c1b08653c73c8d7f04adb"
SUPPLY = 1_000_000_000


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
    pending = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    revision = int(pending["decision_revision"])
    before_balance = int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY]))
    if pending["review"] != "PENDING" or revision != 4 or pending["decision"]["digest"] != CORRECT_DIGEST:
        raise RuntimeError("CHECKPOINT FAILED: exact recovery revision 4 is not pending")

    txs = {"assess_recovery": write(client, "assess_exception", [2, revision])}
    eligible = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    findings = eligible.get("findings") or {}
    if eligible["review"] != "ELIGIBLE" or findings.get("cancellation_explicit") is not True or findings.get("policy_covered") is not True or findings.get("conflicting_obligations") is not False:
        raise RuntimeError("CHECKPOINT FAILED: corrected canonical evidence is not eligible")
    if len(eligible["receipt"]) != 64 or int(eligible["released"]) != 0:
        raise RuntimeError("CHECKPOINT FAILED: assessment receipt/release invariant failed")
    print("CHECKPOINT OK: corrected evidence is fetched, hashed and assessed ELIGIBLE without release", flush=True)

    txs["consume_once"] = write(client, "consume_exception", [2, revision])
    consumed = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    after_balance = int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY]))
    if consumed["review"] != "CONSUMED" or consumed["exception_used"] is not True or int(consumed["released"]) != 25_000:
        raise RuntimeError("CHECKPOINT FAILED: one-shot cap was not consumed exactly")
    if after_balance - before_balance != 25_000:
        raise RuntimeError("CHECKPOINT FAILED: beneficiary accounting delta is not 25,000")
    print("CHECKPOINT OK: exactly 25,000 VEST credited atomically", flush=True)

    snapshot = canonical(consumed)
    txs["replay"] = write(client, "consume_exception", [2, revision])
    if canonical(client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])) != snapshot:
        raise RuntimeError("CHECKPOINT FAILED: replay mutated schedule")
    if int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[BENEFICIARY])) != after_balance:
        raise RuntimeError("CHECKPOINT FAILED: replay changed beneficiary balance")
    print("CHECKPOINT OK: replay rolls back without state or balance change", flush=True)

    info = client.read_contract(address=CONTRACT, function_name="get_info", args=[])
    first = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[1])
    second = client.read_contract(address=CONTRACT, function_name="get_schedule", args=[2])
    receiver_balance = int(client.read_contract(address=CONTRACT, function_name="balance_of", args=[RECEIVER]))
    total = int(info["treasury"]) + sum(int(s["amount"]) - int(s["released"]) for s in (first, second)) + after_balance + receiver_balance
    if total != SUPPLY:
        raise RuntimeError("CHECKPOINT FAILED: fixed-supply conservation failed: " + str(total))
    print("CHECKPOINT OK: treasury + all remaining locks + observed liquid balances = 1,000,000,000", flush=True)
    print("RECOVERY_COMPLETE transactions=" + canonical(txs) + " final=" + canonical({"beneficiary": after_balance, "receiver": receiver_balance, "treasury": info["treasury"], "schedule_1_remaining": int(first["amount"])-int(first["released"]), "schedule_2_remaining": int(second["amount"])-int(second["released"]), "supply_check": total}), flush=True)


if __name__ == "__main__":
    main()
