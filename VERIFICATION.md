# Local verification — 2026-09-08

Corrected version 2 source SHA-256: `1094bf5e5006c56e3e6c96c7bd547612a8102b0a99b743061e638ffc13f5229c`.

- `python -m pytest`: 33 passed. This covers happy path, conflict/ineligible results, complete-byte digest and every bound identity, unavailable-source recovery, stale/revoked/expired decisions, replay, unauthorized callers, invalid inputs without mutation, supply conservation, normal vesting, claim/exception races, and the exact raw-string address representation observed on GenVM. A Direct Mode adapter executes the captured strict-equality validator function and proves changed findings vote false. Direct Mode does not reproduce GenVM sandbox isolation; live validator verification remains required after deployment.
- `genvm-lint check contracts/vesting_exception_gate.py --json`: lint and semantic validation passed; contract `VestingExceptionAuthorizationGate`, 10 public methods, 3 views, 7 writes and no constructor parameters. The informational notice about a newer runner was not followed because this project uses the playbook's frozen deployment header.
- `frontend: npm test`: 3 passed (input validation, timestamps, execution-receipt classification). These are utility tests, not browser workflow tests.
- `frontend: npm run build`: passed, Vite 7.3.6, 454 modules. Initial application JS approximately 10.27 kB before gzip; SDK separately loaded.
- `frontend: npm audit --omit=dev --audit-level=high`: 0 vulnerabilities reported.
- Chrome headless production smoke render passed at 1440 × 1200; `frontend-smoke.png` records the undeployed, no-fallback initial state. Local HTTP returned 200 for the application and `image/png` for the logo.
- Supplied logo copied unchanged into `frontend/public/logo.png`.

## Outstanding gates

Superseded Studionet deployment: `0x003383481158c03C9b3B820af829172e994aB944`.

- Live `get_info`: name `VestingExceptionAuthorizationGate`, version `1`, owner `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`, symbol `VEST`, internal test-token flag true, total supply and treasury both `1,000,000,000`, schedule count `0`.
- Version 1 `getContractCode` returned 10,278 source characters. Its UTF-8 SHA-256 is `2f237cb97bdc7f01805e3638e7bdd9b51d89112c657b04a027946b235e20b38f`, exactly matching the superseded local version 1 source at deployment time.
- Live ABI contains the expected 10 public methods (3 views, 7 nonpayable writes) and no constructor parameters.
- A real `create_schedule` failed with `AttributeError: 'str' object has no attribute 'as_hex'`; GenVM supplied the ABI address as text. Readback remained `schedule_count = 0` and treasury remained the full supply. Version 2 canonicalizes string, Address-object and numeric address forms at every public boundary, includes a raw-string regression, and makes the frontend reject version 1. A replacement deployment is required.

Post-deploy browser integration: account/network changes during asynchronous reads, contract changes, stale revisions, expired decision, unavailable evidence retry, transaction timeout/reconciliation, successful and blocked release flow. These require a real contract address and wallets.

Runtime: exact pinned dependency/schema verification on GenVM and validator disagreement replay in the real sandbox. Local lint and the Direct Mode validator adapter are not deployment proof.

Studionet: version 1 is superseded after the failed runtime transaction. Remaining: deploy exact corrected version 2, verify parity, create a schedule, publish authority-bound fixtures using actual deployment and schedule identities, complete positive consume/transfer and failure/recovery paths, and retain finalized transaction records plus before/after accounting.

## Corrected deployment

- Address: `0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91`.
- Live identity: version `2`, owner `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`, VEST test-token ledger, supply and treasury `1,000,000,000`, schedules `0`.
- `getContractCode`: 10,896 characters, SHA-256 `1094bf5e5006c56e3e6c96c7bd547612a8102b0a99b743061e638ffc13f5229c`, exact local/deployed parity.
- Live ABI: expected 10 methods. The production frontend is bound to this replacement.
- Remaining gate: finalized owner schedule plus beneficiary evidence, recovery, consume/replay/transfer and accounting readbacks.

Production: configure the verified contract address, verify hosted frontend against that deployment, then publish reproducible evidence. No hosting or GitHub push has been performed yet.
