# G11 evidence release — 26 September 2026

Public GitHub Release: [g11-evidence-20260926](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/tag/g11-evidence-20260926).

The [asset manifest](ASSET_MANIFEST.tsv) records every uploaded filename, byte count, SHA-256, and role. Q7 and Q8/Q9 are the original ZIPs uploaded unchanged. Q10's original 10,399,498,240-byte TAR is divided into six ordered assets, each smaller than 2 GB; their sizes and hashes are in [`Q10_ARCHIVE_PARTS.tsv`](../../g11/Q/evidence/Q10/source_archive_parts.tsv). The full source TAR is verified by SHA-256 `7e20e19f7428ca8a084c1a561b5ed97e69bbb9647e8098d1024a8114b4028eaa`.

To reconstruct Q10, download all six `Q10_HPC_HANDOFF_PACKAGE.tar.partNN` assets from the release into one directory and run:

```sh
cat Q10_HPC_HANDOFF_PACKAGE.tar.part00 Q10_HPC_HANDOFF_PACKAGE.tar.part01 Q10_HPC_HANDOFF_PACKAGE.tar.part02 Q10_HPC_HANDOFF_PACKAGE.tar.part03 Q10_HPC_HANDOFF_PACKAGE.tar.part04 Q10_HPC_HANDOFF_PACKAGE.tar.part05 > Q10_HPC_HANDOFF_PACKAGE.tar
shasum -a 256 Q10_HPC_HANDOFF_PACKAGE.tar
```

The command must report the whole-archive hash above. The release also includes direct archives for the 85 fresh join terminal files and audit reports, raw evidence for representatives 17/76/88, and rep53's full native chain plus the two missing source logs. Their individual hashes and sizes are in the asset manifest.

| Evidence | Release asset | SHA-256 |
|---|---|---|
| Q7 | [Q7_FINAL_VERIFICATION_PACKAGE.zip](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/download/g11-evidence-20260926/Q7_FINAL_VERIFICATION_PACKAGE.zip) | `2803882cdc532da5fec7fc141ecafdd5ed083892eb5fd84b86228034c10bff5d` |
| Q8/Q9 | [g11_q89_complete_elimination.zip](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/download/g11-evidence-20260926/g11_q89_complete_elimination.zip) | `e3035da69338b6a258b8c978ce33c398dd99e1ef8c190f1da5979b0c6832aac3` |
| Q10 original source TAR | six ordered `.partNN` assets listed in [`Q10_ARCHIVE_PARTS.tsv`](../../g11/Q/evidence/Q10/source_archive_parts.tsv) | `7e20e19f7428ca8a084c1a561b5ed97e69bbb9647e8098d1024a8114b4028eaa` after reconstruction |
| Q10 raw 85 join terminal files | `Q10_85_JOIN_TERMINAL_FILES.zip` | See asset manifest |
| Q10 raw 85 audit reports | `Q10_85_RAW_JOIN_AUDIT_REPORTS.zip` | See asset manifest |
| Q10 prior raw 17/76/88 records | `Q10_LEGACY_17_76_88_RAW_RECORDS.zip` | See asset manifest |
| Q10 rep53 complete chain | `Q10_REP53_COMPLETE_CHAIN.zip` | See asset manifest |
