# Project status

This file records the evidence status of the computational proof components.

**Important:** manuscript wording may temporarily assume the planned final result. This file must instead reflect the evidence actually deposited and audited in the repository.

## Status vocabulary

- `COMPLETE` — full scope covered and final evidence independently checked.
- `AWAITING_ARTIFACT_IMPORT` — result is reported complete elsewhere, but the frozen evidence has not yet been imported and checked here.
- `INCOMPLETE` — global proof obligation remains open.
- `NOT_APPLICABLE` — no computation is required.

## G11 six-colouring exclusion

| Branch | Profile family | Repository status |
|---|---|---|
| R | at least two size-22 classes | AWAITING_ARTIFACT_IMPORT |
| Q1–Q4 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q5–Q7 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q8–Q9 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q10 | (22,20,20,20,20,19) | INCOMPLETE |
| P1–P3 | no size-22 class | AWAITING_ARTIFACT_IMPORT |
| P4–P5 | three size-21 classes | AWAITING_ARTIFACT_IMPORT |
| P6 | (21,21,20,20,20,19) | INCOMPLETE |
| P7 | (21,20,20,20,20,20) | INCOMPLETE |

The table above is deliberately conservative. A reported result is not promoted to `COMPLETE` until its final ledger/certificate and verification material are present in this repository or in a frozen external archive referenced by hash.

## Final theorem gate

The repository may support the statement

> no valid six-colouring of \(G_{11}\) exists

only after every required R/Q/P branch is `COMPLETE`.

Until then, the G11 lower-bound proof should be treated as incomplete at repository evidence level.
