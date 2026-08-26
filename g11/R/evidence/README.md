# R evidence

This directory contains compact reviewer-facing evidence records for the R branch.

- `caps22_audit.txt` — frozen audit summary for the 676-cap catalogue and disjointness graph.
- `profile_ledger_audit.txt` — frozen deficit-profile coverage summary, including `44 = 16 + 11 + 10 + 7`.
- `pair_orbit_audit.txt` — frozen pair/orbit audit summary.
- `final_ledger_summary.json` — compact summary of the recorded 1,309/1,309 terminal verification ledger.
- `independent_replay_20260826.txt` — fresh re-execution/reconstruction using exact frozen source; despite the historical filename, this is not an independently implemented checker.
- `catalogue_reconstruction_20260826_m4.txt` — fresh exhaustive size-22 catalogue reconstruction from the frozen generator: 534,934,909 search nodes, 1,120 oriented solutions, 676 long-diagonal-feasible caps, 89 D4 representatives, and byte-for-byte reproduction of both frozen catalogue files; also reconfirms 2,138 disjoint pairs, zero triangles, 930 capacity-feasible pairs and 119 pair orbits.

The large proof bodies are not stored here. See `../ARTIFACTS.md` and repository Issue #1 for the remaining public-archive and full-replay gate.
