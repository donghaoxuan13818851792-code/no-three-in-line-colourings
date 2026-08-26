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

The R import now contains:

- the precise R0/R1 mathematical scope;
- the 44-profile coverage audit and the identity `44 = 16 + 11 + 10 + 7`;
- the 676/89 size-22 audit and triangle-free disjointness-graph result;
- the sound residual line-capacity condition and the reconstructed `2138 → 930 → 119` pair reduction;
- compact 1309/1309 final-ledger evidence;
- exact frozen audit/coverage/proof-driver source files with recorded SHA-256 hashes;
- a repository-session independent reconstruction log;
- hashes and byte counts for the staged 0.1.0/0.1.1 certificate packages and the 45.7 GB proof-body archive.

R nevertheless remains `AWAITING_ARTIFACT_IMPORT` because the full 45.7 GB proof-body archive and the large certificate packages still need stable public archival locations (or equivalent immutable release objects) before repository-level replay is self-contained. The small frozen data files used by the imported source are also currently tracked by immutable hashes while their byte-level public placement is being finalised.

The table above is deliberately conservative. A reported result is not promoted to `COMPLETE` merely because a summary or manuscript statement says UNSAT.

## Final theorem gate

The repository may support the statement

> no valid six-colouring of \(G_{11}\) exists

only after every required R/Q/P branch is `COMPLETE`.

Until then, the G11 lower-bound proof should be treated as incomplete at repository evidence level.
