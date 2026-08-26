#!/usr/bin/env python3
"""Audit coverage and exact CNF construction of the two-size-22 leaf batch.

This deliberately does not validate DRAT proofs.  Proof validation is a
separate DRAT-to-LRAT plus LRAT-check pass.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import shutil
import subprocess


N = 11
K = 6
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PROFILES = (
    "0_0_1_1_1_8",
    "0_0_1_1_2_7",
    "0_0_1_1_3_6",
    "0_0_1_1_4_5",
    "0_0_1_2_2_6",
    "0_0_1_2_3_5",
    "0_0_1_2_4_4",
    "0_0_1_3_3_4",
    "0_0_2_2_2_5",
    "0_0_2_2_3_4",
    "0_0_2_3_3_3",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def decompressed_zstd_summary(path: Path):
    executable = shutil.which("zstd")
    if not executable:
        raise RuntimeError("zstd is required for compressed proof audit")
    digest = hashlib.sha256()
    size = 0
    process = subprocess.Popen(
        [executable, "-dc", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    while block := process.stdout.read(1024 * 1024):
        digest.update(block)
        size += len(block)
    _, error = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            f"zstd failed for {path}: "
            f"{error.decode(errors='replace')}")
    return size, digest.hexdigest()


def transform_point(x: int, y: int, reflection: int, rotations: int):
    if reflection:
        x = N - 1 - x
    for _ in range(rotations):
        x, y = y, N - 1 - x
    return x, y


def transform_mask(mask: int, reflection: int, rotations: int):
    result = 0
    for x in range(N):
        for y in range(N):
            if mask >> (N * x + y) & 1:
                xx, yy = transform_point(
                    x, y, reflection, rotations)
                result |= 1 << (N * xx + yy)
    return result


def canonical_pair(first: int, second: int):
    return min(
        tuple(sorted((
            transform_mask(first, reflection, rotations),
            transform_mask(second, reflection, rotations),
        )))
        for reflection in (0, 1)
        for rotations in range(4)
    )


def valid_cap(mask: int):
    points = [
        (x, y)
        for x in range(N)
        for y in range(N)
        if mask >> (N * x + y) & 1
    ]
    if len(points) != 22:
        return False
    for triple in itertools.combinations(points, 3):
        (x1, y1), (x2, y2), (x3, y3) = triple
        if ((x2 - x1) * (y3 - y1)
                == (x3 - x1) * (y2 - y1)):
            return False
    return True


def maximal_lines():
    equations = set()
    points = [(x, y) for x in range(N) for y in range(N)]
    for (x1, y1), (x2, y2) in itertools.combinations(points, 2):
        a = y2 - y1
        b = x1 - x2
        c = -(a * x1 + b * y1)
        divisor = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
        a, b, c = a // divisor, b // divisor, c // divisor
        if a < 0 or (a == 0 and b < 0):
            a, b, c = -a, -b, -c
        equations.add((a, b, c))
    lines = []
    for a, b, c in equations:
        members = [
            (x, y) for x, y in points if a * x + b * y + c == 0
        ]
        if len(members) >= 3:
            lines.append((
                len(members),
                sum(1 << (N * x + y) for x, y in members),
            ))
    assert len(lines) == 628
    return lines


def read_pairs(path: Path):
    pairs = [
        tuple(int(field, 16) for field in line.split())
        for line in path.read_text(encoding="ascii").splitlines()
        if line
    ]
    assert all(len(pair) == 2 for pair in pairs)
    return pairs


def parse_base(path: Path):
    lines = path.read_text(encoding="ascii").splitlines()
    header = lines[0].split()
    assert header[:2] == ["p", "cnf"]
    variables, clauses = map(int, header[2:])
    assert len(lines) - 1 == clauses
    return variables, clauses, lines[1:]


def expected_units(pair):
    first, second = pair
    units = []
    for point in range(N * N):
        if first >> point & 1:
            units.append(f"{point * K + 1} 0")
        if second >> point & 1:
            units.append(f"{point * K + 2} 0")
    assert len(units) == 44
    return units


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path("work/sat_agent/profiles22"),
    )
    parser.add_argument(
        "--pairs",
        type=Path,
        default=Path(
            "work/sat_agent/cap_pairs22_capacity_d4_swap.hex"),
    )
    parser.add_argument(
        "--alternative-pairs",
        type=Path,
        default=Path(
            "work/math_agent/pairs22_filtered_ordered_d4.hex"),
    )
    parser.add_argument(
        "--all-caps",
        type=Path,
        default=Path(
            "work/independent_agent/caps22_diag_independent.hex"),
    )
    parser.add_argument(
        "--leaves",
        type=Path,
        default=Path("work/sat_agent/twomax_leaf_proofs"),
    )
    parser.add_argument(
        "--reports",
        type=Path,
        default=None,
        help="directory containing the separately packaged solver JSON reports",
    )
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument(
        "--defer-proof-content",
        action="store_true",
        help="check proof paths/metadata but leave proof hashing to the "
             "subsequent certificate checker",
    )
    parser.add_argument(
        "--allow-zstd",
        action="store_true",
        help="accept PROOF.drat.zst when the JSON-recorded PROOF.drat "
             "has been removed",
    )
    args = parser.parse_args()

    caps = [
        int(line, 16)
        for line in args.all_caps.read_text(
            encoding="ascii").splitlines()
        if line
    ]
    assert len(caps) == len(set(caps)) == 676
    assert all(valid_cap(cap) for cap in caps)
    cap_set = set(caps)
    lines = maximal_lines()
    edges = [
        (first, second)
        for index, first in enumerate(caps)
        for second in caps[index + 1:]
        if not first & second
    ]
    assert len(edges) == 2138
    admissible = [
        pair
        for pair in edges
        if all(
            length - ((pair[0] | pair[1]) & line).bit_count() <= 8
            for length, line in lines
        )
    ]
    assert len(admissible) == 930
    exhaustive_keys = {canonical_pair(*pair) for pair in admissible}
    assert len(exhaustive_keys) == 119

    pairs = read_pairs(args.pairs)
    alternative_pairs = read_pairs(args.alternative_pairs)
    assert len(pairs) == len(set(pairs)) == 119
    assert len(alternative_pairs) == len(set(alternative_pairs)) == 119
    assert all(
        first in cap_set and second in cap_set and not first & second
        for first, second in pairs
    )
    assert {canonical_pair(*pair) for pair in pairs} == exhaustive_keys
    assert (
        {canonical_pair(*pair) for pair in alternative_pairs}
        == exhaustive_keys
    )

    bases = {}
    actual_profiles = []
    for profile in EXPECTED_PROFILES:
        path = args.profiles / f"profile_{profile}.cnf"
        bases[profile] = (path, *parse_base(path))
        actual_profiles.append(profile)
        deficits = tuple(map(int, profile.split("_")))
        assert deficits[:2] == (0, 0)
        assert tuple(sorted(deficits)) == deficits
        assert sum(deficits) == 11
    globbed = sorted(
        path.stem.removeprefix("profile_")
        for path in args.profiles.glob("profile_0_0_*.cnf")
        if path.stem.count("_") == 6
    )
    assert globbed == sorted(actual_profiles)

    expected_names = {
        f"{profile}__pair_{index:03d}"
        for profile in EXPECTED_PROFILES
        for index in range(119)
    }
    cnf_paths = sorted(args.leaves.glob("*.cnf"))
    actual_names = {path.stem for path in cnf_paths}
    assert actual_names <= expected_names
    if args.require_all:
        assert actual_names == expected_names

    checked_json = 0
    for path in cnf_paths:
        profile, index_text = path.stem.split("__pair_")
        pair_index = int(index_text)
        base_path, variables, clause_count, body = bases[profile]
        lines_in_leaf = path.read_text(encoding="ascii").splitlines()
        assert lines_in_leaf[0] == (
            f"p cnf {variables} {clause_count + 44}")
        assert lines_in_leaf[1:1 + clause_count] == body
        assert lines_in_leaf[1 + clause_count:] == expected_units(
            pairs[pair_index])

        report_path = ((args.reports / f"{path.stem}.json")
                       if args.reports is not None
                       else path.with_suffix(".json"))
        if not report_path.exists():
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["name"] == path.stem
        assert report["profile"] == profile
        assert report["pair_index"] == pair_index
        assert report["exit_code"] == 20
        assert report["stdout"] == "s UNSATISFIABLE\n"
        assert report["cnf_bytes"] == path.stat().st_size
        assert report["cnf_sha256"] == sha256(path)
        if not args.defer_proof_content:
            proof = Path(report["proof"])
            if not proof.is_absolute():
                proof = PROJECT_ROOT / proof
            compressed = Path(str(proof) + ".zst")
            if proof.exists():
                assert report["proof_bytes"] == proof.stat().st_size
                assert report["proof_sha256"] == sha256(proof)
            else:
                assert args.allow_zstd and compressed.exists()
                size, digest = decompressed_zstd_summary(compressed)
                assert report["proof_bytes"] == size
                assert report["proof_sha256"] == digest
        checked_json += 1

    if args.require_all:
        assert checked_json == len(expected_names)

    print(
        "VERIFIED "
        f"caps=676 disjoint_edges=2138 admissible_edges=930 "
        f"pair_orbits=119 alternative_orbits_equal=yes "
        f"profiles={len(EXPECTED_PROFILES)} expected_leaves=1309 "
        f"present_leaves={len(cnf_paths)} completed_reports={checked_json} "
        f"pairs_sha256={sha256(args.pairs)}")


if __name__ == "__main__":
    main()
