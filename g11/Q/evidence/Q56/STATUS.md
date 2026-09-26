# Status

Final canonical run version: q56-canonical-9x1-20260722_181908.

Result: `FINAL_SHARD_AUDIT PASS workers=9 status=UNSAT`. The full ledger has
1,325,039 rows spanning representative indices 0--88. The run used the
frozen source and executable hashes recorded in `results/run_manifest.tsv`.

This is an exhaustive computational elimination conditional on the documented
Q1--Q4-certified reduction and implementation. It is not a standalone proof
of six-colourability impossibility, and leaves P4--P7 and Q7--Q10 outside the
scope. v2 changes only reproducibility, dependency packaging, relative paths,
and audits; it does not rerun or alter the canonical nine-shard results.
