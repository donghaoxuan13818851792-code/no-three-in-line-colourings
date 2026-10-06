# Q7 archived evidence audit — 6 October 2026

The exact original Q7 ZIP has 151 manifested payload files. Every listed hash,
the complete file universe and the public server's archive size/SHA-256 match.
Its immutable retrieval metadata is in `archive.json`.

The unchanged strict terminal auditor passes with nine workers and exact
prefix coverage `[0,1325039)`, zero dominance rejections, 13,366,857 terminal
two-colour instances, and complete UNSAT termination records. Historical
commands are compared against their original absolute paths; only filesystem
reads are relocated by `scripts/run_relocated_audit.py`.

The first adapter attempt failed before mathematical checking because a global
`pathlib.Path` replacement conflicted with Python 3.14 constructors. Both that
failure and the successful retry are retained. The corrected adapter supplies
the path class only to the audit's import namespace. The received audit source
hash and every original predicate remain unchanged.

Fresh `audit_prefix_ledger.py` and `audit_binary_logic.py` checks also pass.
This audits the complete recorded execution and reconstructs the prefix/Boolean
checks; it does not rerun the expensive Q7 search.

Download/hash-check and extract the original archive. From this repository:

```sh
python3 scripts/audit_zip_manifest.py Q7_FINAL_VERIFICATION_PACKAGE.zip Q7_FINAL_VERIFICATION_PACKAGE/PACKAGE_SHA256SUMS /path/to/manifest-audit.json
python3 scripts/run_relocated_audit.py --package /path/to/Q7_FINAL_VERIFICATION_PACKAGE --historical-root /Users/donghaoxuan/Documents/Codex/2026-07-20/consider-the-11-11-integer-grid --script q7_exact_9way_20260722_2130/audit_final.py
python3 /path/to/Q7_FINAL_VERIFICATION_PACKAGE/q7_exact_9way_20260722_2130/audit_prefix_ledger.py
python3 /path/to/Q7_FINAL_VERIFICATION_PACKAGE/q7_exact_9way_20260722_2130/audit_binary_logic.py
```

The strict auditor's existing binary/disassembly, source/input, command, PID,
terminal, time, snapshot and coverage checks are all retained.
