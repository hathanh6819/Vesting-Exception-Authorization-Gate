# Studionet lifecycle evidence

## Verified deployment

- Contract: `0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91`
- Corrected source SHA-256: `1094bf5e5006c56e3e6c96c7bd547612a8102b0a99b743061e638ffc13f5229c`
- Live identity: version 2, owner `0xa365f55a3bf352767bc5c5739ffddaee8fcf3a19`

## Schedule creation

- Transaction: `0x01988bbc32ff741aca5aad7de324d7549bc1f8573804e08d097f7fb781a401d9`
- Receipt: success; sender is the registered owner and destination is the verified contract.
- Readback: schedule 1, beneficiary `0x1d283b45974b0be9630dfd1dec6a62a9b72b2760`, allocation 100,000, cap 2,500 bps, released 0, review `NONE`, exception unused.
- Accounting: treasury moved from 1,000,000,000 to 999,900,000; the remaining 100,000 is locked in schedule 1.

## Canonical decision fixture

- Commit: `dd5fd316b99e601bae4e8a244c99f8c4e23cea07`
- Path: `fixtures/canonical/schedule-1-cancellation.json`
- Complete raw bytes: 483
- SHA-256 recomputed after fetching raw GitHub: `dc54dcc25fd5caa0a383799edc9abbe606e580b0fe4a7397f86289f3f645358e`
- Bound identities: exact contract, schedule ID, beneficiary and decision ID.

The owner still must record this decision on-chain. Beneficiary assessment, eligible consume, replay rejection, transfer and final conservation readbacks are pending and must not be claimed as completed.
