# Version 3 live end-to-end evidence

This file is the canonical checklist and evidence record for the Multi-Party DAO Cancellation Quorum milestone. Do not mark an item complete until the transaction is finalized and its state readback is verified.

## Deployment

- Contract address: `PENDING`
- Deployment transaction: `PENDING`
- Deployed source SHA-256: `8999e9be0ffae6b4e9aa85dd5b40aaaa7beb9d4ce0fc73ce983c8e9f1cd1170a`
- `get_info` readback: `PENDING`
- Deployed/local source parity: `PENDING`

## Owner transactions

1. Call `configure_council(member_a, member_b, 2)` from the deployment owner.
2. Verify `get_governance()` returns the owner and both members, with threshold `2`.
3. Call `create_schedule(...)` from the owner after committing the exact v3 fixture.

Transactions and readbacks: `PENDING`

## Quorum lifecycle

1. Council member 1 calls `record_cancellation(...)` and receives proposal nonce `1`.
2. Verify `get_pending_decision(1)` is `AWAITING_QUORUM`, has one approval, and `get_schedule(1).decision_revision` is still `0`.
3. An outsider calls `approve_cancellation(1, 1)` and the transaction must finalize with `ONLY_COUNCIL` rollback.
4. The proposer calls `approve_cancellation(1, 1)` and the transaction must finalize with `ALREADY_APPROVED` rollback.
5. Council member 2 calls `approve_cancellation(1, 1)` successfully.
6. Verify the proposal is `ACTIVATED`, approval count is `2`, and schedule decision revision is `1` with review `PENDING`.
7. The beneficiary calls `assess_exception(1, 1)`, then `consume_exception(1, 1)`.
8. Verify the bounded release, single-use flag, beneficiary balance, treasury, and fixed-supply conservation.
9. Repeat `consume_exception(1, 1)` and record the expected `NOT_AUTHORIZED` rollback.

Transaction links and final state: `PENDING`

## Production application

- Production URL: `PENDING`
- Production commit: `PENDING`
- Browser verification of v3 identity and council threshold: `PENDING`
