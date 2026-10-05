# Linux build, verification, and HPC continuation

Run all commands from the handoff root.  Required baseline: Linux, Python 3.9+
and a C++20 compiler.  The proof replay needs `drat-trim`, CaDiCaL, and
Idrup-Check; preserved source and the recorded macOS binaries are included, but
a Linux collaborator should rebuild the checkers locally and record their
hashes.

## Fast integrity audit

```sh
python3 verify_handoff.py
```

This is the required first step.  It does not redo any expensive computation.

## Build the production route

```sh
./tools/build_linux.sh
```

This writes `build/linux/q10_cap20_enum`, `q10_cap20_catalogue_audit`, and
`capset_join`.  Build products are intentionally outside the frozen evidence.

## Resume or start a complete 3,025-shard catalogue

Choose one unexhausted zero-based representative index.  The runner's
`RUN_DIR` is the checkpoint: retain it on durable shared storage and rerun the
same command to validate/reuse completed shard records.  Do not change the
anchor, source/binary, cap file, or time-per-shard within a run directory.

```sh
REP=1
ANCHOR=$(sed -n "$((REP + 1))p" work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex)
RUN_DIR=/path/to/durable/q10/rep${REP}_catalogue
python3 work/solver_agent/run_cap20_catalogue.py \
  --run-dir "$RUN_DIR" --anchor "$ANCHOR" \
  --generator build/linux/q10_cap20_enum \
  --generator-source work/solver_agent/q10_cap20_enum.cpp \
  --caps work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_diag.hex \
  --auditor build/linux/q10_cap20_catalogue_audit \
  --summarizer work/solver_agent/summarize_cap20.py \
  --shard-auditor work/solver_agent/audit_cap20_shards.py \
  --jobs 16 --time-per-shard 1200
```

Only `COMPLETE_AUDITED` after all 3,025 records and both audits is terminal.
An `INCOMPLETE` result is a checkpoint, not a mathematical statement.

## Run the exact 55-way four-cap join

After a catalogue is `COMPLETE_AUDITED`, use its `all_masks.hex` and a new
output directory.  All 55 files must complete before audit.

```sh
work/math_agent/nonextendible_structure/run_capset_join_shards.sh \
  "$ANCHOR" "$RUN_DIR/all_masks.hex" /path/to/durable/q10/rep${REP}_join 16 1200
python3 work/math_agent/nonextendible_structure/audit_join_shards.py \
  --directory /path/to/durable/q10/rep${REP}_join \
  --caps "$RUN_DIR/all_masks.hex" \
  --binary build/linux/capset_join
```

Only an audit `PASS` with 55 `COMPLETE_NO_WITNESS` shards establishes
anchor-local UNSAT.  A witness must be independently checked before claiming
SAT.

## Certified proof replay

Fast hash/coverage binding (seconds to minutes, depending on storage):

```sh
python3 work/package_agent/pair_proofs/audit_pair_proof_bundle.py
```

Replay all 88 DRAT certificates (recorded aggregate checker time about 23 min):

```sh
python3 work/package_agent/pair_proofs/certify_ordinary_drat.py \
  --cnf-dir work/root/pair_selectors \
  --output-dir work/package_agent/pair_proofs/drat_pilots \
  --cadical /path/to/cadical --drat-trim /path/to/drat-trim --skip 1
```

Replay representative-1 IDRUP (recorded wall time about 36 min):

```sh
/path/to/idrup-check work/package_agent/pair_proofs/rep1_full.icnf \
  work/package_agent/pair_proofs/rep1_full.idrup
```

Expected terminal text is `s VERIFIED`, exit 0.  The proof verifier is a replay
operation, not a new Q10 search.

## Slurm templates

`slurm/catalogue_resume.sbatch` compiles if needed and runs/resumes one complete
catalogue allocation. `slurm/join_55way.sbatch` runs/resumes the 55-way join.
Set the indicated environment variables and copy this handoff to shared storage
before submission.  These templates intentionally use one node per anchor to
preserve the production runner's immutable checkpoint protocol.

## Original split archives

For provenance delivery, `archives/cloud_upload_parts/REASSEMBLE_AND_VERIFY_20260803.sh`
reconstructs the original 236,803,747-byte core archive and 664,846,308-byte
proof archive.  Its documented SHA-256 values are verified by
`verify_handoff.py`; reassembly is not required to use this curated package.
