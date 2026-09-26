# Desktop handoff verification record

This record was made from this handoff directory without launching a Q10
catalogue enumeration, four-cap join, or new SAT search.

## Passed checks

- `python3 verify_handoff.py`: passed the top-level manifest, frozen input
  hash, 89-representative coverage, `GLOBAL STATUS: INCOMPLETE` boundary,
  cloud-part hashes, complete pair-proof-bundle binding audit, fixed-anchor
  audit for 17/53/76/88, complete rep1 3,025-shard union audit, and shell
  syntax checks for the Linux/Slurm entry points.
- `tools/build_linux.sh`: built all three C++20 production binaries in
  `build/linux/` from this directory's sources.
- `work/package_agent/pair_proofs/MANIFEST.sha256`: all 1,044 listed proof
  bundle files passed SHA-256 verification.
- The supplied Idrup-Check binary checked the included tiny strict fixture with
  exit 0 and zero UNKNOWN conclusions.
- The original split cloud core/proof archives were streamed from their parts:
  each reconstructed logical SHA-256 matched, and each stream passed `gzip -t`
  and `tar -tzf -` without materializing another large archive.

## Deliberately not rerun

The full 88 DRAT replay and full rep1 IDRUP replay were not repeated during this
handoff check.  They are not searches, but their recorded checker times are
about 23 and 36 minutes respectively.  The package includes all proofs,
checkers, replay commands, terminal logs, and a full proof-file manifest; the
fast pair-proof audit rehashed/bound all of them.  A receiving collaborator may
run the full replay commands in `BUILD_AND_RUN_HPC.md` before publication.

This limitation does not change the package's explicit mathematical status:
**Q10 GLOBAL STATUS: INCOMPLETE.**
