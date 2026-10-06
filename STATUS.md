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
| Q10 | (22,20,20,20,20,19) | INDEPENDENT_VERIFICATION_PENDING |
| P1–P3 | no size-22 class | COMPLETE |
| P4–P5 | three size-21 classes | INCOMPLETE |
| P6 | (21,21,20,20,20,19) | INCOMPLETE |
| P7 | (21,20,20,20,20,20) | INCOMPLETE |

## Local campaign — 6 October 2026

The bounded local campaign's available checks are complete and reviewed.
Its preserved coordinator state includes a disk-reserve interruption just
before the final native proof checker completed; that checker then produced
genuine verified evidence. No clean coordinator exit is claimed. Actual costs,
raw receipts and remaining gaps are recorded in
`docs/local_verification_results_20261006.md` and `PAPER_CLAIMS.md`.

P1–P3 now pass a **full fresh independent replay**: 60 disjoint actual parts,
127,491 anchors, 708,638 residual instances, all exits 20, no SAT, and all
primary prefix/instance counters matching when grouped modulo six. Native
elapsed time was 20.92 minutes and summed CPU time 2.707 hours on the M4.
The old missing/empty six-shard records are preserved as historical omissions;
the new independently executed records are separately archived and audited.
See `g11/P/evidence/P123/AUDIT.md`.

Q7 and Q8/Q9 now have exact original ZIPs at immutable public URLs, full
manifest/file-universe passes, passing unchanged strict terminal audits with
explicit historical-path relocation, and fresh prefix and Boolean/profile
checks. Their large terminal searches were not rerun. The new archives and
P1–P3 replay are in the
[local verification release](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/tag/local-verification-20261006),
with all four initial asset server sizes and SHA-256 digests checked.
See `g11/Q/evidence/Q7/AUDIT.md` and `g11/Q/evidence/Q89/AUDIT.md`.

The explicit G9/G10/G12 upper-bound matrices, the eight-grid seed/reflection
table, finite prime-list/example conditions, small G11 graph/profile arithmetic,
and the existing observed 598-class G9 catalogue pass fresh checks. The G10
route2 five-colour exclusion also passes fresh DRAT and independently audited
CNF reconstruction. Their claim boundaries are in `verification/paper/20261006/`.

All 89 Q10 catalogues now pass fresh independent geometric membership checks
on 75,666,410 masks, with exact source, archive, anchor and per-catalogue
bindings. This takes 0.03551 native CPU hours and 19.43 seconds elapsed in
the streamed catalogue workers. Q10 remains `INDEPENDENT_VERIFICATION_PENDING`
because enumeration completeness and independent global join/UNSAT correctness
are separate obligations. The existing at-least-two-extendible sector now also
passes all 88 fresh DRAT checks and the full strict rep1 IDRUP check, together
with source/transcript binding for 2,200 UNSAT queries. That sector pass does
not close the global Q10 obligation.

P4/P5 is now recorded as `INCOMPLETE`, correcting the earlier import-only
placeholder. The existing final Linux delivery explicitly reports both
profiles unresolved, global residual decisions incomplete and no gap-free
global terminal ledger. Its 544,481,464-record outer reduction/count is not
a complete UNSAT decision; the 57,755-case comparisons are finite pilot checks.
The matching research-package final audit likewise says UNKNOWN for both
branches. No newly reviewed package establishes complete global P4/P5.

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

## P6 handoff — 6 October 2026

The new P6 archive adds 10,787/10,787 terminal UNSAT records for one historical
fixed-A branch, in 169 chunks. The repository evidence audit passes, and a
freshly compiled backend replays all 10,787 supplied candidate lists with
matching deterministic search counters. The candidate enumeration itself was
not repeated or independently proved complete. The supplied handoff verifier
rejects the delivered archive because 87,907 added files are absent from its
old manifest; all 2,516 old manifested files still match. The exact rejection,
observed failed launch/rerun, replay ledger and remaining gaps are retained in
[g11/P/evidence/P6/AUDIT.md](g11/P/evidence/P6/AUDIT.md).

P6 remains INCOMPLETE: this local branch does not cover the 266,771,874 retained
canonical pairs in the global frozen scope, and independent terminal
verification remains outstanding.

## Q10 HPC handoff — 6 October 2026

The new archive supplies 85 terminal catalogue/join chains, including the
previously missing rep1 join. Together with the four frozen anchor-local
results, primary coverage now reaches all 89 representatives. The archive
coverage and hash auditor passes 257,125 catalogue records and 4,675 new join
shards, checking 74,011,954 masks in sorted shard unions. The supplied join
auditor also passes fresh checks for all 85 new join chains. The old 23,594-file
manifest remains byte-correct but omits 533,182 additions, so the supplied
verifier's manifest stage rejects the new archive. See
[g11/Q/evidence/Q10/AUDIT.md](g11/Q/evidence/Q10/AUDIT.md).

Q10 is now INDEPENDENT_VERIFICATION_PENDING at repository evidence level.
No independent global UNSAT proof, catalogue regeneration or join search replay
is claimed. Full fresh DRAT/IDRUP replay passes for the deposited proof sector
only. The earlier September import note
and the received frozen status files describe the older boundary, not the new
primary execution coverage.

## Final theorem gate

The repository may support the statement

> no valid six-colouring of \(G_{11}\) exists

only after every required R/Q/P branch is `COMPLETE`.

Until then, the G11 lower-bound proof should be treated as incomplete at repository evidence level.
