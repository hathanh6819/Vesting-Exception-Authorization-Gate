# Version 3 live end-to-end evidence

This file is the canonical checklist and evidence record for the Multi-Party DAO Cancellation Quorum milestone. Do not mark an item complete until the transaction is finalized and its state readback is verified.

## Deployment

- Contract address: `0x6ABc04f05FB0e5450De3F17DDeE449A52a537022`
- Deployment transaction: not supplied; deployment is independently verified through live identity, ABI and exact source retrieval.
- Deployed source SHA-256: `8999e9be0ffae6b4e9aa85dd5b40aaaa7beb9d4ce0fc73ce983c8e9f1cd1170a`
- `get_info` readback: version 3; owner `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`; council threshold 2/3; treasury 999,900,000 VEST; one schedule.
- Deployed/local source parity: exact, 14,868 bytes; both SHA-256 `8999e9be0ffae6b4e9aa85dd5b40aaaa7beb9d4ce0fc73ce983c8e9f1cd1170a`.

## Owner transactions

1. Call `configure_council(member_a, member_b, 2)` from the deployment owner.
2. Verify `get_governance()` returns the owner and both members, with threshold `2`.
3. Call `create_schedule(...)` from the owner after committing the exact v3 fixture.

Council configuration transaction: `0xb266ed5afe6ec3bf5cd5e0826b5dd4489ca16a5d987aa96c2027fb62a109fbc8`.

Schedule creation transaction: `0x592ccbad1416218816b22165edfcec236f98dc83e621c90f8c01f74225825023`. Readback confirms schedule 1, beneficiary `0x260d102f611c8a100e3f9036cf51544d148ee293`, allocation 100,000 VEST, 25% exception cap, revision 0, review `NONE`, and released 0. Treasury decreased exactly once from 1,000,000,000 to 999,900,000.

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

Proposal transaction: `0x047137b849f3c7d1cbb52811e8b325e509a37e44eb471bb9e4ea3da26e74f0bc`. Readback proved status `AWAITING_QUORUM`, approvals 1, and schedule revision remained 0.

Quorum activation transaction: `0xc7cf66a6a2a5f5dbd0a79168590f6809cf396ef150b6816fef411abd0af5e96d`. Council member `0x1d283b45974b0be9630dfd1dec6a62a9b72b2760` supplied the distinct second approval. The finalized result was `MAJORITY_AGREE / ACTIVATED`; schedule revision became 1 and review became `PENDING`.

Assessment transaction: `0xa738e2634805869efd2207e46f7e28260860537a4eb95f4d3608c55c386fb3dd`. It finalized `MAJORITY_AGREE`; findings were cancellation explicit true, policy covered true, conflicting obligations false. The deterministic result was `ELIGIBLE`, with receipt `32ab63ce6fdebd44b37c6f40c8332b3bab469e94367068b752ffcf6000159700` and no token release during review.

Consume transaction: `0xbf5080a8bd86c0e3acde8fd38342c12164325a213de5683bc88f5451e038f4ea`. It finalized `MAJORITY_AGREE`, atomically marked the exception consumed and released exactly 25,000 VEST. Beneficiary liquid balance became 25,000.

Replay transaction: `0x9028c94fd611005ef62e9622060b6766445505db8d3aee16f1b752552cee115c`. The call finalized without altering state: schedule remained `CONSUMED`, released remained 25,000 and the balance remained 25,000. Treasury 999,900,000 + remaining locked 75,000 + liquid 25,000 equals the fixed 1,000,000,000 supply.

## Production application

- Production URL: `PENDING`
- Production commit: `PENDING`
- Browser verification of v3 identity and council threshold: `PENDING`
