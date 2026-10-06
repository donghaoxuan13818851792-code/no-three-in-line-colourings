# Material-dependent local checks — 6 October 2026

Further work can run on our Mac or 9800X3D once matching frozen material is
available. This checklist does not claim the authors possess every missing
final result. No new large search has started and no request has been sent.

## Prioritized requests

| Priority / claim | Material to identify or request | Local work after receipt | Boundary |
|---|---|---|---|
| 1 — G11 R1 | `grid11_six_colour_two_size22_proofs_0.1.0.tar.zst`, 45,687,997,349 bytes, SHA-256 `0087af20d68402c18728e56bc209e508b5565e9522c0b4185afaf2faf43f994f`; all 1,309 matching CNF/leaf IDs, solver reports, expected uncompressed proof hashes and final ledger from its certificate package | reconstruct the 119-pair × 11-profile mapping, check formulas, DRAT → LRAT conversion and independent LRAT checking for every leaf | Metadata reports all 1,309 finished; proof bodies have not been replayed here. The driver and leaf auditor are already in Git. |
| 2 — C5/C7/C9 classifications | complete final representative lists (claimed 62 / 1,726 / 743), exact D4 × colour-relabel convention, frozen generator/canonicalizer, full run/coverage ledger and checksums | validity, canonicalisation, duplicates, stabilizers/orbits, counts and run coverage; then plan any independent enumeration | The checked G9 list contains 598 observed classes. More valid representatives alone do not establish exhaustive C(9)=743. |
| 2 — C6 count | all 33 profile rows, identity/nonidentity fixed-point contributions, equal-size colour-permutation action, source/input hashes and complete exact counting records | recompute Burnside arithmetic/group actions, inspect coverage and bind counts to original records | Lightweight ledger checks do not independently enumerate the roughly 2.949 billion claimed classes. A fresh full count needs a separate cost estimate. |
| 2 — C8 classification | complete 380 oriented full-arc input, all four unordered covers, symmetry expansion/canonicalisation source and coverage records | validate arcs, covers, uniqueness and the claimed two equivalence classes; inspect input completeness | The checked explicit seed does not prove the full classification. |
| 3 — G12 lower bound | exact full-arc input, symmetry expansion, all 26 corner cases, complete case mapping and terminal proof/trace objects or exact verifiable exhaustive records | reconstruct cases and check each exclusion with its frozen verifier | The seven-colour witness passes; six-colour exclusion has not been mapped to matching frozen material. |
| 3 — n=14,16,18,20 packing bounds | exact full-arc catalogues/expansion, complete instance ledger, terminal certificates or exact verification records, generator and verifier source | input/orbit coverage, packing-instance reconstruction and existing-evidence replay | Source or “no packing found” alone does not establish complete exclusion. |
| 4 — smallest admissible prime | complete CRT/candidate-search coverage below 185,456,518,679, all residue constraints, exact search source and logs | reconstruct the candidate universe and certify that no smaller admissible candidate was missed | Primality and admissibility of the displayed example pass; minimality remains separate. |
| Confirm first — global P4/P5, P6, P7 | whether a complete global run exists; if yes, the entire canonical work-item map, frozen inputs or reproducible enumeration, all shard outcomes including retries/UNKNOWN, exact source and terminal proofs where available | coverage audit, formula/input reconstruction and existing-result verification, calibrated before full replay | Received P4/P5 says unresolved; P6 covers one fixed-A branch; P7 has partial takeover evidence. If no complete result exists, extra logs will not close it. A new global search is a separate campaign. |

For each package request an immutable URL/version, byte size, SHA-256,
schema/readme, original source revision, exact command/build settings and
verifier source. Retain original failures and retries, not only a final table.

First map existing received archives to each claim: `NOT_YET_MAPPED` in
`PAPER_CLAIMS.md` does not mean absent from every older package. Request the
specific missing object after that check.

## Storage and cost calibration

R1 is the clearest next proof replay, but its compressed body alone is 45.7 GB.
The Mac has about 10 GiB free and cannot retain the entire archive. Use an
external disk or individually hash-addressed proof files checked in batches.
Decompressed proofs and temporary LRAT add further space. Measure small,
median and large proofs before choosing workers or declaring storage sufficient.

Compressed size does not determine CPU hours. Calibrate decompression, native
checking and temporary peak space, then give measured CPU-hour and Mac
wall-time estimates. Small list/ledger audits should precede expensive complete
enumerations. The previous 3.128-hour campaign does not estimate all these tasks.

## Q10 does not need the catalogue package again

The complete 89-representative catalogue/primary join archive, existing-sector
proof bodies and formulas are already available. Global Q10 still needs
independent enumeration/join correctness beyond that sector. We can work on
the independent checker and coverage argument from existing material.

Ask for a refreshed supplied manifest/final status, exact source/build/submission
provenance and comprehensive run accounting. If a separate proof covers
arbitrary-cap global Q10, request its formula, proof and case mapping. Such
coverage is not established by the current sector receipts. Provenance and a
refreshed manifest alone do not prove independently verified global UNSAT.

The infinite-family construction and theoretical reductions need human
mathematical review; finite checks do not replace those proofs.
