# Adversarial live audit plan

Schedule 2 is isolated from the completed positive lifecycle. The owner signs authority transitions; the two supplied test wallets act only as beneficiary and outsider.

1. Create schedule 2 with the same beneficiary, 100,000 VEST, 2,500 bps cap, a future start and a 30-day end. Confirm treasury decreases exactly once.
2. Outsider attempts `record_cancellation`; expect `ONLY_DAO` and identical state.
3. Owner locks the conflict fixture at its fixed commit. Outsider attempts assessment; expect `ONLY_BENEFICIARY`. Beneficiary assessment must return `CONFLICT`, publish findings, and release nothing.
4. Owner replaces it with the clear fixture but an intentionally wrong digest. Beneficiary assessment must return `UNRESOLVED / DIGEST_MISMATCH`; a same-revision retry must remain fail-closed.
5. Owner records the exact clear digest at a new revision with a deliberately short expiry. Stale revision assessment must fail. Current revision assessment must become `ELIGIBLE`; after expiry, consume must fail and preserve balances.
6. Owner records the exact clear fixture again with a fresh expiry. Beneficiary reassesses and consumes. Replay fails. Verify treasury, remaining locked allocation and both liquid balances conserve the fixed supply.

No fixture is accepted from an arbitrary URL: repository is schedule-bound, commit is a full SHA, path is validated, raw bytes are capped and SHA-256 is recomputed by validators before JSON/semantic evaluation.
