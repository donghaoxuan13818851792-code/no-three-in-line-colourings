# Q5/Q6 archive and audit

Status: `COMPLETE`, conditional on the certified Q1–Q4 reduction.

The exact v2 archive is published as the
[Q5/Q6 evidence release asset](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/download/q56-complete-elimination-v2/g11_q56_complete_elimination_v2.zip).
It is 41,823,110 bytes with SHA-256
`781859c9be9f6ba023399b91eae21814be365f28134394afb4c87954a182c46b`.
[`UPSTREAM_ARCHIVE.tsv`](UPSTREAM_ARCHIVE.tsv) records the filename, size,
and digest. The same digest is in the repository artifact manifest.

The archive's existing `scripts/audit_coverage.py` was run against the full
extracted archive on 26 September 2026 and reported
`FINAL_SHARD_AUDIT PASS workers=9 status=UNSAT`. It checks all nine disjoint
shards, exit codes, terminal prefixes, source/executable/input hashes, and
the complete 1,325,039-row prefix coverage. No Q5/Q6 production search was
rerun during this import.

This directory contains a compact excerpt of the source, binary, run
manifest, shard ledger, small terminal records, and audit output. The full
1,325,039-row residual input is 149,311,162 bytes; it is kept in the release
asset rather than Git history. Download the release asset to replay the
complete audit:

```sh
gh release download q56-complete-elimination-v2 \
  --repo donghaoxuan13818851792-code/no-three-in-line-colourings \
  --pattern g11_q56_complete_elimination_v2.zip
unzip g11_q56_complete_elimination_v2.zip
cd g11_q56_complete_elimination_v2
python3 scripts/audit_coverage.py
```

The excerpt's audit script alone cannot run without that full residual input.
