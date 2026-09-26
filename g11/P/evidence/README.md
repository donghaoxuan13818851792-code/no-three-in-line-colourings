# P1–P3 primary evidence import

Status: `INDEPENDENT_VERIFICATION_PENDING`.

The imported primary package contains the frozen P1–P3 source and source
dependency, six size-21 catalogues, the D4 size-22 table, the run manifest,
six primary `.out`/`.log`/`.status` records, and the six P1 baseline outputs
used by the primary audit. The captured primary audit is in
[`audits/p123_primary_results_audit_20260926.txt`](audits/p123_primary_results_audit_20260926.txt).

The existing primary audit passes: 127,491 first caps, 708,638 residual
instances, and zero residual SAT results across all six shards. Run it from
the repository root with:

```sh
cd g11/P
python3 evidence/Audits/audit_p123_shard_results.py
```

Independent verification is not complete. The independent implementation,
executable, and results auditor are included for follow-up. The auditor
expects one output and one exit-status record for each of six independent
shards. The available independent `.out` files are zero bytes, and the
required `.status` files are absent. See
[`audits/independent_verification_pending.md`](audits/independent_verification_pending.md).
No status files or terminal results were synthesized.
