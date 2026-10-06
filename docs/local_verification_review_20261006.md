# Post-campaign review — 6 October 2026

Reviewed baseline: `b409c1c45767e1332aec3d9eda0992e4ba1035fe`, already on
remote main. Its completed evidence did not await a merge.

## Evidence review

- The SHA inventory covers every tracked file except itself. Local artifact
  byte sizes/hashes and unique artifact IDs pass.
- All JSON evidence parses and verification script syntax passes.
- P123 audit-only replay passes all 60 genuine output/exit/stream records,
  127,491 anchors, 708,638 residuals and grouped primary counters. No search
  is launched by that review.
- All five current release sizes/server SHA-256 digests match committed
  records. The final receipt archive and all 214 member hashes pass review.
- Sector proofs remain separate from global Q10. Original interruptions stay
  visible; incomplete P4/P5, P6, P7 and missing R1 proof bodies are not promoted.

The completed native evidence passed review. One remaining process-control
defect was found and corrected.

## Process-control correction

Previously `terminate_job` escalated to SIGKILL only if waiting for the group
leader timed out. A leader can exit on SIGTERM while a native child ignores
SIGTERM and keeps running. The real-process regression reproduces this on
the baseline and fails as expected. Cleanup now escalates for any remaining
process group even after the leader has exited.

Follow-up ownership also handles `BaseException`: KeyboardInterrupt cleans
up the native job without creating a fake terminal exit. Two real nested
process regressions pass: early leader exit with a signal-ignoring child,
and interrupted follow-up cleanup without a fabricated status. They run no
mathematical search.

```sh
python3 -m unittest discover -s tests -p test_local_campaign_process_cleanup.py -v
```

No frozen solver/checker source, received material or completed receipt was
modified. Archived executed versions remain intact.

## Older open PR

[PR #3](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/pull/3)
is an older September proposal. Its description promotes Q10 to complete
repository evidence status, conflicting with the global/sector boundary now
established. It must not overwrite current main's
`INDEPENDENT_VERIFICATION_PENDING`. This review does not merge that proposal
or authenticate its additional historical records.

The reviewed evidence and process-control correction can remain on main with
conservative mathematical statuses. Further material-dependent checks are
listed in `supplier_materials_needed_20261006.md`.
