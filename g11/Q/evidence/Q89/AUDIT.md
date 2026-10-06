# Q8/Q9 archived evidence audit — 6 October 2026

The complete existing Q8/Q9 ZIP was located in the P6 package's frozen dependency
archives. Its 519 manifested payload files all match, with no missing, extra
or changed file. Public server archive size and SHA-256 also match `archive.json`.

The unchanged original strict terminal auditor passes for all five Q8 workers
and four Q9 workers. Both profiles cover all 89 anchors and 412,995 prefixes,
with 37,232,526 binary instances each and complete UNSAT records.
Q8/Q9 are independent of one another in this audit; their separately declared
dominance dependencies remain the ones recorded in the original package.

Fresh prefix-universe reconstruction independently scans all 89 anchors and
1,019,640 size-21 catalogue members, reconstructs the 412,995-row prefix ledger
byte-for-byte, and checks its geometry. Fresh binary/profile logic audits pass.
The large terminal searches were not rerun.

The first path adapter failed on Python 3.14 construction before mathematical
checking. The successful retry uses import-local path adaptation with the
original historical command strings preserved. Both attempts are retained;
the received strict auditor was not edited.

After downloading/hash-checking and extracting the original ZIP:

```sh
python3 scripts/audit_zip_manifest.py g11_q89_complete_elimination.zip g11_q89_complete_elimination/SHA256SUMS /path/to/manifest-audit.json
python3 scripts/run_relocated_audit.py --package /path/to/g11_q89_complete_elimination --historical-root /Users/donghaoxuan/Documents/Codex/2026-07-20/consider-the-11-11-integer-grid --script q89_exact_9way_20260723_0130/audit_final.py
python3 /path/to/g11_q89_complete_elimination/scripts/audit_prefix_universe.py
python3 /path/to/g11_q89_complete_elimination/q89_exact_development_20260722/audit_binary_logic.py
python3 /path/to/g11_q89_complete_elimination/q89_exact_development_20260722/audit_profile_logic.py
```
