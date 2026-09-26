#!/usr/bin/env python3
"""Validate the imported independent P1-P3 run and frozen inputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


P_ROOT = Path(__file__).resolve().parents[2]
RUN = P_ROOT / "evidence/P123Independent/run_20260926T032326Z"
EXPECTED_INPUTS = {
    "p123_independent_verifier.cpp": "fead71b869a063e8947ce7c0cf1af461eff2c720b34b9b774df33929fadffb78",
    "p1_independent_search.cpp": "825b3a3d6e8d8c926d8a14c8725175188ab8b0e6d8b0c97e7e4916b2e45da1e8",
    "p123_independent_verifier": "117e2e5f4de9ec4ba8b575678317d9dbb18e354f771fcdbeb511e19a3b044180",
    "caps21_r0_diag.hex": "c4ba6b9aa11f4b9b7d1f7c2cd74eada8b727c40851c57e25a553142c4e12df3e",
    "caps21_r1_diag.hex": "62d025e2de26afe788057cc1a4525302d8a56c1be8ae4baf3d6d129f115b3895",
    "caps21_r2_diag.hex": "14f89035771e3428d0d6465d02ebea8430fb101cd0d6e3c972a8e98062d180e5",
    "caps21_r3_diag.hex": "92f7ea6aec073e2b335e089a56634f08ba34d1dab18e6b3c3935b70c2a157b42",
    "caps21_r4_diag.hex": "b1df4d6c48aeaad56d674b688e9398d05ef529409a9f4502fac212a7f4f78060",
    "caps21_r5_diag.hex": "47d59957a0f5f3d83298041cf4d8a3f99c5f5dc5211524c42e74235ea2561f9e",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    rows = list(csv.DictReader((RUN / "run_manifest.tsv").open(), delimiter="\t"))
    assert len(rows) == 6
    repeated: Counter[str] = Counter()
    total_instances = 0
    for expected_shard, row in enumerate(rows):
        assert int(row["shard"]) == expected_shard
        assert int(row["exit_code"]) == 20
        assert int(row["residual_sat"]) == 0
        stem = RUN / "work/independent_agent" / f"p123_independent_full_shard{expected_shard}"
        for extension, column in (
            ("out", "out_sha256"),
            ("log", "log_sha256"),
            ("status", "status_sha256"),
            ("residuals.hex", "residuals_sha256"),
            ("command", "command_sha256"),
        ):
            path = Path(f"{stem}.{extension}")
            assert path.is_file(), path
            assert row[column] == sha256(path), (path, row[column], sha256(path))
        residual_path = Path(f"{stem}.residuals.hex")
        count = 0
        with residual_path.open("r", encoding="ascii") as stream:
            for line_number, line in enumerate(stream, 1):
                text = line.rstrip("\n")
                assert len(text) == 31, (residual_path, line_number)
                value = int(text, 16)
                assert value.bit_count() == 37, (residual_path, line_number)
                repeated[text] += 1
                count += 1
        assert count == int(row["residual_instances"])
        total_instances += count

    inputs = list(csv.DictReader((RUN / "source_inputs.tsv").open(), delimiter="\t"))
    assert {row["artifact"] for row in inputs} == set(EXPECTED_INPUTS)
    for row in inputs:
        artifact = row["artifact"]
        if artifact.startswith("caps21_"):
            path = P_ROOT / "work/math_agent" / artifact
        elif artifact == "p123_independent_verifier":
            path = P_ROOT / "work/independent_agent/p123_verifier_build" / artifact
        elif artifact == "p123_cap_packing_manifest.tsv":
            path = P_ROOT / "work/sat_agent" / artifact
        else:
            path = P_ROOT / "work/independent_agent" / artifact
        assert path.is_file(), path
        assert int(row["bytes"]) == path.stat().st_size
        assert row["sha256"] == sha256(path) == EXPECTED_INPUTS[artifact], artifact

    # Run the archived result auditor in an isolated mirror so no work-tree
    # files need to be overwritten to satisfy its historical relative paths.
    with tempfile.TemporaryDirectory(prefix="p123-import-audit-") as temporary:
        shadow = Path(temporary) / "g11/P"
        (shadow / "evidence/Audits").mkdir(parents=True)
        (shadow / "work").mkdir()
        (shadow / "work/independent_agent").symlink_to(
            RUN / "work/independent_agent", target_is_directory=True)
        (shadow / "work/sat_agent").symlink_to(
            P_ROOT / "work/sat_agent", target_is_directory=True)
        auditor = P_ROOT / "evidence/Audits/audit_p123_independent_results.py"
        copied_auditor = shadow / "evidence/Audits/audit_p123_independent_results.py"
        shutil.copy2(auditor, copied_auditor)
        completed = subprocess.run(
            [sys.executable, str(copied_auditor)], cwd=shadow,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False)
        assert completed.returncode == 0, completed.stdout
        assert "INDEPENDENT_P123_VERIFIED residuals=708638" in completed.stdout

    result = {
        "status": "PASS",
        "shards": len(rows),
        "first_caps": sum(int(row["first_caps"]) for row in rows),
        "residual_instances": total_instances,
        "residual_sat": sum(int(row["residual_sat"]) for row in rows),
        "audited_unique_mask_encodings": len(repeated),
        "repeated_mask_occurrences": total_instances - len(repeated),
        "interpretation": "Residuals are checked and counted as instances. A repeated mask encoding may occur in distinct residual instances.",
        "existing_auditor": completed.stdout.strip(),
        "frozen_input_hashes": "PASS",
        "run_manifest_hashes": "PASS",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n")
    print(rendered)


if __name__ == "__main__":
    main()
