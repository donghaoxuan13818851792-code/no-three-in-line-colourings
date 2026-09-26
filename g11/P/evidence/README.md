# P1–P3 evidence

Status: `COMPLETE`.

The primary six-shard result is audited in [`audits/p123_primary_results_audit_20260926.txt`](audits/p123_primary_results_audit_20260926.txt). The fresh independent six-shard run is in [`P123Independent/run_20260926T032326Z/`](P123Independent/run_20260926T032326Z/), with each shard's output, log, exit status, residual stream, timestamps, and command string. [`run_manifest.tsv`](P123Independent/run_20260926T032326Z/run_manifest.tsv) records their SHA-256 values; [`source_inputs.tsv`](P123Independent/run_20260926T032326Z/source_inputs.tsv) records the frozen verifier and catalogue inputs.

Run the import audit from the repository root:

```sh
python3 g11/P/evidence/Audits/audit_p123_independent_import.py
```

The audit runs the existing independent result checker in a temporary path-compatible mirror, checks the output statistics against the primary run, and verifies the frozen input and output hashes. It passes with 127,491 first caps, 708,638 residual instances, and zero residual SAT results. Of those instances, 707,115 distinct mask encodings appear; the remaining 1,523 occurrences repeat across different instances. The count is by residual instance, not by globally unique mask string.

The recorded independent run used the frozen verifier and inputs; it did not rerun the primary production search. See [`independent_verification_20260926.md`](Audits/independent_verification_20260926.md). The earlier pending-state note remains at [`independent_verification_pending.md`](audits/independent_verification_pending.md) with a superseded-status note.
