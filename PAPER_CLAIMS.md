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
3. Exhaustive profile classification.
4. Reduction to the R, Q, and P families.
5. Sound symmetry reduction and branch-specific exact residual formulations.

See [`docs/g11_overview.md`](docs/g11_overview.md).

### Computational evidence nodes

| Evidence node | Required content | Location |
|---|---|---|
| G11-R | complete R coverage + terminal certificates | `g11/R/` |
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
