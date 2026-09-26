# Q1–Q4 final execution evidence

Status: `COMPLETE` for Q1–Q4, conditional on the exact profile reduction and
shared 89-cap catalogue documented here.

The frozen input set includes the Q1–Q4 source and its P1 source dependency,
the 89-cap D4 table, all six size-21 catalogue files, the source manifest,
and all six primary shard `.out`, `.log`, and `.status` records. The separate
independent verifier source, executable, 89 fixed-cap checks, and 670-row
residual ledger are also present. The independent audit compares every
fixed-cap result with the primary run and validates the residual masks and
line constraints.

The profile mapping and reduction are in
[`q1234_cap_packing_proof.md`](../../work/sat_agent/q1234_cap_packing_proof.md).
Aggregate results are 89 fixed caps, 670 residual instances, 10,210 residual
nodes, 5,440 conflicts, and zero satisfiable residuals.

Both existing focused auditors passed on 26 September 2026 from these
repository files. The checks inspect frozen execution records; they do not
rerun the production search.

From the repository root, run:

```sh
cd g11/Q
python3 evidence/Audits/audit_q1234_shard_results.py
python3 evidence/Audits/audit_q1234_independent_results.py
```

The captured outputs are in [`audits/`](../audits/). The hashes for every file
in the repository working tree are listed in `manifests/SHA256SUMS` at the
repository root.
