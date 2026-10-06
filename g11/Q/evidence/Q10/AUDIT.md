# Q10 HPC handoff audit — 6 October 2026

## New evidence and status

The received archive adds complete primary catalogue/join records for the
**85 representatives not exhausted by the older handoff**, including the
previously missing representative-1 join. Together with the four previously
audited anchors 17, 53, 76 and 88, the primary record chain covers all **89
frozen D4 representatives**. No old “85 unresolved” claim is carried forward
as the latest execution status.

The archive auditor passes with:

- 257,125 catalogue shard records: 85 × 3,025 exact row/column-pair keys;
- 74,011,954 masks in their sorted shard unions;
- 4,675 terminal join shards: 85 × 55 exact root-row-pair keys;
- all new joins `COMPLETE_NO_WITNESS`, exit 20;
- zero missing records, identity/hash mismatches, or missing source/binary
  bindings; frozen representative input hash unchanged.

Each immutable catalogue identity, source and binary hash, command anchor,
shard ID, mask-file hash/count, reconstructed shard union, catalogue/log hash,
join metadata and terminal output is bound to its exact archive bytes. Saved
join audit hashes and search counters are checked against all underlying
outputs. The compact 89-row ledger is `audits/representative_ledger.json`.
The old four-anchor chain is retained by exact equality of all previously
manifested bytes; the full old handoff verifier was also run and passed.

The package's unmodified `audit_join_shards.py` was also re-executed for
**all 85 new join chains**, using one small temporary extraction at a time and
hash-checked relocated catalogues/Linux binary. All 85 native checks passed;
they validate all terminal outputs, exit files, resource records and 55-way
coverage. Their fresh reports are under `audits/native_join_rechecks/`.
This auditor re-execution took 14.86 seconds and did not rerun a join search.
Temporary extraction times affect only operational mtime-based makespan
estimates, not mathematical status or content hashes.

**Repository Q10 status: INDEPENDENT_VERIFICATION_PENDING.** The new execution
coverage closes the former missing-primary-run gap, but does not by itself
establish independently verified global UNSAT.

## Fresh all-catalogue geometry replay

The complete remote ZIP was reassembled by streaming all 63 release parts,
with every part and the full archive hash verified. The separately authored
`q10_cap20_catalogue_audit.cpp` was then freshly compiled, unchanged, on the
M4 Mac and run on **all 89 exact catalogues: 75,666,410 masks**.

Every catalogue file hash and count matches its received metadata, every
anchor binds to the frozen 89-representative list, and all 85 new saved audit
counter strings agree exactly. The checker verifies 20-point size, absence
of collinear triples, anchor disjointness, row/column occupancy and singleton
conditions, residual line capacities, strict ordering/uniqueness, and
extendibility/least-eligible classification against the 676-cap catalogue.

All 89 cases pass. Summed native CPU time is **0.03551 CPU hours**; elapsed
catalogue-worker time including streamed extraction is **19.43 seconds**.
Archive hashing and compilation are additional setup time. Results and actual
per-case stdout/stderr/exit records are in `audits/membership_replay_20261006/`.
This validates catalogue membership and stored counters. Independent
enumeration completeness and global join/UNSAT correctness remain open.

## Supplied verifier and storage

The supplied `verify_handoff.py` source is unchanged from the earlier handoff
(SHA-256 `7f8b8d17b78d7a0ef2d4e024877e671e695422b69665f3b7155417493de9db86`).
Its original manifest stage was executed using a read-only ZIP path adapter,
with the verification checks unchanged. It streamed and CRC-checked **556,776
files** and rejected the file universe with exit 1:
`FAIL: handoff manifest file universe differs`.

All **23,594** old manifest entries remain present and byte-identical. There
are **533,182** additions absent from that manifest. The old status and root
README still describe four exhausted anchors; these files are retained as
received, not rewritten into a supplied-verifier pass. The adapter was first
checked on the old exact ZIP, where the original manifest stage passed.
Later subprocess stages of the top-level verifier were not run on the new
archive through this adapter.

