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

## Recorded decision

- Transaction: `0x8b4cdb84d5e8ba0794390cf47d87abffb9391fb20d91bc594061ecf6494179c2`
- Sender: registered owner; receipt success.
- Readback: revision 1, review `PENDING`; stored commit, path, digest, decision ID and expiry exactly match the canonical fixture.

## Beneficiary lifecycle

| Scenario | Transaction | Finalized result and readback |
|---|---|---|
| Assess canonical cancellation | `0x7860a2c84161592403cbb0e6fbb722a708f29d960ec4a4e7963c39ae2ba55dc9` | `FINALIZED / MAJORITY_AGREE`; leader returned `ELIGIBLE`; three validators agreed and two were idle. Findings are all strict booleans: cancellation explicit true, policy covered true, conflicting obligations false. Evidence receipt is `2dc9ab7da2560a0499a597c07050446442d4f308a61b95c0568890b5d499736e`. |
| Consume authorization | `0x5e8f311b56fcc7bc13e9bce6f35cebd0702a747a16d7547e59a6ba3b18db6470` | `FINALIZED / MAJORITY_AGREE`, successful execution returned 25,000. Readback is `CONSUMED`, exception used true, released 25,000; beneficiary balance atomically became 25,000. |
| Replay same authorization | `0x664095307f34578898fb9daf94093faecc1dded21da7654e142dca2806fe4d64` | `FINALIZED / MAJORITY_AGREE`; leader and agreeing validators rolled back with `NOT_AUTHORIZED`. Full schedule state remained unchanged. |
| Transfer released VEST | `0xc61757ce7cd5c8fcdcc4dc9867a915f16581cac03a29232994cbd467f8ab6a8b` | `FINALIZED / MAJORITY_AGREE`, returned `TRANSFERRED`; beneficiary balance 24,000 and receiver balance 1,000. |

Final conservation readback: treasury 999,900,000 + remaining locked allocation 75,000 + beneficiary liquid 24,000 + receiver liquid 1,000 = fixed supply 1,000,000,000. The lifecycle runner prompts for a key and never persists it.

Conflict, unavailable-source recovery, invalid identity/digest, expiry, authorization and claim/exception race paths are covered by direct real-contract tests. They are not presented as separate live transactions on this consumed schedule.
