# R branch metadata

This file keeps execution metadata separate from the repository-wide artifact TSV.

## Data formats

The imported certificate package uses:

- caps and cap pairs: hexadecimal bit masks with bit `11*x+y` for zero-based coordinates;
- terminal leaves: DIMACS CNF;
- solver reports: JSON plus Kissat stdout;
- proof bodies: zstd-compressed DRAT;
- proof-verification reports: JSON;
- hashes: SHA-256.

## Verification chain

For each R1 leaf, the recorded chain is:

```text
Kissat (UNSAT, exit code 20)
    ↓
DRAT proof
    ↓
drat-trim with LRAT output
    ↓
lrat-check
```

Temporary LRAT files were deleted after successful checking and are not part of the archived proof-body collection.

## Recorded verification tools

From the authoritative final ledger summary:

- drat-trim SHA-256: `64225379fcc22b847746f585c195ff2bdb9c5c67ba936c836dd60738ff62ff65`
- drat-trim source commit: `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`
- lrat-check SHA-256: `7c2164f4da22c37a8b983b121441c31f7da8d88e3912363f5cff2417a94ab75e`
- verification driver SHA-256: `54b2220be65156d2c991b5dda128193be658a84fafb06ade86f9ada83b1a8266`
- zstd SHA-256: `aff8169fb421bb925fb16c44a7e0143fa2c7a941dc45cce76b15062a2ce54917`
- recorded verification workers: `4`

Hardware and OS details not present in the authoritative ledger are intentionally not inferred here.

## Reproduction commands recorded by package 0.1.1

Commands are relative to the certificate-package root:

```bash
scripts/audit_coverage.sh
scripts/verify_package.sh
WORKERS=2 scripts/verify_all_leaves.sh
```

Their documented roles are:

- `audit_coverage.sh`: independent 676 / 2138 / 930 / 119 / 11 / 1309 coverage audit;
- `verify_package.sh`: read-only manifest/count audit plus representative proof replay;
- `verify_all_leaves.sh`: full resumable replay of all 1,309 proof chains.

The source programs themselves will be imported or linked by immutable archive hash before R is promoted to repository status `COMPLETE`.