A full extraction would require 10.02 GB of payload, plus filesystem overhead
(about 12.31 GB with a conservative per-entry allowance), breaking the user's
5 GB reserve. The ZIP adapter and primary auditor therefore read the full
archive directly. Four build files excluded by the top-level manifest rules
are additionally hash-bound directly where required by the run identities.

## Preserved operational failures

The delivered logs retain **168 failed catalogue launches**: arrays 24623136
and 24623228 referenced a nonexistent
`project/q10/Q10_HPC_HANDOFF_PACKAGE/slurm/catalogue_resume.sbatch`.
They are failed launches, not mathematical negative results. The later final
catalogue records for every required shard are complete/exit 0.

The representative-1 job `25031304` also retains one stderr report from a
resource-wrapper arithmetic expression parsing “non-zero status 20”. The
terminal join output chain is separately checked; exit 20 is the solver's
UNSAT convention. This operational error is preserved, not interpreted as an
additional UNSAT result or hidden as empty stderr.
See `audits/nonempty_stderr_summary.json` and the received job logs.
These observed logs do not substitute for a complete cluster accounting export.

## Remaining verification and provenance gaps

1. Update the supplier's manifest and final status to cover the HPC additions
   and the complete 89-representative primary run ledger.
2. Re-establish enumeration completeness and exact join correctness
   independently. Every listed mask now passes fresh geometry/membership
   validation, but the enumerator and global join searches were not rerun.
3. The fresh DRAT/IDRUP certificate replay for the separately proof-certified
   at-least-two-extendible sector is running. Until its full native checker
   and source/transcript binding results are reviewed, no fresh final-sector
   pass is claimed. That proof sector alone does not prove arbitrary-cap
   global Q10 UNSAT.
4. Provide the original source revision, exact compiler environment/submission
   records, and comprehensive scheduler accounting tying every failed attempt
   and retry to the final tasks. Source/input/binary hashes and Slurm/job logs
   are now archived, but do not recover omitted provenance.

## Reproduction and archives

`archive.json` identifies the exact 3,140,960,671-byte ZIP and its 63 ordered release
parts. Concatenate chunks `00` through `62` in numeric order; verify the complete SHA-256
`1ea37d8321c44a018efc37694e21e2d8dacc4870224a540ea14b5609cbc2000e`
before use. `hash_index.json` identifies the compressed complete file index.
Neither the ZIP nor its large candidate/proof bodies belongs in ordinary Git.

All 63 chunks and the compressed file index are uploaded and match their
expected byte sizes and GitHub server SHA-256 digests. The metadata sidecars
and P6 ZIP were also checked: 67/67 release assets match. See
[`UPLOAD_STATUS.md`](UPLOAD_STATUS.md) and
[`audits/remote_asset_verification.json`](audits/remote_asset_verification.json).
The complete archive hash was verified on the downloaded source and local
ordered reassembly; a second full remote download was not performed.

The retrieval helper streams the ordered release chunks into a single ZIP,
checks every chunk and the complete archive hash, and keeps at least 5 GB
free. It creates no separate local chunk copies. Use an empty destination;
an interrupted or rejected transfer retains a `.partial` file.

```sh
python3 g11/Q/evidence/Q10/scripts/fetch_archive.py \
  /path/to/Q10_HPC_HANDOFF_PACKAGE.zip
python3 g11/Q/evidence/Q10/scripts/run_zip_manifest_verifier.py \
  Q10_HPC_HANDOFF_PACKAGE.zip Q10_FILE_INDEX.jsonl \
  --expected-verifier-sha256 7f8b8d17b78d7a0ef2d4e024877e671e695422b69665f3b7155417493de9db86
# Above: expected supplied-manifest rejection, with full file index retained.
python3 g11/Q/evidence/Q10/scripts/audit_hpc_zip.py \
  Q10_HPC_HANDOFF_PACKAGE.zip Q10_FILE_INDEX.jsonl /tmp/q10-audit
```

The primary result and the verification limitations must be cited together.
