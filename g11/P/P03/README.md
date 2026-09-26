# P3

Status: `COMPLETE`.

P3 is included in the shared P1–P3 six-shard runs. The primary audit and
independent result audit both pass. The shared independent run covers
127,491 first-cap representatives and 708,638 residual instances across six
shards. All six exited with code 20, with zero residual SAT results. The audit
records 1,523 repeated mask encodings; they are counted as separate residual
instances. See the
[shared import status and audit details](../evidence/README.md).

- [Independent run manifest](../evidence/P123Independent/run_20260926T032326Z/run_manifest.tsv)
- [Import audit report](../evidence/P123Independent/run_20260926T032326Z/import_audit.json)
- [Portable import auditor](../evidence/Audits/audit_p123_independent_import.py)
