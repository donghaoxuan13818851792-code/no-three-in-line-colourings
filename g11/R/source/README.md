# R audit source

This directory contains exact source files imported from the frozen `grid11_six_colour_two_size22_certificate_0.1.1` package. They are kept here so that reviewer-facing coverage claims do not depend only on prose summaries or recorded counts.

## Imported exact source

| Repository path | Original package path | SHA-256 |
|---|---|---|
| `caps/audit_disjoint_caps.py` | `caps/source/audit_disjoint_caps.py` | `3364c0cd6db3010608cc1ff0c7e063f89185f7dd99b2419c05c82f1839303a9e` |
| `symmetry/canonical_cap_pairs.py` | `symmetry/source/canonical_cap_pairs.py` | `2b5095c8221cbca15f48094ca469cad9c015be5a5885a06131e6166e16177f47` |
| `coverage/audit_coverage.py` | `scripts/audit_coverage.py` | `7930707d894c312e519b8c530b21f54be3887cece5e6b3e16164d4136a1b457b` |
| `verification/audit_twomax_leaf_batch.py` | `verification/source/audit_twomax_leaf_batch.py` | `d5a6832355b67701e68e65ce7b62eb8c117d50b948ac6aeb7296e1a8027f423a` |
| `verification/verify_twomax_proofs_parallel.py` | `verification/source/verify_twomax_proofs_parallel.py` | `54b2220be65156d2c991b5dda128193be658a84fafb06ade86f9ada83b1a8266` |
| `verification/verify_metadata.py` | `scripts/verify_metadata.py` | `85064205d05f5fcde9184a6c077c6403142f089e6e50335ac758e0a1988c6fbf` |

The imported files above are intentionally preserved with their original logic. Repository-authored documentation may explain them, but should not silently modify the historical audit code and still describe it as the frozen source.

## What the source checks

- `audit_disjoint_caps.py` checks the 676-cap input, validates each cap geometrically, constructs the 2,138-edge disjointness graph, and verifies that the graph has no triangles.
- `canonical_cap_pairs.py` independently constructs disjoint pairs, optionally applies the four-colour complement line-capacity condition, requires exactly 930 retained pairs, and canonicalises under `D4` plus interchange of the two caps.
- `audit_coverage.py` and `audit_twomax_leaf_batch.py` reconstruct the 628 relevant maximal lines, the 2,138 disjoint pairs, the 930 capacity-feasible pairs, the 119 canonical pair orbits, the 11 exactly-two-zero profiles, and the 1,309 expected leaf names. With the full external leaf package present, they also check exact CNF construction and solver-report metadata.
- `verify_twomax_proofs_parallel.py` first requires the exhaustive leaf preflight, then checks each proof through `drat-trim`, emits a temporary LRAT, validates that LRAT with `lrat-check`, records hashes/logs atomically, and requires all 1,309 leaves to verify.
- `verify_metadata.py` cross-checks the complete 1,309-leaf CNF/report/verification-log/ledger metadata in the original package layout.

The checker binaries/source used by the proof driver and the full proof bodies remain part of the frozen external package/proof archive. Full public replay therefore still depends on the archival gate recorded in `../ARTIFACTS.md`.
