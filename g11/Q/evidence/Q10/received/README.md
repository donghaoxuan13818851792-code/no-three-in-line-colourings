# Q10 HPC collaborator handoff

This is a frozen, portable handoff for the 11x11 no-three-collinear six-colour
profile `(22,20,20,20,20,19)`.  Its sole global conclusion is:

> **Q10 GLOBAL STATUS: INCOMPLETE.**

It provides an audited production route that a collaborator or HPC cluster can
resume.  It also preserves the complete proof-certified at-least-two-extendible
sector, four anchor-local UNSAT results (17, 53, 76, 88), and representative
1's complete catalogue.  None of those facts proves global Q10 UNSAT.

## Start here

Run the fast, non-searching verification from this directory:

```sh
python3 verify_handoff.py
```

It rehashes this handoff, checks all 89 frozen representatives, reruns the
saved proof-bundle and fixed-anchor audits, and rescans rep1's 3,025-shard
catalogue.  It does not invoke the enumerator, join, SAT solver, DRAT checker,
or IDRUP checker.

For full proof replays and Linux/HPC continuation, read
`BUILD_AND_RUN_HPC.md`.  The desktop verification record is
`HANDOFF_VERIFICATION.md`.

## Package layout

- `work/package/` — frozen 676-anchor and 89-representative authoritative data.
- `work/solver_agent/` — C++ enumerator/auditor source, resumable 3,025-shard
  runner, and preserved output for representatives 1, 17, 53, 76, and 88.
- `work/math_agent/nonextendible_structure/` — exact 55-way join source,
  runner, independent join/fixed-anchor auditors, and terminal ledgers.
- `work/package_agent/pair_proofs/` — 88 DRAT proofs, representative-1 IDRUP,
  checker source/binaries, proof logs, manifests and binding auditor.
- `work/root/pair_selectors/` — frozen source CNFs/INCCNF for the proof sector.
- `slurm/` and `tools/` — Linux build and conservative single-node Slurm entry
  points.  The 3,025-shard runner uses resumable records and can be rerun after
  a batch allocation ends.
- `archives/cloud_upload_parts/` — original split core/proof archives, exact
  SHA-256 metadata, and reassembly script.  They are provenance delivery
  archives; the active handoff is the top-level curated tree.
- `quarantined/` — explicitly invalid/superseded historical rep76 reuse75
  audit material.  It is excluded from every authoritative verifier.
- `provenance/` — frozen cloud handoff context, status, environment, and
  original archive-input descriptions.

## Deliberate claim boundary

The proof sector rules out only colourings with at least two extendible
size-20 classes.  The arbitrary-cap production route is required for the
remaining sector.  The four exhausted anchors are not an outer-universe
exhaustion.  Do not cite this package as a solution of the 11x11 six-colour
problem or as global Q10 UNSAT.
