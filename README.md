# Vesting Exception Authorization Gate

A focused Studionet prototype for early vesting release after an authenticated DAO milestone cancellation. The supplied logo is used unchanged. The UI is a new treasury workspace, not a clone of the previous dApps.

## Scope

VEST is an internal, transferable test-token ledger with a fixed 1,000,000,000-unit supply. It is not an external ERC-20 and accepts no GEN deposits. The deploying wallet is the decision authority, not a verified DAO voting adapter. Beneficiaries must be separate wallets. Review eligibility alone does not move tokens: `consume_exception` verifies the current revision and expiry, marks the exception consumed, and releases the capped allocation in one contract write.

Early release accelerates the schedule only up to a cap measured against the original allocation. Amounts already claimed count against that cap, and released amounts count against later linear vesting, so racing the two paths cannot double-pay. Ordinary vested claims remain available even if evidence review fails.

## Local verification

Requires Python 3.12 with gltest/GenVM dependencies and Node 22+.

```powershell
python -m pytest
$env:PYTHONIOENCODING='utf-8'
genvm-lint contracts/vesting_exception_gate.py
cd frontend
npm ci
npm test
npm run build
npm run dev
```

Direct tests call the real Python contract; only external HTTP/model boundaries are mocked. No fake data or fallback balances exist in the runtime frontend. Test receipts do not constitute live network evidence.

## Deployment workflow — pending live verification

Superseded Studionet deployment: `0x003383481158c03C9b3B820af829172e994aB944`. Its source matched version 1, but a real `create_schedule` exposed that GenVM delivered the ABI address as a string while the address formatter assumed `.as_hex`. State remained fresh (`schedule_count = 0`, full treasury). Version 2 normalizes both runtime forms and adds direct regression coverage. The production address was cleared until the corrected source was redeployed.

Verified replacement deployment: `0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91`. Live `get_info`, ABI and complete deployed-source SHA-256 match the corrected local source. The production frontend is configured for this address. A finalized authority-to-beneficiary lifecycle proves canonical assessment, exact capped release, replay rejection, transfer and supply conservation; see `docs/live-evidence.md`.

1. Deploy `contracts/vesting_exception_gate.py` on Studionet using the DAO authority wallet; constructor has no arguments. Archive exact source and its SHA-256.
2. Enter the returned address in the UI; read contract identity, connect authority, and create a schedule for a separate beneficiary with a future start/end.
3. Publish an authority-authored UTF-8 JSON decision in the schedule's GitHub repository. Required exact fields: `contract`, `schedule_id` (integer), `beneficiary`, `decision_id`, `statement`. Addresses must be lowercase. Include explicit milestone cancellation terms and any remaining obligations. This is an authority attestation, not independent proof of a DAO vote.
4. Lock a full Git commit, path and SHA-256 of complete raw bytes via `record_cancellation`. Expiry must be in the next seven days. Contract fetches the fixed-commit raw source, verifies all bytes and identity, and fails closed above 16,000 bytes.
5. Beneficiary assesses, inspects findings, consumes once, reads balance and transfers released VEST. Record finalized execution, before/after schedule and balances, then prove replay/outsider/stale/expired calls cannot release more tokens.
6. Run a conflict decision and an unavailable-evidence retry, as well as normal vesting after early release. Validate the actual frontend wallet/context flows. Only then publish evidence and configure `VITE_CONTRACT_ADDRESS` for production.

Not yet submission-ready: deployed-source parity, live positive/negative transactions, browser interaction tests and production deployment remain verification gates. See BUILD_PLAN.md for invariants and scope.
