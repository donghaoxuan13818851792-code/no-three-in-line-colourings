# No-three-in-line colourings of square grids

Computational companion repository for the project on arc-proper colourings of square integer grids.

For
\[
G_n = \{0,1,\ldots,n-1\}^2,
\]
an **arc-proper colouring** is a colouring in which no three collinear grid points have the same colour.

This repository is intended to make the computational parts of the project independently auditable. Its main current focus is the exclusion of a six-colouring of \(G_{11}\).

## Scope

The repository will contain:

- human-readable descriptions of the mathematical reductions;
- frozen catalogue definitions and validation tools;
- branch-by-branch search inputs and terminal evidence;
- independent verifiers;
- manifests and cryptographic hashes for large external artifacts;
- claim-to-artifact mappings matching the manuscript.

Large catalogues and production outputs should not be committed directly when they are too large for ordinary Git. They should be archived in a release or external repository and referenced here by immutable hashes.

## G11 proof architecture

A hypothetical six-colouring of \(G_{11}\) is reduced by long-line rigidity and deficit bookkeeping to finitely many colour-class profiles.

The proof is organised into three top-level families:

- **R** — at least two size-22 colour classes;
- **Q** — exactly one size-22 colour class;
- **P** — no size-22 colour class.

The R family has two logically distinct stages. The subcase with three or more size-22 classes is eliminated by triangle-freeness of the size-22 disjointness graph. The remaining exactly-two subcase is reduced to 119 canonical compatible-pair orbits, 11 residual deficit profiles, and 1,309 terminal residual instances. See [`g11/R/README.md`](g11/R/README.md).

The complete deficit-profile coverage checksum is

\[
44 = 16 + 11 + 10 + 7,
\]

where 16 profiles have at least three zero deficits, 11 have exactly two, 10 have exactly one, and 7 have none.

See:

- [`docs/g11_overview.md`](docs/g11_overview.md)
- [`docs/g11_algorithm.md`](docs/g11_algorithm.md)
- [`docs/verification_model.md`](docs/verification_model.md)
- [`PAPER_CLAIMS.md`](PAPER_CLAIMS.md)
- [`STATUS.md`](STATUS.md)

## Evidence rule

A branch is marked **COMPLETE** only when all required mathematical coverage, catalogue coverage, work-item coverage, and terminal verification are present.

Timeouts, resource limits, interrupted runs, bounded searches, near-colourings, and solver `UNKNOWN` states are **not** treated as UNSAT evidence.

## Repository status

`STATUS.md` is the authoritative public status ledger inside the repository. Large final proof archives are imported by immutable metadata and hashes before a branch is promoted to `COMPLETE`.
