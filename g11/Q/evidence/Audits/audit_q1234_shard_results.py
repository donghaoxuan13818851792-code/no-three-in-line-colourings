#!/usr/bin/env python3
"""Strictly audit and hash the six completed Q1--Q4 packing shards."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
PREFIX = ROOT / "work/sat_agent/q1234_full_shard"
SOURCE = ROOT / "work/sat_agent/q1234_cap_packing.cpp"
BINARY = ROOT / "work/sat_agent/q1234_cap_packing"
SOURCE_SHA256 = (
    "2227dba3f45b344abd38e445b9636ecaa6f30258ae68f9c7e992029c990e2fa7"
)
BINARY_SHA256 = (
    "b01bf5f9b036f0ecea138fb239918fa8cc46a7fa26a5e2a36ed2ca9a30487457"
)
KEYS = (
    "fixed_processed",
    "tested1", "passed1",
    "tested2", "passed2",
    "tested3", "passed3",
    "residual_instances", "residual_nodes",
    "residual_conflicts", "residual_sat",
)
PROGRESS_KEYS = (
    "tested1", "passed1",
    "tested2", "passed2",
    "tested3", "passed3",
    "residual_instances", "residual_nodes", "residual_sat",
)
EXPECTED_AGGREGATE = {
    "fixed_processed": 89,
    "tested1": 1_000_619,
    "passed1": 412_995,
    "tested2": 7_470_942,
    "passed2": 1_325_039,
    "tested3": 10_929,
    "passed3": 670,
    "residual_instances": 670,
    "residual_nodes": 10_210,
    "residual_conflicts": 5_440,
    "residual_sat": 0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def parse_pairs(tokens: list[str], keys: tuple[str, ...]) -> dict[str, int]:
    if len(tokens) != 2 * len(keys):
        raise AssertionError((len(tokens), len(keys), tokens))
    result: dict[str, int] = {}
    for index, expected in enumerate(keys):
        key = tokens[2 * index]
        if key != expected:
            raise AssertionError((key, expected, tokens))
        value = tokens[2 * index + 1]
        if not value.isdecimal():
            raise AssertionError((key, value))
        result[key] = int(value)
    return result


def main() -> None:
    assert sha256(SOURCE) == SOURCE_SHA256
    assert sha256(BINARY) == BINARY_SHA256
    aggregate = {key: 0 for key in KEYS}
    all_fixed: list[int] = []

    print(f"SOURCE {SOURCE_SHA256}")
    print(f"BINARY {BINARY_SHA256}")
    for shard in range(6):
        base = Path(f"{PREFIX}{shard}")
        status = base.with_suffix(".status")
        output = base.with_suffix(".out")
        log = base.with_suffix(".log")
        assert status.read_bytes() == b"20\n"

        output_lines = output.read_text(encoding="ascii").splitlines()
        assert len(output_lines) == 1
        words = output_lines[0].split()
        assert words[:3] == ["UNSAT_Q1234_SHARD", str(shard), "6"]
        final = parse_pairs(words[3:], KEYS)
        assert final["fixed_processed"] == (15 if shard < 5 else 14)
        assert final["residual_instances"] == final["passed3"]
        assert final["residual_sat"] == 0
        for depth in (1, 2, 3):
            assert final[f"passed{depth}"] <= final[f"tested{depth}"]

        log_lines = log.read_text(encoding="ascii").splitlines()
        assert len(log_lines) == 2 * final["fixed_processed"] + 3
        expected_indices = list(range(shard, 89, 6))
        assert len(expected_indices) == final["fixed_processed"]
        previous = {key: 0 for key in PROGRESS_KEYS}
        candidate_total = 0
        for offset, fixed_index in enumerate(expected_indices):
            fixed_words = log_lines[2 * offset].split()
            assert fixed_words[:2] == ["fixed", str(fixed_index)]
            assert fixed_words[2] == "candidates"
            assert len(fixed_words) == 4 and fixed_words[3].isdecimal()
            candidates = int(fixed_words[3])
            assert candidates > 0
            candidate_total += candidates

            progress_words = log_lines[2 * offset + 1].split()
            assert progress_words[:2] == [
                "completed_fixed", str(fixed_index)]
            assert progress_words[-2] == "seconds"
            seconds = float(progress_words[-1])
            assert seconds >= 0
            current = parse_pairs(progress_words[2:-2], PROGRESS_KEYS)
            for key in PROGRESS_KEYS:
                assert current[key] >= previous[key]
            for depth in (1, 2, 3):
                assert current[f"passed{depth}"] <= current[f"tested{depth}"]
            assert current["residual_instances"] == current["passed3"]
            assert current["residual_sat"] == 0
            previous = current
            all_fixed.append(fixed_index)

        assert candidate_total == final["tested1"]
        for key in PROGRESS_KEYS:
            assert previous[key] == final[key]
        assert re.fullmatch(r"real [0-9]+(?:\.[0-9]+)?", log_lines[-3])
        assert re.fullmatch(r"user [0-9]+(?:\.[0-9]+)?", log_lines[-2])
        assert re.fullmatch(r"sys [0-9]+(?:\.[0-9]+)?", log_lines[-1])

        for key in KEYS:
            aggregate[key] += final[key]
        print(
            f"SHARD {shard} fixed={final['fixed_processed']} "
            f"tested={final['tested1']},{final['tested2']},{final['tested3']} "
            f"passed={final['passed1']},{final['passed2']},{final['passed3']} "
            f"residual_sat={final['residual_sat']} "
            f"out_sha256={sha256(output)} "
            f"log_sha256={sha256(log)} "
            f"status_sha256={sha256(status)}"
        )

    assert sorted(all_fixed) == list(range(89))
    assert len(all_fixed) == len(set(all_fixed)) == 89
    assert aggregate == EXPECTED_AGGREGATE
    print(
        "AGGREGATE "
        + " ".join(f"{key}={aggregate[key]}" for key in KEYS)
    )
    print("Q1234_PRIMARY_AUDIT_OK")


if __name__ == "__main__":
    main()
