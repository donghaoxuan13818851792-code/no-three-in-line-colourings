#!/usr/bin/env python3
"""Compare the independent Q1--Q4 replay with every primary fixed-cap result."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIMARY_PREFIX = ROOT / "work/sat_agent/q1234_full_shard"
SOURCE = ROOT / "work/independent_agent/q1234_independent_verifier.cpp"
INCLUDED = ROOT / "work/independent_agent/p1_independent_search.cpp"
BINARY = (
    ROOT / "work/independent_agent/q1234_verifier_build"
    / "q1234_independent_verifier"
)
OUTPUT = ROOT / "work/independent_agent/q1234_independent_full.out"
LOG = ROOT / "work/independent_agent/q1234_independent_full.log"
STATUS = ROOT / "work/independent_agent/q1234_independent_full.status"
RESIDUALS = ROOT / "work/independent_agent/q1234_independent_residuals.tsv"
FIXED_TABLE = ROOT / "work/math_agent/caps22_d4.hex"
SOURCE_SHA256 = (
    "aba311380a8b4ee08349d795b165c6227767b724880c2dd3f2ae4760b8c6ba7b"
)
INCLUDED_SHA256 = (
    "825b3a3d6e8d8c926d8a14c8725175188ab8b0e6d8b0c97e7e4916b2e45da1e8"
)
BINARY_SHA256 = (
    "e5a4010427ff978e17a7075c2588096b3121d6eef1300fdd3070a1bcbcb1313f"
)
FIXED_SHA256 = (
    "234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40"
)
COUNTER_KEYS = (
    "tested1", "passed1",
    "tested2", "passed2",
    "tested3", "passed3",
    "residual_instances", "residual_nodes",
    "residual_conflicts", "residual_sat",
)
COMPARABLE_KEYS = (
    "tested1", "passed1",
    "tested2", "passed2",
    "tested3", "passed3",
    "residual_instances", "residual_sat",
)
EXPECTED = {
    "fixed_processed": 89,
    "tested1": 1_000_619,
    "passed1": 412_995,
    "tested2": 7_470_942,
    "passed2": 1_325_039,
    "tested3": 10_929,
    "passed3": 670,
    "residual_instances": 670,
    "residual_sat": 0,
}
FULL = (1 << 121) - 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def pairs(tokens: list[str]) -> dict[str, int]:
    assert len(tokens) % 2 == 0
    result: dict[str, int] = {}
    for offset in range(0, len(tokens), 2):
        key, text = tokens[offset:offset + 2]
        assert key not in result and text.isdecimal()
        result[key] = int(text)
    return result


def primary_per_fixed() -> tuple[dict[int, dict[str, int]], dict[int, int]]:
    result: dict[int, dict[str, int]] = {}
    candidates: dict[int, int] = {}
    for shard in range(6):
        lines = Path(f"{PRIMARY_PREFIX}{shard}.log").read_text(
            encoding="ascii").splitlines()
        previous = {key: 0 for key in COUNTER_KEYS if key != "residual_conflicts"}
        progress_keys = tuple(previous)
        fixed_lines = lines[:-3]
        assert len(fixed_lines) % 2 == 0
        for offset in range(0, len(fixed_lines), 2):
            first = fixed_lines[offset].split()
            assert first[0] == "fixed" and first[2] == "candidates"
            fixed = int(first[1])
            assert fixed % 6 == shard and fixed not in result
            candidates[fixed] = int(first[3])
            second = fixed_lines[offset + 1].split()
            assert second[:2] == ["completed_fixed", str(fixed)]
            assert second[-2] == "seconds"
            current = pairs(second[2:-2])
            assert tuple(current) == progress_keys
            result[fixed] = {
                key: current[key] - previous[key] for key in progress_keys}
            previous = current
    assert sorted(result) == list(range(89))
    return result, candidates


def maximal_lines() -> list[int]:
    found: set[int] = set()
    for first in range(121):
        r1, c1 = divmod(first, 11)
        for second in range(first + 1, 121):
            r2, c2 = divmod(second, 11)
            mask = 0
            for point in range(121):
                row, column = divmod(point, 11)
                if ((r2 - r1) * (column - c1)
                        == (c2 - c1) * (row - r1)):
                    mask |= 1 << point
            if mask.bit_count() >= 3:
                found.add(mask)
    lines = sorted(found)
    distribution = Counter(mask.bit_count() for mask in lines)
    assert len(lines) == 628
    assert distribution == {
        3: 396, 4: 124, 5: 40, 6: 28,
        7: 4, 8: 4, 9: 4, 10: 4, 11: 24,
    }
    return lines


def main() -> None:
    assert sha256(SOURCE) == SOURCE_SHA256
    assert sha256(INCLUDED) == INCLUDED_SHA256
    assert sha256(BINARY) == BINARY_SHA256
    assert sha256(FIXED_TABLE) == FIXED_SHA256
    assert STATUS.read_bytes() == b"20\n"
    primary, primary_candidates = primary_per_fixed()

    output_lines = OUTPUT.read_text(encoding="ascii").splitlines()
    assert len(output_lines) == 90
    independent: dict[int, dict[str, int]] = {}
    independent_candidates: dict[int, int] = {}
    for fixed, line in enumerate(output_lines[:-1]):
        words = line.split()
        assert words[:2] == ["INDEPENDENT_FIXED", str(fixed)]
        current = pairs(words[2:])
        assert current["candidates"] > 0
        independent_candidates[fixed] = current.pop("candidates")
        assert tuple(current) == COUNTER_KEYS
        independent[fixed] = current
        for key in COMPARABLE_KEYS:
            assert current[key] == primary[fixed][key], (
                fixed, key, current[key], primary[fixed][key])
        assert current["residual_instances"] == current["passed3"]
        assert current["residual_sat"] == 0
        assert independent_candidates[fixed] == primary_candidates[fixed]

    final_words = output_lines[-1].split()
    assert final_words[:3] == [
        "INDEPENDENT_UNSAT_Q1234_SHARD", "0", "1"]
    final = pairs(final_words[3:])
    for key, expected in EXPECTED.items():
        assert final[key] == expected
    for key in COUNTER_KEYS:
        assert final[key] == sum(
            independent[fixed][key] for fixed in range(89))

    fixed_masks = sorted(
        int(line, 16) for line in FIXED_TABLE.read_text(
            encoding="ascii").splitlines() if line)
    assert len(fixed_masks) == len(set(fixed_masks)) == 89
    lines = maximal_lines()
    residual_counts: Counter[int] = Counter()
    residual_lines = RESIDUALS.read_text(encoding="ascii").splitlines()
    assert len(residual_lines) == 670
    seen_prefixes: set[tuple[int, int, int, int]] = set()
    for text in residual_lines:
        fields = text.split()
        assert len(fields) == 5
        fixed = int(fields[0])
        selected = tuple(int(value, 16) for value in fields[1:4])
        residual = int(fields[4], 16)
        assert 0 <= fixed < 89
        assert all(len(value) == 31 for value in fields[1:])
        assert selected[0] < selected[1] < selected[2]
        assert all(mask.bit_count() == 21 and not mask & ~FULL
                   for mask in selected)
        assert residual.bit_count() == 36 and not residual & ~FULL
        assert all(not (first & second)
                   for first, second in itertools.combinations(selected, 2))
        assert all(not (fixed_masks[fixed] & mask) for mask in selected)
        union = fixed_masks[fixed]
        for mask in selected:
            union |= mask
        assert residual == FULL ^ union
        assert all((mask & line).bit_count() <= 2
                   for mask in selected for line in lines)
        assert all((residual & line).bit_count() <= 4 for line in lines)
        prefix = (fixed, *selected)
        assert prefix not in seen_prefixes
        seen_prefixes.add(prefix)
        residual_counts[fixed] += 1
    for fixed in range(89):
        assert residual_counts[fixed] == independent[fixed]["passed3"]

    print(
        "Q1234_INDEPENDENT_VERIFIED "
        "fixed=89 tested=1000619,7470942,10929 "
        "passed=412995,1325039,670 residual_sat=0 "
        "per_fixed_primary_match=yes residual_masks=670")
    for path in (SOURCE, INCLUDED, BINARY, OUTPUT, LOG, STATUS, RESIDUALS):
        print(
            f"{path.relative_to(ROOT)} bytes={path.stat().st_size} "
            f"sha256={sha256(path)}")


if __name__ == "__main__":
    main()
