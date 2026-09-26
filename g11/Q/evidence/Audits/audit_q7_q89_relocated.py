#!/usr/bin/env python3
"""Run the frozen Q7 and Q8/Q9 package audits after relocating their archives.

The Q7/Q89 package-level verifiers accept relocation, while their historical
strict audit_final.py scripts compare a saved absolute command string.  This
wrapper runs the relocation-aware package verifiers and records that exact
strict-audit diagnostic without changing any archived package member.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def run(label: str, command: list[str], cwd: Path) -> tuple[str, int]:
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    output = result.stdout.strip()
    if result.returncode:
        raise SystemExit(f"{label} failed (exit {result.returncode}):\n{output}")
    return output, result.returncode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q7-root", type=Path, required=True,
                        help="extracted Q7_FINAL_VERIFICATION_PACKAGE directory")
    parser.add_argument("--q89-root", type=Path, required=True,
                        help="extracted g11_q89_complete_elimination directory")
    parser.add_argument("--report", type=Path,
                        help="optional path for a JSON audit summary")
    args = parser.parse_args()
    q7 = args.q7_root.resolve()
    q89 = args.q89_root.resolve()
    if not (q7 / "verify_package.py").is_file():
        raise SystemExit(f"missing Q7 verify_package.py under {q7}")
    if not (q89 / "scripts/audit_q89.py").is_file():
        raise SystemExit(f"missing Q89 scripts/audit_q89.py under {q89}")

    q7_output, _ = run("Q7_PACKAGE_VERIFICATION",
                       [sys.executable, str(q7 / "verify_package.py")], q7)
    if not re.search(r"Q7_PACKAGE_VERIFICATION PASS files=151 workers=9 coverage=\[0,1325039\)", q7_output):
        raise SystemExit(f"unexpected Q7 package-audit summary:\n{q7_output}")
    q7_strict = q7 / "q7_exact_9way_20260722_2130/audit_final.py"
    strict_q7 = subprocess.run([sys.executable, str(q7_strict)], cwd=q7,
                               text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, check=False)
    q7_diag = strict_q7.stdout.strip()
    expected_q7 = "Q7_FINAL_AUDIT FAIL: w00 executed-command record mismatch"
    if strict_q7.returncode == 0 or q7_diag != expected_q7:
        raise SystemExit(f"unexpected strict Q7 audit result ({strict_q7.returncode}):\n{q7_diag}")

    q89_audit, _ = run("Q89_FINAL_AUDIT",
                       [sys.executable, str(q89 / "scripts/audit_q89.py")], q89)
    if "Q89_FINAL_AUDIT PASS workers=9 profiles=Q8,Q9 status=UNSAT" not in q89_audit:
        raise SystemExit(f"unexpected Q89 package-audit summary:\n{q89_audit}")
    q89_universe, _ = run("Q89_PREFIX_UNIVERSE_AUDIT",
                          [sys.executable, str(q89 / "scripts/audit_prefix_universe.py")], q89)
    if not re.search(r"Q89_PREFIX_UNIVERSE_AUDIT PASS rows=412995 fixed=89 caps21=1019640 lines=628 triples=6992 active_lines=32 ledger_sha256=[0-9a-f]{64}", q89_universe):
        raise SystemExit(f"unexpected Q89 prefix-universe summary:\n{q89_universe}")
    q89_strict = q89 / "q89_exact_9way_20260723_0130/audit_final.py"
    strict_q89 = subprocess.run([sys.executable, str(q89_strict)], cwd=q89,
                                text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False)
    q89_diag = strict_q89.stdout.strip()
    expected_q89 = "Q89_FINAL_AUDIT FAIL: executed command mismatch for q8w0"
    if strict_q89.returncode == 0 or q89_diag != expected_q89:
        raise SystemExit(f"unexpected strict Q89 audit result ({strict_q89.returncode}):\n{q89_diag}")

    report = {
        "status": "PASS",
        "relocation_mode": True,
        "q7": {
            "package_audit": q7_output,
            "strict_audit_diagnostic": q7_diag,
            "strict_diagnostic_class": "historical absolute executed-command mismatch after relocation",
            "terminal_scope": "9 workers, [0,1325039) complete coverage; package verifier checked hashes, terminal exit/status, SAT/UNKNOWN/INCOMPLETE exclusions and independent ledgers",
        },
        "q89": {
            "package_audit": q89_audit,
            "prefix_universe_audit": q89_universe,
            "strict_audit_diagnostic": q89_diag,
            "strict_diagnostic_class": "historical absolute executed-command mismatch after relocation",
            "terminal_scope": "Q8 five workers plus Q9 four workers; exact fixed coverage and the shared 412995-row prefix universe verified",
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
