# Project status

This file records the evidence status of the computational proof components.

**Important:** manuscript wording may temporarily assume the planned final result. This file must instead reflect the evidence actually deposited and audited in the repository.

## Status vocabulary

- `COMPLETE` — full scope covered and final evidence independently checked.
- `AWAITING_ARTIFACT_IMPORT` — the branch is reported complete, but at least one frozen artifact needed for repository-level independent replay still lacks a stable public archival location or has not yet been imported and checked here.
- `INDEPENDENT_VERIFICATION_PENDING` — primary execution evidence is imported and audited, but required independent result records are missing or incomplete.
- `INCOMPLETE` — global proof obligation remains open.
- `NOT_APPLICABLE` — no computation is required.

## G11 six-colouring exclusion

| Branch | Profile family | Repository status |
|---|---|---|
| R | R0: ≥3 size-22; R1: exactly two size-22 | AWAITING_ARTIFACT_IMPORT |
| Q1–Q4 | one size-22 class | COMPLETE |
| Q5–Q6 | one size-22 class | COMPLETE |
| Q7 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q8–Q9 | one size-22 class | AWAITING_ARTIFACT_IMPORT |
| Q10 | (22,20,20,20,20,19) | INCOMPLETE |
| P1–P3 | no size-22 class | INDEPENDENT_VERIFICATION_PENDING |
| P4–P5 | three size-21 classes | AWAITING_ARTIFACT_IMPORT |
| P6 | (21,21,20,20,20,19) | INCOMPLETE |
| P7 | (21,20,20,20,20,20) | INCOMPLETE |

## Evidence import — 26 September 2026

Q1–Q4 now have repository-local frozen inputs, all six primary shard
outputs/logs/status files, and the existing independent verifier inputs and
residual ledger. The primary and independent audits both pass from the
repository tree. They cover all 89 fixed size-22 representatives and 670
residual instances, with zero satisfiable residuals. The search itself was
not rerun during this import.

Q5–Q6 are complete within the documented Q5/Q6 reduction, backed by the exact
41,823,110-byte v2 archive at the versioned public
[Q5/Q6 evidence release](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/download/q56-complete-elimination-v2/g11_q56_complete_elimination_v2.zip).
Its SHA-256 is
`781859c9be9f6ba023399b91eae21814be365f28134394afb4c87954a182c46b`.
The archive's existing nine-shard coverage auditor passed against the full
archive. A source, ledger, and audit excerpt is also in the Git tree; the
149,311,162-byte residual input is in the release asset rather than ordinary
Git history.

P1–P3 remain `INDEPENDENT_VERIFICATION_PENDING`. Their primary six-shard audit passes
with 127,491 first caps and 708,638 residual instances, and the primary
source, inputs, manifests, outputs, logs, statuses, and audit are imported.
Independent verification remains pending: the available independent shard
outputs are empty and the required independent `.status` files are missing.
The imported P1–P3 files are explicitly primary evidence only; no missing
records were synthesized.

Q7 and Q8/Q9 remain pending. The Q7 audit from its extracted package rejected
the `w00` command record. The Q8/Q9 audit attempted from a temporary
extraction rejected the `q8w0` command path; relocation may account for that
mismatch, so this is not treated as a successful audit. No completion claim
is made for either package. Q10 remains `INCOMPLETE`; this import did not
read or copy the Q10 TAR or its run records. P4/P5, P6, P7, and R1 evidence
remain as listed above.

### R import note

The small R evidence layer is now largely self-contained in Git. The repository contains the R0/R1 mathematical scope, the 44-profile coverage audit, the four small frozen catalogue/pair files, the exact frozen cap generator and D4 canonicalizer, triangle-free and 930→119 audit source, the compact 1309/1309 final-ledger summary, proof-verification driver source, and fresh reconstruction logs for the small R0/R1 layer.

A fresh exhaustive catalogue reconstruction was completed on 26 August 2026 from repository commit `8e35fc930de2d5ecb447759770415e283803a22d`. On an Apple M4 / macOS 27 system with clang 17 and Python 3.14.7, the frozen generator traversed 534,934,909 search nodes in approximately 30 seconds and reproduced 1,120 oriented solutions, 676 caps meeting both long diagonals, and 89 `D4` representatives. Both the 676-cap catalogue and the 89-orbit catalogue were reproduced byte-for-byte. The same replay reconfirmed 2,138 disjoint pairs, zero triangles, 930 capacity-feasible pairs and 119 `D4` × pair-swap orbits. The detailed log is `g11/R/evidence/catalogue_reconstruction_20260826_m4.txt`.

The separate fresh 2026-08-26 frozen-source reconstruction is a re-execution of frozen source, not a separately implemented checker. A structurally independent implementation remains a separate evidence requirement.

R nevertheless remains `AWAITING_ARTIFACT_IMPORT` because the full 45.7 GB proof-body archive and the large certificate packages still need stable public immutable archival locations, followed by a public full 1,309-proof replay and final independent audit.

The table above is deliberately conservative. A reported result is not promoted to `COMPLETE` merely because a summary or manuscript statement says UNSAT.

## Final theorem gate

The repository may support the statement

> no valid six-colouring of \(G_{11}\) exists

only after every required R/Q/P branch is `COMPLETE`.

Until then, the G11 lower-bound proof should be treated as incomplete at repository evidence level.
