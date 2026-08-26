# R audit source

This directory contains exact source files imported from the frozen `grid11_six_colour_two_size22_certificate_0.1.1` package, together with a very small number of clearly labelled repository-authored wrappers. The frozen files are kept here so that reviewer-facing coverage claims do not depend only on prose summaries or recorded counts.

## Imported exact source

| Repository path | Original package path | SHA-256 |
|---|---|---|
| `generator/enumerate_caps.cpp` | `caps/source/enumerate_caps.cpp` | `c47a5a4488a6963be51defdfbe135b9637442ee26b798188be84279fed48a824` |
| `caps/audit_disjoint_caps.py` | `caps/source/audit_disjoint_caps.py` | `3364c0cd6db3010608cc1ff0c7e063f89185f7dd99b2419c05c82f1839303a9e` |
| `caps/canonicalize_caps.py` | `caps/source/canonicalize_caps.py` | `d67cd40f91a907bac8519d300f50f68a85bcd36c525dd3dbaeb92dab415dedcf` |
| `symmetry/canonical_cap_pairs.py` | `symmetry/source/canonical_cap_pairs.py` | `2b5095c8221cbca15f48094ca469cad9c015be5a5885a06131e6166e16177f47` |
| `coverage/audit_coverage.py` | `scripts/audit_coverage.py` | `7930707d894c312e519b8c530b21f54be3887cece5e6b3e16164d4136a1b457b` |
| `verification/audit_twomax_leaf_batch.py` | `verification/source/audit_twomax_leaf_batch.py` | `d5a6832355b67701e68e65ce7b62eb8c117d50b948ac6aeb7296e1a8027f423a` |
| `verification/verify_twomax_proofs_parallel.py` | `verification/source/verify_twomax_proofs_parallel.py` | `54b2220be65156d2c991b5dda128193be658a84fafb06ade86f9ada83b1a8266` |
| `verification/verify_metadata.py` | `scripts/verify_metadata.py` | `85064205d05f5fcde9184a6c077c6403142f089e6e50335ac758e0a1988c6fbf` |

The imported files above are intentionally preserved with their original logic. Repository-authored documentation may explain them, but should not silently modify the historical audit code and still describe it as frozen source.

## Repository-authored wrapper

`generator/rebuild_size22_catalogue.py` is not historical frozen source. It is a reviewer-facing wrapper that gives the imported generator and canonicalizer stable repository-relative paths. It compiles `enumerate_caps.cpp`, requires the exhaustive summary to contain

```text
oriented_solutions 1120
meets_long_diagonals 676
```

requires the generated 676-line catalogue to be byte-identical to `../data/caps22_diag_independent.hex`, then canonicalizes it under `D4` and requires the generated 89-line output to be byte-identical to `../data/caps22_d4.hex`.

This wrapper exists specifically to close the distinction between auditing a supplied 676-cap file and reconstructing the exhaustive catalogue that produced it.

## What the source checks

- `enumerate_caps.cpp` exhaustively enumerates the relevant row-by-row size-22 no-three-in-line solutions; in emit mode it records the full oriented count and emits precisely the solutions meeting both long diagonals.
- `canonicalize_caps.py` quotients a cap list under the eight square symmetries and produces the 89 frozen `D4` representatives.
- `audit_disjoint_caps.py` checks the 676-cap input, validates each cap geometrically, constructs the 2,138-edge disjointness graph, and verifies that the graph has no triangles. Its historical `--full` mode refers to the original package layout; reviewers should use `generator/rebuild_size22_catalogue.py` for the repository-relative completeness replay.
- `canonical_cap_pairs.py` constructs disjoint pairs, optionally applies the four-colour complement line-capacity condition, requires exactly 930 retained pairs, and canonicalises under `D4` plus interchange of the two caps.
- `audit_coverage.py` and `audit_twomax_leaf_batch.py` reconstruct the 628 relevant maximal lines, the 2,138 disjoint pairs, the 930 capacity-feasible pairs, the 119 canonical pair orbits, the 11 exactly-two-zero profiles, and the 1,309 expected leaf names. With the full external leaf package present, they also check exact CNF construction and solver-report metadata.
- `verify_twomax_proofs_parallel.py` first requires the exhaustive leaf preflight, then checks each proof through `drat-trim`, emits a temporary LRAT, validates that LRAT with `lrat-check`, records hashes/logs atomically, and requires all 1,309 leaves to verify.
- `verify_metadata.py` cross-checks the complete 1,309-leaf CNF/report/verification-log/ledger metadata in the original package layout.

## Independence terminology

The fresh 2026-08-26 reconstruction log re-executes exact frozen source in a separate working session. That is useful evidence, but it is **not** an independently implemented checker. A structurally separate reimplementation remains a distinct evidence item for the final independent-verification layer.

The checker binaries/source used by the proof driver and the full proof bodies remain part of the frozen external package/proof archive. Full public replay therefore still depends on the archival gate recorded in `../ARTIFACTS.md`.
