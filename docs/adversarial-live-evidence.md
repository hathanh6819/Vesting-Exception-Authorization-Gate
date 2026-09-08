# Studionet adversarial audit evidence

## Scope and immutable inputs

- Contract: `0x18Dbe884Bf6403CceC4b8fFa254dbE9bA0421d91`
- Isolated schedule: 2; beneficiary `0x1d283b45974b0be9630dfd1dec6a62a9b72b2760`; allocation 100,000 VEST; exception cap 2,500 bps.
- Fixture commit: `aaa490637743723cee4cbb4e3abb95d6d348d3c2`.
- Conflict fixture: `fixtures/adversarial/schedule-2-conflict.json`, 478 raw bytes, SHA-256 `71975755b0f983527a9acc99b785f0106d9e8de01b8f663846fa44e2143e91cc`.
- Clear fixture: `fixtures/adversarial/schedule-2-clear.json`, 448 raw bytes, SHA-256 `7398b0d81dfb322201788a098ad36d9e1edbd5883c2c1b08653c73c8d7f04adb`.
- Schedule creation: `0x6364647eb10eb5e26ee939f3bcc9a62d76348fa0d50ff6a0f22f5d563c48aec2`; treasury decreased exactly once to 999,800,000.

## Authority and beneficiary boundaries

| Scenario | Transaction | Finalized result |
|---|---|---|
| Outsider records a decision | `0xae66647864d82378d98d0f6bc7c7b7f9e80233e510eb1495afc7fed69f7a629c` | Rollback `ONLY_DAO`; state unchanged. |
| Outsider assesses evidence | `0x3fc68b9a7a082de5f77e97d5f4f9bdd6e05cabcdf5286f057186b354d23cea80` | Rollback `ONLY_BENEFICIARY`; state unchanged. |
| Owner records conflict revision 1 | `0xfe2a75a8e8e7f580f842f43760ea7575fe40e2c9496c6500df91cb7d6aede24c` | Exact commit, path and digest stored as `PENDING`. |
| Beneficiary assesses conflict | `0x95198d5096c9cfe94de6c08f4fa950d96c2ac0162e7f63517753fa9783eb1806` | `CONFLICT`; canonical digest returned; `conflicting_obligations=true`; release remains zero. |
| Consume conflict result | `0x9c405d878f0c9ac5bfaaee17c2079d34cc8618737e3c4cfed22d099f7be27e25` | Rollback `NOT_AUTHORIZED`; state and balance unchanged. |

## Expiry, stale revision and digest binding

| Scenario | Transaction | Finalized result |
|---|---|---|
| Owner records short-lived wrong digest revision 2 | `0x014a886d33ba6444125442f3139278dc355b37bc1c457343197334738af569e1` | Wrong digest stored without granting authorization. |
| Assess stale revision 1 | `0x85a5e7ff983e163e0740b09b60ce2eb36526a3186868ea8d74f4fb62eff51647` | Rollback `STALE_REVISION`; state unchanged. |
| Assess expired revision 2 | `0xeb9f04957c9ed896605c97a76f8f362d4238c9e7b84c7a291735ab6f0a8a4ffe` | Rollback `EXPIRED`; state unchanged. |
| Owner records active wrong digest revision 3 | `0x2183bd2c46f216c642d2ad2ed5c7ec8704c2519ce4cd2ca389953481f4a546c2` | Clear fixture identity stored with intentionally false digest. |
| Assess stale revision 2 | `0x1f4f5265792f04ff4cb8b710dbccce58f5c5ae454d1f8a67e78eac7b5daea7ce` | Rollback `STALE_REVISION`; state unchanged. |
| Assess wrong digest revision 3 | `0xa939151f7b011a01c19fd72a8e906933e2d25cb172d4dde29bbcf6569ccc2c9d` | Validators fetched the full raw file, recomputed SHA-256 and returned `UNRESOLVED / DIGEST_MISMATCH`; release and balance unchanged. |
| Retry the same wrong revision | `0x211ac1f57f4fbb609665c8b736b89a26cc05d33dd41991995862f858ae42d952` | Again `UNRESOLVED / DIGEST_MISMATCH`; deterministic state unchanged. |
| Consume unresolved result | `0x4d0c30cec908ac81d2f91a23f8d3cd20547b68fbaf0e3ae8e98f7e572d5fe97b` | Rollback `NOT_AUTHORIZED`; accounting unchanged. |

## Corrected-source recovery and single use

| Scenario | Transaction | Finalized result |
|---|---|---|
| Owner records exact clear digest revision 4 | `0x0be3848dfdab245ddee7025e5973f6974d6632da65cd04cd0904a611d7ab1af6` | Exact fixed commit, path, decision identity, digest and fresh expiry stored. |
| Beneficiary assesses corrected evidence | `0x6fc8c406a506a92147dd73b63fac2596a1d82caf253cabe96fb1b162f7694f7d` | `FINALIZED / MAJORITY_AGREE`, `ELIGIBLE`; findings are cancellation explicit true, policy covered true and conflicting obligations false; no release during assessment. |
| Consume once | `0xcfcf4861ba23a3edf3d0083a39a6abab4b84a5d22acc09e31fdf35feaca487cd` | Successful execution returned exactly 25,000; schedule became `CONSUMED`; beneficiary balance increased atomically from 24,000 to 49,000. |
| Replay revision 4 | `0xd4125ebf17e9fb61a31c9a838f38e18f6064144d36d5ae485ef19b666d921d79` | Rollback `NOT_AUTHORIZED`; full schedule and beneficiary balance unchanged. |

Final readback conserves the fixed supply: treasury 999,800,000 + schedule 1 remaining 75,000 + schedule 2 remaining 75,000 + beneficiary liquid 49,000 + receiver liquid 1,000 = 1,000,000,000 VEST.

The live runners prompt for test keys through a hidden terminal input. No private key, keystore or fallback account is stored in the repository.
