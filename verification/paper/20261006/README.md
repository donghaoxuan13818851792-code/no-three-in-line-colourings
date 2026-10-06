# Fresh finite-certificate checks — 6 October 2026

All listed programs returned zero. Their original output, stderr/time and
status records are deposited here.

| Check | Fresh result | Scope |
|---|---|---|
| G9/G10/G12 matrices | PASS, determinant triples and normalized lines agree, 0 monochromatic collinear triples | valid upper-bound witnesses with exact manuscript text hashes |
| Small G11 layer | PASS: 676 caps, 89 D4 orbits, 2,138 edges, 0 triangles, 930 feasible pairs, 119 orbits, 1,309 leaves | membership/orbit/graph/profile arithmetic; no full R1 proof replay |
| Eight-grid seed/table | PASS: 2,240 determinants, 1,024 reflection memberships, 8 mixed-colour sites | exact finite absorption conditions |
| Prime data | PASS: 576 primitive directions, 65 distinct norms, complete 29-prime list; exact primality and admissibility of 185,456,518,679 | finite arithmetic; no smallest-prime or infinite-family proof claim |
| C6 displayed sum | PASS, four subtotals sum to 2,949,015,889 | displayed arithmetic only; not the full 33-row fixed-point ledger |
| Existing G9 observed catalogue | PASS: 598 valid inequivalent classes, 1,756,093 within-class triples checked, canonicalisation/stabilizers/hashes agree | observed catalogue only; not the exhaustive C(9)=743 classification |
| G10 route2 upper/lower | PASS: two six-colour witnesses; fresh DRAT check and exact independently audited CNF reconstruction | χ(G10)=6 via the deposited route2 encoding |

The G10 CNF has 500 variables, 24,740 clauses and 4,448 collinear triples.
The checker verifies the 84,066,978-byte trimmed proof with 1,815,254 lemmas
in its core. Actual elapsed time including compilation, reconstruction and
input comparison was 24.14 seconds; user+system CPU time was 22.65 seconds.
The original package and its public archive identity are in `g10_archive.json`.
The package's proof and its encoder/checker sources are in that archive.

Reproduce the manuscript finite checks from the repository:

```sh
python3 scripts/audit_paper_certificates.py --output /path/to/paper-certificates.json
python3 scripts/audit_grid9_catalogue.py --csv verification/paper/20261006/inputs/g9_observed598.csv /path/to/g9-catalogue.json
```

To replay G10, download/hash-check `g10_archive.json`'s original ZIP, extract
it, then run its unchanged `scripts/verify_upper_bound.sh` and
`scripts/verify_sat_lower_bound.sh` from that package root. The lower-bound
script compiles its checker, regenerates and audits the formula, compares the
exact certified CNF and checks the existing DRAT proof. It starts no SAT search.

The manuscript hash in `paper_certificates.json` identifies the exact text
checked. Later manuscript edits require rechecking its explicit certificates.
