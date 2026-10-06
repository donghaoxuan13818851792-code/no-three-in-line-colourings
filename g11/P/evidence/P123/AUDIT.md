# P1–P3 full independent replay — 6 October 2026

The unchanged separately authored `p123_independent_verifier.cpp`, including
`p1_independent_search.cpp`, was freshly compiled with clang on an Apple M4
Mac (10 cores, 24 GiB RAM). All 127,491 first-cap representatives were
partitioned by index modulo 60. Each of the 60 actual runs exited 20, reported
zero satisfiable residuals, and produced its own residual stream.

The independent replay covers **708,638 residual instances**. For every
historical primary shard, grouping the new parts modulo six reproduces all
first-cap, examined/accepted depth-2/3/4, residual-instance and SAT counters.
All streams contain the expected number of 37-point, 121-bit masks.
The fresh source/include and frozen input hashes are bound in `build.json`;
the repository's audit-only entry point rechecks those bindings as well.

Actual native elapsed time: **1,255.48 seconds (20.92 minutes)**.
Actual summed user+system CPU time: **2.70674 CPU hours**. These exclude the
earlier disk-reserve interruption, which did not complete a part and is not
counted as UNSAT.

The exact new evidence archive is publicly deposited at the URL in
[`replay_20261006/archive.json`](replay_20261006/archive.json); its server size
and SHA-256 match the local archive. It retains all 60 streams, native
outputs, progress/time logs, status files, commands, build metadata and the
coordinator source used for execution. All 240 archived stream/output/log/status
hashes were checked against the audit before upload.

The Git excerpt preserves the individual run records, build, timings and audit.
No old empty output was overwritten and no historical six-shard status was
synthesised. The archived execution coordinator is preserved as run; the current
repository coordinator additionally rejects reused run directories, validates
input bindings in audit-only mode and terminates complete job process groups.

## Reproduce

From this repository, perform a fresh independent computation in a new folder:

```sh
python3 scripts/run_local_verification.py --run /path/to/new-run --workers 10
```

Without a `followups.json` in that folder this runs P1–P3 only. For a record
audit, download and hash-check the archive from `archive.json`, extract it,
then use:

```sh
python3 scripts/run_local_verification.py --audit-only --run /path/to/P123_independent_replay_20261006
```

The replay closes the missing independent P1–P3 execution records under the
documented frozen catalogue and branch reduction. Catalogue correctness and
the other G11 branches keep their separate obligations.
