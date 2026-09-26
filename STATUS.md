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
| Q7 | one size-22 class | COMPLETE |
| Q8–Q9 | one size-22 class | COMPLETE |
| Q10 | (22,20,20,20,20,19) | COMPLETE |
| P1–P3 | no size-22 class | COMPLETE |
| P4–P5 | three size-21 classes | AWAITING_ARTIFACT_IMPORT |
| P6 | (21,21,20,20,20,19) | INCOMPLETE |
| P7 | (21,20,20,20,20,20) | INCOMPLETE |

## Evidence import — 26 September 2026

Q1–Q4 have repository-local frozen inputs, all six primary shard outputs/logs/status files, and the existing independent verifier inputs and residual ledger. Primary and independent audits both pass for all 89 fixed size-22 representatives and 670 residual instances, with zero satisfiable residuals.

Q5–Q6 are complete within the documented reduction. The exact 41,823,110-byte v2 archive is attached to the versioned public [Q5/Q6 evidence release](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/download/q56-complete-elimination-v2/g11_q56_complete_elimination_v2.zip), SHA-256 `781859c9be9f6ba023399b91eae21814be365f28134394afb4c87954a182c46b`. Its nine-shard coverage audit passed against the complete archive. The 149,311,162-byte residual input remains in the release asset rather than ordinary Git history.

Q7, Q8 and Q9 now have stable public archive assets and pass the relocation-aware package audits. Q7 covers all nine workers and `[0,1325039)`. Q8 and Q9 cover all 89 fixed representatives and the shared 412,995-row prefix universe. The historical strict scripts still report their recorded absolute command mismatch after relocation; the frozen package verifiers and prefix-universe verifier pass. See [`g11/Q/evidence/`](g11/Q/evidence/README.md) and the [2026-09-26 evidence release](releases/g11-evidence-20260926/README.md).

Q10 is complete across 89 fixed representatives. Eighty-five representatives have fresh 55-shard raw terminal audits; representatives 17, 76 and 88 have prior raw 55-shard audits; representative 53 has a complete native 3,025-shard enumeration audit and exact terminal join record. Every join has zero final candidates and no witness. The original 10,399,498,240-byte TAR is preserved in six public release parts with a reconstruction manifest. The historical 85-row `join-status.tsv` is preserved as an earlier snapshot; the later `join-summary.tsv` and raw audits supersede its `MISSING` rows. See [`g11/Q/evidence/Q10/FINAL_AUDIT.md`](g11/Q/evidence/Q10/FINAL_AUDIT.md).

P1–P3 now have a completed independent six-shard result run. It covers 127,491 first caps and 708,638 residual instances, agrees with the primary statistics, and reports zero residual SAT results. All output, log, status, residual-stream and command hashes are recorded in [`run_manifest.tsv`](g11/P/evidence/P123Independent/run_20260926T032326Z/run_manifest.tsv); the portable import audit passes. Residual masks are instances: 1,523 repeated encodings occur across distinct instances, so no global uniqueness claim is made.

### Remaining evidence

R remains `AWAITING_ARTIFACT_IMPORT` because its 45.7 GB proof-body archive and certificate packages still need stable public archival locations, followed by a public full 1,309-proof replay and final independent audit. P4/P5, P6, and P7 remain as listed above.

The repository may support the statement

> no valid six-colouring of \(G_{11}\) exists

only after every required R/Q/P branch is `COMPLETE`. The global theorem remains incomplete at repository evidence level.
