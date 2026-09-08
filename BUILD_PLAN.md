# Vesting Exception Authorization Gate

## Scope and mechanism
Studionet prototype for milestone cancellation only. A fixed-supply, transferable VEST test token lives in the same contract as vesting schedules and the exception gate. No ERC-20 compatibility or external-asset custody is claimed. Token units are integers. Treasury allocation moves existing supply into locked schedules; normal vesting and exception settlement debit the same remaining allocation atomically.

The deployment owner is the DAO decision authority. Schedules cannot name the authority as beneficiary. Authority registers schedule, immutable policy and GitHub repository. It records a cancellation decision with commit, path, document SHA-256 and expiry; a beneficiary cannot manufacture this decision. This is an authenticated DAO attestation, not proof of a broader DAO vote. A future governance adapter is outside this version.

## Plan
1. Implement transferable VEST balances, fixed supply, linear vesting, normal claims and cancellation decisions.
2. Fetch full commit-pinned GitHub decision bytes and recompute the authority-committed SHA-256. Bind schedule, beneficiary, contract address and decision ID. Reject malformed, unavailable and oversized sources.
3. Validators classify only cancellation clarity and contradictory obligations; consensus binds document digest and findings. Deterministic code derives outcome and the cap in basis points. Snapshot storage before nondeterminism.
4. Consume approved authorization inside the asset contract, rechecking beneficiary, decision revision, expiry and remaining allocation. Exception is one-time per schedule. Normal claims remain live regardless of review failure.
5. Build original navy/white treasury workspace with supplied logo, real wallet reads/writes, transaction journal and explicit undeployed state.
6. Direct-contract tests: conservation, normal vesting, exception happy path, rejection, conflict, unavailable retry, poisoned ground truth, hash/identity mismatch, stale decision, expiry, race with normal claim and replay.
7. Frontend tests, clean production build, GenVM lint/schema, manual deployment instructions and source hash.
8. After user deployment: exact source parity; real positive assessment/consume and negative/recovery transactions; balance readbacks; configure production frontend. Do not mark submission-ready before this gate.

## Consequence invariants
Treasury + liquid balances + remaining locked allocations = fixed supply. No mint method. Transfer cannot access locked allocation. Settlement only accelerates the schedule up to its policy cap (`cap - already released`), and never increases the total allocation. A revoked/replaced decision invalidates unconsumed findings. Missing or contradictory evidence never releases tokens. Atomic consume requires no cross-contract acknowledgement.

## Originality
This is a vesting accounting engine with two competing release paths over one allocation. Schedule arithmetic bounds semantic exceptions; normal claims can race with authorization and settlement recomputes remaining value. There is no generic request-to-external-target authorization skeleton. Review is per schedule, authority decision versions supersede unconsumed findings, and asset movement plus consumption are atomic.

## Test resources
Direct Mode mocks only network and model boundaries while calling the actual contract. Public live resources require an authority-authored JSON decision at a fixed GitHub commit with the exact deployed contract address, schedule ID, beneficiary, decision ID and cancellation statement. Hash the complete UTF-8 bytes after committing. A positive and conflicting document are required; a missing path supplies recovery testing. No IPFS account or paid API is required. Live wallets: deployment authority, beneficiary, outsider; VEST comes from the fixed deployment supply, GEN is only needed for fees.
