# Final research-package audit

Date: 2026-07-26

## Claim boundary

- P4 status: `UNKNOWN`.
- P5 status: `UNKNOWN`.
- Outcome class: E.
- No SAT witness is claimed.
- No complete branch-level UNSAT certificate is claimed.
- `certificates/` contains only an explicit statement that no final certificate exists.

## Required artifact check

Present and nonempty:

- `P4_P5_RESEARCH_REPORT.md`
- `P4_P5_METHOD_AND_SCOPE.md`
- `P4_P5_PILOT_RESULTS.csv`
- `P4_P5_COMMANDS.md`
- `P4_P5_STATUS.json`

Present directories:

- `src/`
- `data/`
- `pilots/`
- `logs/`
- `audit/`
- `certificates/`
- `historical_noncertified/`

## Independent-formulation ordering

`P4_P5_INDEPENDENT_FORMULATION.md` was written before opening optional historical work.  Its contemporaneous digest is retained in `independent_formulation.sha256`.

## Exact outer-cover audit

The independent auditor re-read all nine atomic ledgers and passed the following checks:

- exactly 127,491 distinguished D4-canonical first-cap representatives;
- exactly the representative positions 0 through 127,490, once each;
- 1,699,467,737 compatible duplicate-retaining occurrences;
- 1,633,664,146 occurrences after the audited size-21 nonextendibility reduction;
- no missing outer shard;
- cross-check agreement with all 180 rows of the modulo-shard pilot and 24 overlapping rows of the earlier stratified pilot.

The outer ledger is a complete cover for the three size-21 classes.  It is not a P4/P5 UNSAT computation because the residual profiles were not solved for all occurrences.

## Dependency audit

The final evidence chain uses only certified dependencies P1-P3 and Q5-Q9.  Q10 and every unresolved P4-P7/Q10 branch are excluded.  The distinction between global size-21 nonextendibility and residual-only size-20 maximality is recorded in `dependency_and_reduction_audit.md`.

An exploratory program version that incorrectly imposed global size-20 maximality was detected, removed from the evidence chain, and quarantined under `historical_noncertified/superseded_global_maximality_pilot/`.

## Build and data-format checks

- All C++ sources compile with g++ 14.2.0 under C++20.
- All Python sources pass `py_compile` under Python 3.13.5.
- All JSON and JSONL artifacts parse.
- `P4_P5_PILOT_RESULTS.csv` parses with 12 experiment rows.
- The status file records Outcome E and both branches as UNKNOWN.
- The supplied context package verifier passed before the investigation.

Compiler warnings from exploratory compact source files are preserved in `source_build_check.stderr`; they are warnings, not build failures.

## Integrity

`SHA256SUMS` hashes every released file except `SHA256SUMS` itself and its verification transcript.  `SHA256SUMS.check` records a successful verification.
