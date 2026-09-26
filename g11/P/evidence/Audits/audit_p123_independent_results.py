#!/usr/bin/env python3
"""Audit the independently re-enumerated P123 shards and residual streams."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "work/independent_agent"
SAT = ROOT / "work/sat_agent"
FULL = (1 << 121) - 1

INDEPENDENT = re.compile(
    r"INDEPENDENT_UNSAT123_SHARD (?P<shard>\d+) 6"
    r" first_caps (?P<first>\d+)"
    r" examined2 (?P<t2>\d+) accepted2 (?P<p2>\d+)"
    r" examined3 (?P<t3>\d+) accepted3 (?P<p3>\d+)"
    r" examined4 (?P<t4>\d+) accepted4 (?P<p4>\d+)"
    r" residual_instances (?P<instances>\d+)"
    r" residual_nodes (?P<nodes>\d+)"
    r" residual_conflicts (?P<conflicts>\d+)"
    r" residual_sat (?P<sat>\d+)\n?"
)
PRIMARY = re.compile(
    r"UNSAT123_SHARD (?P<shard>\d+) 6 first_caps (?P<first>\d+)"
    r" tested2 (?P<t2>\d+) passed2 (?P<p2>\d+)"
    r" tested3 (?P<t3>\d+) passed3 (?P<p3>\d+)"
    r" tested4 (?P<t4>\d+) passed4 (?P<p4>\d+)"
    r" residual_instances (?P<instances>\d+)"
    r" residual_nodes (?P<nodes>\d+)"
    r" residual_conflicts (?P<conflicts>\d+)"
    r" residual_sat (?P<sat>\d+)\n?"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def parsed(path: Path, pattern: re.Pattern[str]) -> dict[str, int]:
    text = path.read_text(encoding="ascii")
    assert "SOLUTION" not in text
    match = pattern.fullmatch(text)
    assert match, (path, text)
    return {key: int(value) for key, value in match.groupdict().items()}


def main() -> None:
    total_residuals = 0
    for shard in range(6):
        stem = HERE / f"p123_independent_full_shard{shard}"
        assert stem.with_suffix(".status").read_text(
            encoding="ascii").strip() == "20"
        independent = parsed(stem.with_suffix(".out"), INDEPENDENT)
        primary = parsed(
            SAT / f"p123_full_shard{shard}.out", PRIMARY)
        for key in (
            "shard", "first", "t2", "p2", "t3", "p3", "t4", "p4",
            "instances", "sat",
        ):
            assert independent[key] == primary[key], (
                shard, key, independent[key], primary[key])
        assert independent["sat"] == 0
        residual_path = HERE / (
            f"p123_independent_full_shard{shard}.residuals.hex")
        residual_count = 0
        with residual_path.open("r", encoding="ascii") as source:
            for line_number, line in enumerate(source, 1):
                text = line.rstrip("\n")
                assert len(text) == 31
                mask = int(text, 16)
                assert not mask & ~FULL
                assert mask.bit_count() == 37, (
                    residual_path, line_number)
                residual_count += 1
        assert residual_count == independent["instances"]
        total_residuals += residual_count
        print(
            f"shard {shard}",
            f"residuals={residual_count}",
            f"stream_sha256={sha256(residual_path)}",
            f"out_sha256={sha256(stem.with_suffix('.out'))}",
            f"log_sha256={sha256(stem.with_suffix('.log'))}",
            f"status_sha256={sha256(stem.with_suffix('.status'))}",
        )
    assert total_residuals == 708638
    print(
        "INDEPENDENT_P123_VERIFIED",
        f"residuals={total_residuals}",
    )


if __name__ == "__main__":
    main()
