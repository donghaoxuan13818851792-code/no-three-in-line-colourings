# Claim-to-artifact map

This document maps manuscript claims to the objects needed to verify them.

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
