# Q10 final audit

Status: `COMPLETE` for all 89 fixed size-22 representatives.

## Result

Eighty-five representatives have fresh raw 55-shard terminal audits. Representatives 17, 76, and 88 have prior raw 55-shard audits whose terminal records and catalogue metadata were rechecked. Representative 53 uses its native complete 3,025-shard catalogue result and its complete exact terminal join log. All 89 representatives have a complete catalogue record and a no-witness join result.

For every 55-shard join audit, all 55 rows have exit code 20 and `COMPLETE_NO_WITNESS`, no witness hash, and zero final pool candidates. The rep53 native chain independently confirms all 3,025 enumeration shards completed with exit zero; its join log reports `COMPLETE_NO_WITNESS` and zero final candidates.

The 85 fresh `join-summary.tsv` rows account for 74,011,954 candidate masks examined by those 85 join runs. The sum of the catalogue sizes across all 89 representatives is a different measure: 75,666,410 masks. The per-representative values and catalogue hashes are in [`audits/final_audit.tsv`](audits/final_audit.tsv); the imported audit result is [`audits/final_audit_summary.json`](audits/final_audit_summary.json).

## Source and audit records

- The selected 814-member source-record import is listed in [`source_members.tsv`](source_members.tsv). The import audit checks every listed file's size and SHA-256 against the extracted record.
- The original `Q10_HPC_HANDOFF_PACKAGE.tar` is 10,399,498,240 bytes with SHA-256 `7e20e19f7428ca8a084c1a561b5ed97e69bbb9647e8098d1024a8114b4028eaa`. It is preserved as six sequential public release assets; see [`source_archive_parts.tsv`](source_archive_parts.tsv) and the [release reconstruction notes](../../../../releases/g11-evidence-20260926/README.md).
- The release includes a direct ZIP of the 14,025 raw `.out`, `.time`, and `.exit` files for the 85 fresh representatives, plus a ZIP of the 85 raw per-representative audits and their selected-input manifest.
- The prior raw 17/76/88 audit records are preserved in this repository and in a direct release archive. Rep53's full catalogue-shard chain, catalogue, terminal result and audit records are in a separate release archive. Its two exact supplemental source logs are copied byte-for-byte under [`rep53_supplement/`](rep53_supplement/) and listed in [`rep53_supplement/supplement_manifest.tsv`](rep53_supplement/supplement_manifest.tsv).
- The earlier `runs/join-status.tsv` is preserved unchanged with 85 `MISSING` rows. It predates the later passing `runs/join-summary.tsv` and raw terminal audit records; those later records supersede it.

## Recheck

Run from the repository root:

```sh
python3 g11/Q/evidence/Audits/audit_q10_import.py
```

The portable import audit checks source-selection hashes, all 85 fresh reports, the three prior raw reports, catalogue result metadata, rep53 source and rerun equality, its supplemental-file hashes, and full representative coverage. It prints `Q10_FINAL_AUDIT PASS audited=89/89`.
