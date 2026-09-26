# Q10 collaborator / HPC handoff status

## Q10 GLOBAL STATUS: INCOMPLETE

This package concerns the labelled 11x11 six-colour profile
`(22,20,20,20,20,19)`.  It does **not** prove global Q10 UNSAT and it does
not provide a Q10 colouring.  The 89 frozen D4 representatives are the outer
case universe.  Four representatives are exhausted; 85 remain unresolved.

## Certified and complete within their stated scopes

- The frozen outer input has 676 feasible oriented size-22 anchors and 89 D4
  representatives.
- The at-least-two-extendible size-20 sector is completely refuted over all 89
  representatives.  It has 88 ordinary DRAT certificates plus the complete
  representative-1 2,200-query IDRUP certificate.  Certificate bytes total
  3,690,379,185.
- Fixed representatives 17, 53, 76, and 88 have independently audited,
  complete arbitrary-cap catalogues and exact no-witness joins.  Each is
  anchor-locally UNSAT only.
- Representative 1 has a `COMPLETE_AUDITED` 3,025/3,025-shard compatible
  size-20 catalogue with 2,736,306 caps (2,517 extendible and 2,733,789
  nonextendible).  Its unordered four-cap join has **not** been completed.

## Production-ready route, not yet globally run to completion

`work/solver_agent/run_cap20_catalogue.py` is the resumable production runner.
It atomically records each of the exact 55x55 = 3,025 row/column-pair shards,
binds them to an immutable run identity, rejects corrupt/replaced output on
resume, and finalizes only after independent aggregate and shard audits pass.
`work/math_agent/nonextendible_structure/run_capset_join_shards.sh` runs the
exact 55-way join.  A fixed anchor becomes locally UNSAT only when every join
shard finishes with `COMPLETE_NO_WITNESS` and its aggregate audit passes.

## What remains

- 85 representatives, including representative 1's four-cap join, require a
  terminal arbitrary-cap catalogue/join result or a verified Q10 witness.
- A global result requires all 89 representatives to be terminally covered.
- Interrupted runs, time limits, UNKNOWN, missing shards, and partial coverage
  are always `INCOMPLETE`, never UNSAT.

See `README.md` for quick verification and `BUILD_AND_RUN_HPC.md` for Linux and
Slurm execution.  The machine-readable authoritative boundary is in
`provenance/AUTHORITATIVE_STATUS_20260803.json`.
