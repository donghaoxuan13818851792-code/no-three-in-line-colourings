#!/usr/bin/env python3
"""Relocatable, non-searching integrity audit for the P6 research handoff."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()

def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(f'FAIL: {message}')

def execute(label: str, command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    if completed.returncode:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(f'FAIL: {label} exited {completed.returncode}')
    line = next((x for x in reversed(completed.stdout.splitlines()) if x.strip()), 'PASS')
    print(f'{label}_PASS last={line[:180]}')

def manifest_audit() -> int:
    manifest = ROOT / 'HANDOFF_SHA256SUMS'
    require(manifest.is_file(), 'missing HANDOFF_SHA256SUMS')
    expected = {}
    for line in manifest.read_text().splitlines():
        checksum, name = line.split(maxsplit=1)
        expected[name.removeprefix('*').removeprefix('./')] = checksum
    actual = {}
    for path in ROOT.rglob('*'):
        if path.is_symlink():
            raise SystemExit(f'FAIL: symlink forbidden: {path.relative_to(ROOT)}')
        if path.is_file() and path.name != 'HANDOFF_SHA256SUMS' and not path.is_relative_to(ROOT / 'build'):
            actual[path.relative_to(ROOT).as_posix()] = sha256(path)
    require(set(actual) == set(expected), 'top-level manifest file universe differs')
    for name, checksum in expected.items():
        require(actual[name] == checksum, f'top-level hash mismatch: {name}')
    print(f'HANDOFF_MANIFEST_PASS files={len(actual)}')
    return len(actual)

def main() -> None:
    manifest_audit()
    status = json.loads((ROOT / 'provenance/AUTHORITATIVE_FROZEN_STATUS.json').read_text())
    require(status['p6_status'] == 'PARTIAL_TERMINAL_PROGRESS', 'wrong P6 status')
    require(status['terminal_unsat_regression_cases'] == 26, 'wrong terminal case count')
    require(status['retained_canonical_pairs'] == 266771874, 'wrong retained outer count')
    print('STATUS_PASS global=PARTIAL_TERMINAL_PROGRESS terminal_pairs=26 retained_outer_pairs=266771874')
    execute('ULTRA_FROZEN', [sys.executable, 'ultra_frozen/scripts/verify_ultra_package.py', 'ultra_frozen'])
    artifact = ROOT / 'authoritative_core/prior_results/agent1_residual_architecture'
    execute('AGENT1_ARTIFACT', [sys.executable, str(artifact / 'scripts/verify_agent1_artifact.py'), str(artifact)])
    expected = artifact / 'inputs/p6_terminal_26_expected_ids.txt'
    ledger = artifact / 'baseline_reference/results/p6_terminal_26.tsv'
    execute('TERMINAL26_LEDGER', [sys.executable, str(artifact / 'baseline_reference/scripts/validate_terminal_ledger.py'),
            '--expected', str(expected), '--ledger', str(ledger), '--root', str(artifact)])
    rows = list(csv.DictReader(ledger.open(), delimiter='\t'))
    require(len(rows) == 26 and all(row['status'] == 'UNSAT_P6_RESIDUAL' and row['exit_code'] == '20' for row in rows), 'terminal ledger is not 26 UNSAT records')
    branch = ROOT / 'authoritative_core/benchmarks/family_branches/historical_fixed_A_10787/fixed_first_after_q89_maximality.tsv'
    require(sum(1 for _ in branch.open()) == 10788, 'fixed-first branch ledger is not 10,787 records plus header')
    print('FIXED_BRANCH_LEDGER_PASS retained_records=10787')
    for script in (ROOT / 'tools/build_linux.sh',):
        execute(f'SHELL_SYNTAX_{script.name}', ['bash', '-n', str(script)])
    print('P6_HANDOFF_VERIFICATION_PASS global_status=PARTIAL_TERMINAL_PROGRESS terminal_pairs=26 fixed_branch_remaining=10787 outer_retained=266771874')

if __name__ == '__main__':
    main()
