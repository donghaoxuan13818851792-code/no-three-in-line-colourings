# Project status

This file records the evidence status of the computational proof components.

**Important:** manuscript wording may temporarily assume the planned final result. This file must instead reflect the evidence actually deposited and audited in the repository.

## Status vocabulary

- `COMPLETE` — full scope covered and final evidence independently checked.
- `AWAITING_ARTIFACT_IMPORT` — the branch is reported complete, but at least one frozen artifact needed for repository-level independent replay still lacks a stable public archival location or has not yet been imported and checked here.
- `INCOMPLETE` — global proof obligation remains open.
- `NOT_APPLICABLE` — no computation is required.

## G11 six-colouring exclusion

| Branch | Profile family | Repository status |
|---|---|---|
| R | R0: ≥3 size-22; R1: exactly two size-22 | AWAITING_ARTIFACT_IMPORT |
| Q1–Q4 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q5–Q7 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q8–Q9 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q10 | (22,20,20,20,20,19) | INCOMPLETE |
| P1–P3 | no size-22 class | AWAITING_ARTIFACT_IMPORT |
| P4–P5 | three size-21 classes | AWAITING_ARTIFACT_IMPORT |
| P6 | (21,21,20,20,20,19) | INCOMPLETE |
| P7 | (21,20,20,20,20,20) | INCOMPLETE |

### R import note

The small R evidence layer is now largely self-contained in Git. The repository contains the R0/R1 mathematical scope, the 44-profile coverage audit, the four small frozen catalogue/pair files, the exact frozen cap generator and D4 canonicalizer, triangle-free and 930→119 audit source, the compact 1309/1309 final-ledger summary, proof-verification driver source, and a fresh re-execution log for the small R0/R1 reconstruction.

The repository also contains a reviewer-facing wrapper for exhaustive reconstruction of the size-22 catalogue. That full generator replay still needs to be run to completion and recorded as a repository evidence log; the current session imported the capability but did not record a completed 1120→676 replay.

The fresh 2026-08-26 reconstruction is a re-execution of frozen source, not a separately implemented checker. A structurally independent implementation remains a separate evidence requirement.

R nevertheless remains `AWAITING_ARTIFACT_IMPORT` because the full 45.7 GB proof-body archive and the large certificate packages still need stable public immutable archival locations, followed by a public full 1,309-proof replay and final independent audit.

The table above is deliberately conservative. A reported result is not promoted to `COMPLETE` merely because a summary or manuscript statement says UNSAT.

## Final theorem gate

The repository may support the statement

> no valid six-colouring of \(G_{11}\) exists

only after every required R/Q/P branch is `COMPLETE`.

Until then, the G11 lower-bound proof should be treated as incomplete at repository evidence level.
