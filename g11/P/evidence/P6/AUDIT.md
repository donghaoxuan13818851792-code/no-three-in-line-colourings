# P6 handoff audit — 6 October 2026

## Result and scope

The newly received archive contains a successful Apocrita run for all **10,787
fixed-orientation inputs for A = `024110014808a0004848a0000ca0002`**, in 169 chunks.
All decision records are terminal `UNSAT_P6_RESIDUAL`, exit 20. Their source,
Linux binary, input, pairgrid, candidate-list, and output hashes bind correctly.
The ledger audit also reconstructs each D4 × pair-swap key and matches all
10,787 pair records. It counts 13,510,361 candidate occurrences.

A fresh clang C++20 build on this Mac re-executed the backend for **all
10,787 inputs**, using the received candidate lists. Every execution returned
UNSAT/20 with empty stderr, and every deterministic search counter matched the
primary log. The fresh run used two workers and took 44.38 seconds.
The full replay outputs and their SHA-256 are recorded under `audits/`.

This is **primary evidence validation and frozen-source backend replay**.
The 13-hour candidate enumeration was not rerun. Matching candidate hashes,
counts and basic membership do not independently prove that no candidate was
omitted. The received Q5/Q6, Q7 and Q8/Q9 filter claims are not newly proved by
this audit. No structurally independent full UNSAT proof was produced.
**Global P6 remains INCOMPLETE.** The one historical first-cap branch does not
cover the frozen global outer universe of 266,771,874 retained canonical pairs.
These counts must not be subtracted as if they represented the same universe.

## Supplied verifier result

The new archive's unmodified `verify_handoff.py` was actually run and rejected
it with exit 1: `FAIL: top-level manifest file universe differs`.
The repository auditor found 2,516 previously manifested files, all present
with unchanged hashes, plus **87,907 unmanifested additions** (90,423 files in
the verifier's universe). The old manifest, status and verifier still describe
26 terminal regression cases. This rejection is preserved; it was not patched
into a pass. A separately run verifier for the older August package passed,
and that result is explicitly labelled legacy.

## Run and failure history

- Job 24428447: full fixed-A run, 26 August 12:02:55 BST to 27 August
  01:34:52 BST; 10,787 UNSAT, zero SAT/ERROR/INCOMPLETE, driver exit 0,
  empty Slurm stderr. The Slurm script and final stdout/stderr are imported.
- Job 24427405: earlier 64-input launch failed with exit 127 because the
  relative driver path was absent in its working directory. It is retained as
  a failed launch, not a terminal mathematical result.
- Job 24427919: successful 64-input rerun, all 64 UNSAT, driver exit 0,
  empty Slurm stderr. This is an overlapping preliminary run, not extra coverage.
- The archive also preserves test/terminal26 runs. Its Slurm array labelled
  terminal26 is not assumed identical to the older 26-case regression ledger.

## Remaining gaps

1. A refreshed manifest and status covering the delivered HPC additions.
2. Global work-item/shard mapping, completion ledger and terminal coverage
   beyond this one historical first-cap branch.
3. Candidate enumeration completeness checked independently, followed by
   independent terminal correctness for the required global scope.
4. Exact original submission commands, compiler/build environment and source
   revision tied to the cluster binaries. Source and binary hashes are present;
   hashes alone do not recover those missing provenance details.
5. An explicit run-wide accounting of crashes, timeouts, reruns and UNKNOWN
   across the whole global computation. The observed failed launch and rerun
   are preserved, but do not establish that no other attempts existed.

## Reproduction

Obtain the exact release archive referenced in `archive.json`, verify its
SHA-256, and extract it outside Git. With `HANDOFF` set to its extracted root:

```sh
python3 "$HANDOFF/verify_handoff.py"  # expected rejection of this delivered archive
python3 g11/P/evidence/P6/scripts/audit_fixed_a_run.py "$HANDOFF"
clang++ -O3 -std=c++20 \
  g11/P/evidence/P6/received/ultra_frozen/optional_prior_work/fixed_A_reuse/src/p6_residual_solver_candidate_input.cpp \
  -o /tmp/p6-backend
python3 g11/P/evidence/P6/scripts/replay_fixed_a_backend.py \
  "$HANDOFF" /tmp/p6-backend /tmp/p6-backend-replay.jsonl --workers 2
```

The last two commands validate supplied candidate lists and replay the backend;
they do not regenerate those lists. The large candidate files, per-task logs,
Linux binaries and dependencies remain in the hash-addressed original archive.
The Git tree contains compact ledgers, source, Slurm records and fresh audits.
