# Reproducing the R-branch audits

The commands below describe the intended reviewer-facing checks from a clone of this repository. Run them from `g11/R` unless otherwise stated.

Small frozen inputs are committed under `data/`. Exact imported source hashes are recorded in `source/README.md` and the repository-wide artifact manifest.

## 0. Reconstruct the exhaustive size-22 catalogue

This is the catalogue-completeness step. It distinguishes

> the supplied 676 caps are all valid

from the stronger statement

> exhaustive generation produces exactly these 676 diagonal-feasible size-22 caps.

Run:

```bash
python3 source/generator/rebuild_size22_catalogue.py
```

The wrapper compiles the frozen `source/generator/enumerate_caps.cpp`, runs the exhaustive size-22 generator, and requires its summary to contain:

```text
oriented_solutions 1120
meets_long_diagonals 676
```

It then requires:

```text
676 generated caps == data/caps22_diag_independent.hex byte-for-byte
89 D4 representatives == data/caps22_d4.hex byte-for-byte
```

The final success line begins:

```text
CATALOGUE_RECONSTRUCTION_PASS caps=676 ... d4_orbits=89 ... caps_byte_identical=yes d4_byte_identical=yes
```

A fresh exhaustive replay was completed on 26 August 2026 from repository commit `8e35fc930de2d5ecb447759770415e283803a22d`. On Apple M4 / macOS 27 with clang 17 and Python 3.14.7, the generator traversed 534,934,909 search nodes in approximately 30 seconds, reproduced 1,120 oriented solutions and 676 long-diagonal-feasible caps, and reproduced both the 676-cap catalogue and 89-orbit `D4` catalogue byte-for-byte. The evidence log is:

```text
evidence/catalogue_reconstruction_20260826_m4.txt
```

Thus the fresh catalogue-completeness replay is recorded **PASS**.

## 1. R0: validate the 676 caps and triangle-free disjointness graph

Run:

```bash
python3 source/caps/audit_disjoint_caps.py data/caps22_diag_independent.hex
```

Expected output:

```text
vertices 676 edges 2138 triangles 0
```

This validates every supplied cap geometrically and establishes the finite graph statement used to exclude three or more size-22 colour classes.

For the 89-orbit count alone, independently of the wrapper output, run:

```bash
python3 source/caps/canonicalize_caps.py data/caps22_diag_independent.hex | cmp - data/caps22_d4.hex
```

A zero exit status means the canonicalized output is byte-identical to the frozen 89-line table.

## 2. R1: complement-capacity filter and pair orbits

Run:

```bash
python3 source/symmetry/canonical_cap_pairs.py \
  data/caps22_diag_independent.hex \
  /tmp/generated_pairs.hex \
  --complement-capacity
```

Expected output:

```text
caps=676 retained_pairs=930 d4_swap_orbits=119
```

Then require byte identity with the frozen production table:

```bash
cmp /tmp/generated_pairs.hex data/cap_pairs22_capacity_d4_swap.hex
shasum -a 256 /tmp/generated_pairs.hex
```

Expected SHA-256:

```text
5f6b9033e3eef7b0505be70b6e2eb98cc879984f2456ab0836567014a87f9c3c
```

The separate frozen table `data/pairs22_filtered_ordered_d4.hex` is checked by the full coverage auditor to represent the same canonical orbit universe.

## 3. Full R1 coverage / CNF construction

When the frozen profile CNFs, leaf CNFs and solver reports are available, use the exact imported coverage auditor:

```bash
python3 source/coverage/audit_coverage.py \
  --profiles /path/to/profiles22 \
  --pairs data/cap_pairs22_capacity_d4_swap.hex \
  --alternative-pairs data/pairs22_filtered_ordered_d4.hex \
  --all-caps data/caps22_diag_independent.hex \
  --leaves /path/to/twomax_leaf_proofs \
  --reports /path/to/solver_reports \
  --require-all \
  --defer-proof-content
```

The coverage audit reconstructs:

```text
caps=676
disjoint_edges=2138
admissible_edges=930
pair_orbits=119
profiles=11
expected_leaves=1309
```

and checks that each leaf CNF is exactly the relevant profile base CNF plus the 44 unit clauses fixing the two selected size-22 classes.

## 4. Proof replay

The exact frozen proof driver is stored as:

```text
source/verification/verify_twomax_proofs_parallel.py
```

It first invokes an exhaustive leaf preflight and then checks every UNSAT proof in two stages:

```text
CNF + DRAT --drat-trim--> temporary LRAT --lrat-check--> VERIFIED
```

For each leaf it records the CNF/proof/checker/log hashes and requires both checker exit codes to be zero. The aggregate schema is:

```text
grid11-twomax-drat-lrat-parallel-v1
```

A complete successful replay requires all 1,309 leaves to verify and the aggregate report to have `verified=true`.

## Independence note

`evidence/independent_replay_20260826.txt` records a fresh re-execution/reconstruction using exact frozen source. It is **not** a separately implemented verifier. A structurally independent implementation remains a distinct final evidence item.

## Current archival gate

The public repository now contains the small frozen R inputs, the exhaustive cap generator, a completed fresh catalogue-completeness replay, canonicalizers, audit source, compact audit outputs, final-ledger summary, package/proof hashes, and the fresh reconstruction logs.

The 45.7 GB proof-body archive and the large certificate packages still require stable public immutable archival locations, and the full proof replay has not yet been made publicly reproducible from those locations. A structurally independent implementation of the small catalogue/pair/orbit checks also remains outstanding.

Therefore these instructions do **not** yet justify changing R from `AWAITING_ARTIFACT_IMPORT` to `COMPLETE`.
