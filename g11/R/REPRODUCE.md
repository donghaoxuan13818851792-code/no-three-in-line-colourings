# Reproducing the R-branch audits

The commands below describe the intended reviewer-facing checks. Small-source hashes are recorded in `source/README.md` and the repository-wide artifact manifest.

## 1. R0: size-22 catalogue and triangle-free compatibility graph

With the frozen 676-cap file available as `caps22_diag_independent.hex`:

```bash
python3 source/caps/audit_disjoint_caps.py caps22_diag_independent.hex
```

Expected output:

```text
vertices 676 edges 2138 triangles 0
```

This establishes the finite graph statement used to exclude three or more size-22 colour classes.

## 2. R1: complement-capacity filter and pair orbits

Run:

```bash
python3 source/symmetry/canonical_cap_pairs.py \
  caps22_diag_independent.hex \
  generated_pairs.hex \
  --complement-capacity
```

Expected output:

```text
caps=676 retained_pairs=930 d4_swap_orbits=119
```

The generated pair table should have SHA-256

```text
5f6b9033e3eef7b0505be70b6e2eb98cc879984f2456ab0836567014a87f9c3c
```

and should be byte-identical to the frozen `cap_pairs22_capacity_d4_swap.hex` table from the certificate package.

## 3. Full R1 coverage / CNF construction

When the frozen profile CNFs, pair tables, leaf CNFs and solver reports are available, use the exact imported coverage auditor:

```bash
python3 source/coverage/audit_coverage.py \
  --profiles /path/to/profiles22 \
  --pairs /path/to/cap_pairs22_capacity_d4_swap.hex \
  --alternative-pairs /path/to/pairs22_filtered_ordered_d4.hex \
  --all-caps /path/to/caps22_diag_independent.hex \
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

## Current archival gate

The public repository currently contains the proof architecture, exact audit source, small audit outputs, final-ledger summary, package/proof hashes, and an independent reconstruction log. The 45.7 GB proof-body archive itself still requires a stable public archival location.

Therefore these instructions do **not** yet justify changing R from `AWAITING_ARTIFACT_IMPORT` to `COMPLETE`.
