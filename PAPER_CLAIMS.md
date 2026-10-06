# Claim-to-artifact map

This document maps manuscript claims to the objects needed to verify them.

## Whole-paper evidence review — 6 October 2026

The local campaign checks deposited evidence and explicit finite certificates.
Its results do not certify every assertion in the manuscript. `QUEUED` below
means the program has been scheduled; it is not a passing result. `NOT_YET_MAPPED`
means a matching frozen artifact has not been identified in the material reviewed
so far, rather than a claim that the authors never produced it.

| Manuscript claim | Evidence needed | Current usable evidence and check | Remaining obligation |
|---|---|---|---|
| Optimal values and counts for grids 1–4 | exact finite enumeration and equivalence convention | short mathematical/direct-enumeration claims in the manuscript | a reproducible count table under the paper's D4 × colour-relabel convention |
| C(5)=62, C(7)=1,726 | complete representative sets, exhaustive generation, canonicalisation and count manifests | NOT_YET_MAPPED | bind the claimed lists to complete runs and check validity, uniqueness and orbit coverage |
| C(6)=2,949,015,889 | 33 profile contributions, identity/nonidentity fixed-point ledger, implemented equal-size colour permutation action | displayed four-subtotal arithmetic PASS | all 33 rows, Burnside integrality, source/input hashes and fixed-point method; a subtotal sum is not a second enumeration |
| C(8)=2 | complete 380 oriented full-arc input, four unordered covers, D4/colour canonicalisation | explicit eight-grid seed PASS | classification and complete cover/orbit ledger NOT_YET_MAPPED |
| χ(G9)=5 | valid five-colour matrix and row-capacity lower bound | manuscript matrix PASS by two independent geometry methods | fresh matrix result is deposited; the lower bound follows from four classes of size at most 18 covering at most 72 of 81 cells |
| C(9)=743 | full final catalogue and exhaustive primary/independent enumerations | existing random-search catalogue of 598 observed classes PASS for validity/canonicalisation | the 743-class final release, completeness and independent enumeration; 598 observed classes do not refute or establish 743 |
| χ(G10)=6 | six-colour witness and exclusion of five colours | exact route2 package 0.1.1 publicly archived; witnesses and fresh DRAT/CNF reconstruction PASS | route2 proof and exact CNF binding pass; route2 checks a different route from the paper's full-arc/corner explanation |
| χ(G12)=7 | seven-colour witness plus complete full-arc/corner exclusion of six colours | manuscript upper-bound matrix PASS | full-arc input, symmetry expansion, all 26 corner cases and complete lower-bound argument NOT_YET_MAPPED |
| χ(G11)=7 | upper bound from restricting G12 witness, every R/Q/P lower-bound branch and catalogue dependency | P1–P3 full independent replay and Q7/Q8/Q9 audits PASS; see STATUS.md for the remaining branches | full R1 proof bodies; global P4/P5, P6 and P7 terminal evidence; independent global Q10 correctness |
| Packing lower bounds at n=14,16,18,20 | exact full-arc inputs, oriented orbit expansion, complete packing exclusions and terminal evidence | NOT_YET_MAPPED | locate frozen inputs and all four complete runs; adjacent odd-grid bounds also require the monotonicity argument |
| Infinite family χ(G8p)≤8p−8 | human proof of field partition/absorption and exact finite seed conditions | seed, 1,024 reflection memberships, prime-list and displayed-prime admissibility PASS | mathematical review of the construction; finite checks do not prove the infinite family |
| Smallest admissible prime 185,456,518,679 | complete candidate search/CRT coverage and primality evidence | exact primality and all required residue conditions PASS for this example | no smaller candidate exists is a separate claim; the exhaustive search record is NOT_YET_MAPPED |

The route2 G10 archive SHA-256 is
`e8e2a9ac54261ca2ac2730c5759bf2b4e1896d3f3e045fab20b1b3a5320e80b9`.
The classification packages and larger-grid packing records need their own
immutable artifact bindings before the manuscript's supplement table can be
treated as an audited availability statement.

The newly reviewed P4/P5 delivery explicitly states `P4_resolved=false`,
`P5_resolved=false`, and `complete_global_residual_decisions=false` in
`grid11_p45_professor_linux_final_20260726_v2/reports/P45_STATUS.json` inside
the existing `g11 p45.zip`. It has complete outer counting/reduction and pilot
checks, but not terminal decisions for all 544,481,464 canonical records.
The separately reviewed research package also states both branches are UNKNOWN.
Consequently the received P4/P5 evidence is globally incomplete, irrespective
of whether its package-integrity auditor passes.

See [the local verification plan](docs/local_verification_plan_20261006.md)
and [catalogue coverage review](docs/catalogue_coverage_review_20261006.md) for
the checked predicates, resource limits and limits of the replay.

## G11 lower bound

### Claim

There is no arc-proper six-colouring of \(G_{11}\).

### Human-readable mathematical coverage

1. Long-line rigidity on all rows, columns, and the two main diagonals.
2. Deficit-singleton identity
   \[
   d_i = 22-|C_i|,
   \qquad
   \sum_i d_i = 11.
   \]
3. Exhaustive profile classification: 44 deficit profiles in total.
4. Size-22 compatibility reduction: 16 profiles with at least three zero deficits are eliminated by triangle-freeness of the size-22 disjointness graph.
5. Remaining coverage identity:
   \[
   28 = 11_R + 10_Q + 7_P.
   \]
6. Sound symmetry reduction and branch-specific exact residual formulations.

See [`docs/g11_overview.md`](docs/g11_overview.md).

### R claim decomposition

The top-level claim `G11-R` means “no valid six-colouring has at least two size-22 colour classes”, but its proof has two distinct evidence nodes:

| Evidence node | Claim | Required evidence | Location |
|---|---|---|---|
| G11-R0 | three or more size-22 classes are impossible | admissible size-22 catalogue + disjointness graph + triangle-free audit + profile coverage | `g11/R/evidence/` |
| G11-R1 | exactly two size-22 classes are impossible | 930 capacity-feasible pairs → 119 canonical pair orbits → 11 profiles → 1309 leaves → 1309/1309 terminal verification | `g11/R/` |

The 1,309 terminal instances cover **R1 only**. They do not by themselves cover the phrase “at least two size-22 classes”; R0 must be included separately.

### Computational evidence nodes

| Evidence node | Required content | Location |
|---|---|---|
| G11-R0/R1 | complete R0 graph obstruction + R1 terminal certificates | `g11/R/` |
| G11-Q | Q1–Q10 branch evidence | `g11/Q/` |
| G11-P | P1–P7 branch evidence | `g11/P/` |
| catalogue validation | frozen catalogue predicates, counts and hashes | `g11/catalogues/`, `verification/catalogues/` |
| terminal validation | certificate/ledger verification | `verification/unsat/` |
| independent checks | separately implemented reconstruction/checks | `verification/independent/` |
| artifact hashes | immutable checksums | `manifests/` |

### Completion condition

The manuscript claim is evidence-complete only if:

- every mathematical branch is covered;
- every frozen catalogue used by the reduction is validated;
- every canonical work item is accounted for exactly once;
- every terminal result is SAT with a verified witness or UNSAT with acceptable exact evidence;
- no timeout, missing item, interruption or UNKNOWN is silently counted as UNSAT;
- the artifact manifest identifies the precise frozen inputs and outputs.
