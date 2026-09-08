# Local verification — 2026-09-08

Contract source SHA-256: `2f237cb97bdc7f01805e3638e7bdd9b51d89112c657b04a027946b235e20b38f`.

- `python -m pytest`: 32 passed. This covers happy path, conflict/ineligible results, complete-byte digest and every bound identity, unavailable-source recovery, stale/revoked/expired decisions, replay, unauthorized callers, invalid inputs without mutation, supply conservation, normal vesting and claim/exception races. A Direct Mode adapter executes the captured strict-equality validator function and proves changed findings vote false. Direct Mode does not reproduce GenVM sandbox isolation; live validator verification remains required after deployment.
- `genvm-lint check contracts/vesting_exception_gate.py --json`: lint and semantic validation passed; contract `VestingExceptionAuthorizationGate`, 10 public methods, 3 views, 7 writes and no constructor parameters. The informational notice about a newer runner was not followed because this project uses the playbook's frozen deployment header.
- `frontend: npm test`: 3 passed (input validation, timestamps, execution-receipt classification). These are utility tests, not browser workflow tests.
- `frontend: npm run build`: passed, Vite 7.3.6, 454 modules. Initial application JS approximately 10.27 kB before gzip; SDK separately loaded.
- `frontend: npm audit --omit=dev --audit-level=high`: 0 vulnerabilities reported.
- Chrome headless production smoke render passed at 1440 × 1200; `frontend-smoke.png` records the undeployed, no-fallback initial state. Local HTTP returned 200 for the application and `image/png` for the logo.
- Supplied logo copied unchanged into `frontend/public/logo.png`.

## Outstanding gates

Verified Studionet deployment: `0x003383481158c03C9b3B820af829172e994aB944`.

- Live `get_info`: name `VestingExceptionAuthorizationGate`, version `1`, owner `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`, symbol `VEST`, internal test-token flag true, total supply and treasury both `1,000,000,000`, schedule count `0`.
- `getContractCode` returned 10,278 source characters. Its UTF-8 SHA-256 is `2f237cb97bdc7f01805e3638e7bdd9b51d89112c657b04a027946b235e20b38f`, exactly matching the final local contract.
- Live ABI contains the expected 10 public methods (3 views, 7 nonpayable writes) and no constructor parameters.
- The frontend production build is configured for this verified address.

Post-deploy browser integration: account/network changes during asynchronous reads, contract changes, stale revisions, expired decision, unavailable evidence retry, transaction timeout/reconciliation, successful and blocked release flow. These require a real contract address and wallets.

Runtime: exact pinned dependency/schema verification on GenVM and validator disagreement replay in the real sandbox. Local lint and the Direct Mode validator adapter are not deployment proof.

Studionet: deployment and source parity are verified. Remaining: create a schedule, publish authority-bound fixtures using the actual deployment and schedule identities, complete positive consume/transfer and failure/recovery paths, and retain finalized transaction records plus before/after accounting. No lifecycle transaction has been sent for this project yet.

Production: configure the verified contract address, verify hosted frontend against that deployment, then publish reproducible evidence. No hosting or GitHub push has been performed yet.
