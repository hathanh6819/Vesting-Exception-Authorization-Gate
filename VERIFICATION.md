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
- Owner schedule transaction `0x01988bbc32ff741aca5aad7de324d7549bc1f8573804e08d097f7fb781a401d9` succeeded. Schedule 1 binds the expected beneficiary/repository/policy, locks 100,000 VEST, and leaves released at zero. Fixture commit `dd5fd316b99e601bae4e8a244c99f8c4e23cea07` was fetched from raw GitHub; all 483 bytes hash to `dc54dcc25fd5caa0a383799edc9abbe606e580b0fe4a7397f86289f3f645358e`.
- The owner decision transaction `0x8b4cdb84d5e8ba0794390cf47d87abffb9391fb20d91bc594061ecf6494179c2` stored the exact commit, path, digest and decision identity as revision 1.
- The beneficiary lifecycle is complete: assessment `0x7860a2c84161592403cbb0e6fbb722a708f29d960ec4a4e7963c39ae2ba55dc9`, consume `0x5e8f311b56fcc7bc13e9bce6f35cebd0702a747a16d7547e59a6ba3b18db6470`, blocked replay `0x664095307f34578898fb9daf94093faecc1dded21da7654e142dca2806fe4d64`, and transfer `0xc61757ce7cd5c8fcdcc4dc9867a915f16581cac03a29232994cbd467f8ab6a8b` all finalized with authoritative readbacks.
- Final state: `CONSUMED`, released 25,000; beneficiary liquid 24,000; receiver liquid 1,000. Treasury 999,900,000 + remaining locked 75,000 + those liquid balances equals the fixed 1,000,000,000 supply.

Production: configure the verified contract address, verify hosted frontend against that deployment, then publish reproducible evidence. No hosting or GitHub push has been performed yet.
