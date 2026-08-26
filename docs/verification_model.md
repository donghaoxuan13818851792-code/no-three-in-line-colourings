# Verification model

The purpose of this repository is not merely to reproduce solver output. It is to make every computational theorem claim independently checkable.

## Four evidence layers

### C0 — mathematical coverage

The human proof must show that every hypothetical colouring belongs to the enumerated profile/branch universe.

### C1 — catalogue and symmetry coverage

Frozen catalogues must have precise membership predicates. Orbit expansion and canonicalisation must be checked independently where possible.

### C2 — work-item coverage

For a branch divided into residual instances, the ledger must prove that every required canonical instance appears exactly as intended.

### C3 — terminal correctness

Every terminal instance must have acceptable evidence.

For SAT:
- explicit witness;
- independent reconstruction;
- exact collinearity verification.

For UNSAT:
- formal proof object when available; or
- complete exact exhaustive trace/ledger with an independently auditable verifier.

## Forbidden status upgrades

The following must never be interpreted as global UNSAT:

- timeout;
- resource limit;
- interrupted or crashed run;
- partial shard completion;
- local-neighbourhood UNSAT;
- bounded search failure;
- solver UNKNOWN;
- absence of a witness in a heuristic search.
