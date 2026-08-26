# R family — at least two size-22 colour classes

The R family is the part of the G11 six-colouring proof with at least two colour classes of size 22. It has two logically different subcases and they must not be conflated.

## R0 — three or more size-22 classes

A valid size-22 colour class must belong to the verified admissible size-22 catalogue.

The imported audit records:

- 676 admissible oriented size-22 caps;
- 89 orbits under the square symmetry group \(D_4\);
- 2,138 edges in the graph whose vertices are the 676 caps and whose edges join disjoint caps;
- 0 triangles in this disjointness graph.

Three distinct colour classes in a colouring are pairwise disjoint. Hence three size-22 colour classes would give a triangle in this graph. Since the graph is triangle-free, every profile with at least three zero deficits is impossible.

The profile audit contains exactly 16 such deficit profiles.

Thus R0 eliminates

\[
16\text{ of the }44\text{ initial deficit profiles}.
\]

### Catalogue completeness

There are two different claims here:

1. the committed 676 masks are individually valid size-22 candidates; and
2. the 676-mask list is exhaustive for the admissibility predicate used by R.

The first is checked directly by `source/caps/audit_disjoint_caps.py`. For the second, the repository includes the exact frozen exhaustive generator `source/generator/enumerate_caps.cpp`, the exact frozen `D4` canonicalizer, both frozen output tables, and the reviewer-facing wrapper `source/generator/rebuild_size22_catalogue.py`.

A fresh exhaustive reconstruction was completed on 26 August 2026 from repository commit `8e35fc930de2d5ecb447759770415e283803a22d`. On Apple M4 / macOS 27 with clang 17 and Python 3.14.7, the run traversed 534,934,909 search nodes in approximately 30 seconds and reported

```text
oriented_solutions 1120
meets_long_diagonals 676
```

The regenerated 676-cap catalogue was byte-for-byte identical to `data/caps22_diag_independent.hex`, and its regenerated 89-element `D4` quotient was byte-for-byte identical to `data/caps22_d4.hex`.

Thus the fresh size-22 catalogue-completeness replay is **REPRODUCED / PASS**. The detailed environment, counts, hashes and replay scope are recorded in [`evidence/catalogue_reconstruction_20260826_m4.txt`](evidence/catalogue_reconstruction_20260826_m4.txt).

## R1 — exactly two size-22 classes

After R0, the R family means exactly two size-22 classes.

The certified two-size-22 reduction is:

1. start with the 676 admissible size-22 caps;
2. form the 2,138 disjoint pairs;
3. apply the necessary residual line-capacity test, retaining 930 capacity-feasible pairs;
4. quotient by the simultaneous action of \(D_4\) and swapping the two size-22 colour classes;
5. obtain 119 canonical compatible-pair orbits;
6. combine each pair orbit with each of the 11 exactly-two-zero deficit profiles;
7. obtain exactly
   \[
   119\times11=1309
   \]
   terminal residual instances.

### Why the 2,138 → 930 capacity filter is sound

Let \(C_1,C_2\) be the two fixed size-22 colour classes and let \(\ell\) be any grid line. The other four colours can each occur on \(\ell\) at most twice, so together they can cover at most eight points of \(\ell\). Therefore every extendible pair \((C_1,C_2)\) must satisfy

\[
|\ell|-|(C_1\cup C_2)\cap\ell|\le 8
\]

for every relevant grid line \(\ell\).

Equivalently, the complement of \(C_1\cup C_2\) may contain at most eight points on any line. A disjoint pair that fails this inequality cannot be extended to a six-colouring, so discarding it is a logically necessary pruning step, not a heuristic filter.

The imported audit source reconstructs all 628 maximal relevant grid lines, applies this condition to all 2,138 disjoint pairs, obtains exactly 930 retained pairs, and then canonicalises them under \(D_4\) together with pair-swap to obtain exactly 119 orbits. The same 26 August reconstruction reproduced the 930 and 119 counts, and the regenerated 119-pair production table was byte-for-byte identical to the frozen table.

The 11 deficit profiles are:

| deficits | colour-class sizes |
|---|---|
| 0,0,1,1,1,8 | 22,22,21,21,21,14 |
| 0,0,1,1,2,7 | 22,22,21,21,20,15 |
| 0,0,1,1,3,6 | 22,22,21,21,19,16 |
| 0,0,1,1,4,5 | 22,22,21,21,18,17 |
| 0,0,1,2,2,6 | 22,22,21,20,20,16 |
| 0,0,1,2,3,5 | 22,22,21,20,19,17 |
| 0,0,1,2,4,4 | 22,22,21,20,18,18 |
| 0,0,1,3,3,4 | 22,22,21,19,19,18 |
| 0,0,2,2,2,5 | 22,22,20,20,20,17 |
| 0,0,2,2,3,4 | 22,22,20,20,19,18 |
| 0,0,2,3,3,3 | 22,22,20,19,19,19 |

## Terminal verification

The imported certificate metadata reports:

- expected terminal instances: 1,309;
- completed: 1,309;
- failures: 0;
- final ledger `verified=true`;
- every leaf was solved UNSAT and passed the solver → DRAT → LRAT verification chain.

The final ledger schema is `grid11-twomax-drat-lrat-parallel-v1`.

The full compressed proof-body archive is a separate large artifact (45,687,997,349 bytes) with SHA-256

`0087af20d68402c18728e56bc209e508b5565e9522c0b4185afaf2faf43f994f`.

It is not committed directly to ordinary Git history.

## Coverage chain

The intended reviewer-facing chain is

```text
size-22 admissibility predicate
        ↓
exhaustive generator: 1120 oriented → 676 meeting both long diagonals
        ↓
676 oriented caps / 89 D4 classes
        ↓
disjointness graph: 2,138 edges, no triangles
        ↓
R0: ≥3 size-22 classes impossible (16 profiles)
        ↓
R1: exactly two size-22 classes
        ↓
residual line-capacity condition on all relevant lines
        ↓
930 capacity-feasible disjoint pairs
        ↓
119 canonical D4 × pair-swap orbits
        ↓
11 exactly-two deficit profiles
        ↓
1,309 residual instances
        ↓
1,309 / 1,309 terminal verification
        ↓
public full proof replay + structurally independent audit
```

## Independence terminology

`evidence/independent_replay_20260826.txt` is retained under its historical filename, but its scope is explicit: it is a fresh re-execution and reconstruction using exact frozen source. It is **not** an independently implemented verifier. A structurally separate implementation is still required before the repository claims that strongest form of independent checking.

## Imported evidence

Small audit material and branch metadata are stored under [`evidence/`](evidence/). Exact frozen source is under `source/`, and the four small frozen catalogue/pair files needed by the basic R reconstruction are committed under `data/`.

Large frozen archives are tracked in [`ARTIFACTS.md`](ARTIFACTS.md) and in the repository-wide artifact manifest.

The fresh exhaustive catalogue-completeness gate is now closed. The R branch nevertheless remains conservatively `AWAITING_ARTIFACT_IMPORT` until the remaining completion gates are closed: a structurally independent checker, stable public immutable locations for the large archives, and a public full 1,309-proof replay/final audit.
