# Milestone upgrade: Multi-Party DAO Cancellation Quorum

## What changed

Version 3 replaces unilateral cancellation activation with a locked three-member DAO council. The deployment owner configures the council once, before any schedule exists, and selects a threshold of two or three approvals. Any council member may propose commit-pinned cancellation evidence, but the proposal remains `AWAITING_QUORUM` and does not change the active schedule revision. A distinct council member must approve it before the evidence becomes assessable by the beneficiary.

The upgrade adds:

- one-time `configure_council` with distinct-member and threshold validation;
- `record_cancellation` as a council proposal rather than immediate activation;
- replay-protected, per-member `approve_cancellation` votes;
- `get_governance` and `get_pending_decision` audit views;
- proposal nonce, approval count, proposer, status, and activated revision provenance;
- a v3 frontend workflow for council setup, proposal, and approval;
- Direct Mode coverage for unilateral activation, outsider approval, duplicate approval, and quorum activation.

## Security properties

An unapproved proposal cannot overwrite or revoke an existing active decision. Approval keys bind schedule, proposal nonce, and member address, so one member cannot vote twice. Expired proposals cannot be activated. Council membership is immutable after configuration, and configuration must happen before the first vesting schedule. Emergency revocation remains owner-controlled and can only remove authorization, never release value.

## Verification

- `python -m pytest -q` — 34 passed.
- `genvm-lint check contracts/vesting_exception_gate.py --json` — passed; 14 public methods, 5 views, 9 writes.
- `npm test -- --run` — 4 passed.
- `npm run build` — passed with Vite 7.3.6.
- v3 source SHA-256: `8999e9be0ffae6b4e9aa85dd5b40aaaa7beb9d4ce0fc73ce983c8e9f1cd1170a`.

## Deployment status

Version 3 is deployed at `0x6ABc04f05FB0e5450De3F17DDeE449A52a537022`. Live source retrieval exactly matches all 14,868 local bytes and the documented SHA-256. Council configuration, proposal non-activation before quorum, distinct-member activation, AI assessment, bounded consumption and replay protection are finalized on Studionet. See [`docs/live-e2e-v3.md`](docs/live-e2e-v3.md).
