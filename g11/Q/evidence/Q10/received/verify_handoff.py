#!/usr/bin/env python3
"""Relocatable non-searching integrity audit for the Q10 collaborator handoff."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_REP_HASH = "234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def manifest_audit() -> int:
    manifest = ROOT / "HANDOFF_SHA256SUMS"
    require(manifest.is_file(), "missing HANDOFF_SHA256SUMS")
    rows = [line.split(maxsplit=1) for line in manifest.read_text().splitlines() if line]
    require(rows and all(len(row) == 2 for row in rows), "malformed handoff manifest")
    expected = {name.removeprefix("*").removeprefix("./"): checksum for checksum, name in rows}
    actual: dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"FAIL: symlink forbidden in handoff: {path.relative_to(ROOT)}")
        if path.is_file() and path.name != "HANDOFF_SHA256SUMS" and not path.is_relative_to(ROOT / "build"):
            actual[str(path.relative_to(ROOT))] = digest(path)
    require(set(expected) == set(actual), "handoff manifest file universe differs")
    for name, checksum in expected.items():
        require(actual[name] == checksum, f"handoff manifest hash mismatch: {name}")
    print(f"HANDOFF_MANIFEST_PASS files={len(actual)}")
    return len(actual)


def execute(label: str, command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(f"FAIL: {label} exited {completed.returncode}")
    last = next((line for line in reversed(completed.stdout.splitlines()) if line.strip()), "PASS")
    print(f"{label}_PASS last={last[:180]}")


def archive_parts_audit() -> None:
    parts_dir = ROOT / "archives/cloud_upload_parts"
    expected = {
        "Q10_CLOUD_CORE_SOURCE_20260803.tar.gz.part_aaa": "cec9f1e5178c4a684721ae5f897cc552cea49a8f7f0fd48ffa7adc685ae498b8",
        "Q10_CLOUD_PROOF_SOURCE_20260803.tar.gz.part_aaa": "5580783b3b3be4455b49b7168308eee304c96ef6b45ff783ed648426ebac091f",
        "Q10_CLOUD_PROOF_SOURCE_20260803.tar.gz.part_aab": "1b936f6f0bbf8a5e08984005c3408237a6740fb7fce6bdb1594d1c0c91bf6ad1",
    }
    for name, checksum in expected.items():
        require(digest(parts_dir / name) == checksum, f"archive part hash mismatch: {name}")
    print("CLOUD_ARCHIVE_PARTS_PASS parts=3 core_sha256=cec9f1e5178c4a684721ae5f897cc552cea49a8f7f0fd48ffa7adc685ae498b8 proof_sha256=b45b65ec91e1f56a7c527d65e012a26901a1ea94cd45b632eb9b6f4323cf6c87")


def main() -> None:
    manifest_audit()
    status = json.loads((ROOT / "provenance/AUTHORITATIVE_STATUS_20260803.json").read_text())
    require(status["global_mathematical_status"] == "INCOMPLETE", "global status is not INCOMPLETE")
    require(status["exhausted_representative_indices_zero_based"] == [17, 53, 76, 88], "wrong exhausted representative index list")
    require(len(status["remaining_representative_indices_zero_based"]) == 85, "wrong remaining representative count")
    reps = ROOT / "work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex"
    values = [line.strip() for line in reps.read_text().splitlines() if line.strip()]
    require(len(values) == 89 and len(set(values)) == 89, "frozen representative coverage is not 89 unique masks")
    require(digest(reps) == EXPECTED_REP_HASH, "frozen representative hash mismatch")
    print("STATUS_AND_INPUTS_PASS global=INCOMPLETE representatives=89 exhausted=4 remaining=85")
    archive_parts_audit()
    with tempfile.TemporaryDirectory(prefix="q10-handoff-audit-") as temporary:
        tmp = Path(temporary)
        execute("PAIR_PROOF_BUNDLE", [sys.executable,
                "work/package_agent/pair_proofs/audit_pair_proof_bundle.py",
                "--json", str(tmp / "pair_proof_audit.json")])
        execute("FIXED_ANCHOR_RESULTS", [sys.executable,
                "work/math_agent/nonextendible_structure/audit_exhausted_representatives.py",
                "--root", str(ROOT), "--json", str(tmp / "fixed_anchor_audit.json")])
        execute("REP1_3025_SHARD_CATALOGUE", [sys.executable,
                "work/solver_agent/audit_cap20_shards.py",
                "--shards", "work/solver_agent/cap20_rep1_runner_v1/shards",
                "--log", "work/solver_agent/cap20_rep1_runner_v1/shards.log",
                "--catalogue", "work/solver_agent/cap20_rep1_runner_v1/all_masks.hex",
                "--json", str(tmp / "rep1_shard_audit.json")])
    for script in (ROOT / "tools/build_linux.sh", ROOT / "slurm/catalogue_resume.sbatch", ROOT / "slurm/join_55way.sbatch"):
        execute(f"SHELL_SYNTAX_{script.name}", ["bash", "-n", str(script)])
    print("Q10_HANDOFF_VERIFICATION_PASS global_status=INCOMPLETE proof_sector=PASS fixed_anchors=4 rep1_catalogue=3025_of_3025")


if __name__ == "__main__":
    main()
