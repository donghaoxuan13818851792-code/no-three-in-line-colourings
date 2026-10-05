#!/usr/bin/env python3
"""Aggregate and audit the 55 exact capset_join root-row-pair shards."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path
import re

N = 11
P = 121
FULL = (1 << P) - 1

FIELDS = {
    "status", "anchor", "candidate_count", "root_row_pair",
    "roots_examined", "pair_candidates", "triple_candidates",
    "final_pool_candidates", "pair_pools_built", "triple_pools_built",
    "final_pools_built", "seconds",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_key_values(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        fields = raw.strip().split(maxsplit=1)
        if len(fields) == 2 and fields[0] in FIELDS:
            if fields[0] in result:
                raise AssertionError(f"duplicate {fields[0]} in {path}")
            result[fields[0]] = fields[1]
    missing = FIELDS - set(result)
    # SAT outputs add masks, but all common accounting fields still exist.
    if missing:
        raise AssertionError(f"missing fields in {path}: {sorted(missing)}")
    return result


def parse_meta(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        fields = raw.split(maxsplit=1)
        if len(fields) != 2 or fields[0] in result:
            raise AssertionError(f"bad metadata line: {raw!r}")
        result[fields[0]] = fields[1]
    return result


def parse_resource_log(path: Path) -> dict[str, float | int]:
    """Parse the BSD /usr/bin/time -l fields emitted by the shard runner."""
    timing = re.findall(
        r"^\s*([0-9]+(?:\.[0-9]+)?) real\s+"
        r"([0-9]+(?:\.[0-9]+)?) user\s+"
        r"([0-9]+(?:\.[0-9]+)?) sys\s*$",
        path.read_text(),
        flags=re.MULTILINE,
    )
    rss = re.findall(
        r"^\s*([0-9]+)\s+maximum resident set size\s*$",
        path.read_text(),
        flags=re.MULTILINE,
    )
    if len(timing) != 1 or len(rss) != 1:
        raise AssertionError(f"cannot parse one resource record from {path}")
    real, user, system = map(float, timing[0])
    return {
        "real_seconds": real,
        "user_seconds": user,
        "system_seconds": system,
        "maximum_resident_set_size_bytes": int(rss[0]),
    }


def maximal_lines() -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []
    for dr in range(N):
        for dc in range(-(N - 1), N):
            if dr == 0:
                if dc != 1:
                    continue
            elif gcd(dr, abs(dc)) != 1:
                continue
            for r in range(N):
                for c in range(N):
                    if 0 <= r - dr < N and 0 <= c - dc < N:
                        continue
                    pts: list[int] = []
                    rr, cc = r, c
                    while 0 <= rr < N and 0 <= cc < N:
                        pts.append(N * rr + cc)
                        rr += dr
                        cc += dc
                    if len(pts) >= 3:
                        result.append(tuple(pts))
    if len(result) != 628 or len(set(result)) != 628:
        raise AssertionError("bad independently reconstructed geometry")
    return result


def verify_witness(path: Path, expected_anchor: int) -> dict[str, object]:
    masks = [int(raw.strip(), 16) for raw in path.read_text().splitlines() if raw.strip()]
    if len(masks) != 6 or masks[0] != expected_anchor:
        raise AssertionError(f"bad witness layout in {path}")
    sizes = [mask.bit_count() for mask in masks]
    if sizes != [22, 20, 20, 20, 20, 19]:
        raise AssertionError(f"bad witness sizes in {path}: {sizes}")
    occupied = 0
    for mask in masks:
        if mask & occupied:
            raise AssertionError(f"overlapping witness masks in {path}")
        occupied |= mask
    if occupied != FULL:
        raise AssertionError(f"witness does not cover grid in {path}")
    lines = maximal_lines()
    line_masks = [sum(1 << p for p in line) for line in lines]
    if any((mask & line).bit_count() > 2 for mask in masks for line in line_masks):
        raise AssertionError(f"witness has a monochromatic triple in {path}")
    triples = set(t for line in lines for t in itertools.combinations(line, 3))
    if len(triples) != 6992:
        raise AssertionError("bad triple reconstruction")
    return {
        "path": str(path),
        "sha256": sha256(path),
        "sizes": sizes,
        "covered_points": occupied.bit_count(),
        "maximal_lines_checked_per_colour": len(lines),
        "collinear_triples_reconstructed": len(triples),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument(
        "--caps", type=Path,
        help="relocated catalogue override; SHA/count must match run.meta",
    )
    parser.add_argument(
        "--binary", type=Path,
        help="relocated capset_join override; SHA must match run.meta",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    meta = parse_meta(directory / "run.meta")
    caps = args.caps.resolve() if args.caps else Path(meta["caps"])
    if not caps.is_file():
        raise AssertionError("catalogue recorded in run.meta is missing")
    if sha256(caps) != meta["caps_sha256"]:
        raise AssertionError("catalogue hash differs from run.meta")
    binary = args.binary.resolve() if args.binary else Path(meta["binary"])
    if not binary.is_file() or sha256(binary) != meta["binary_sha256"]:
        raise AssertionError("join binary is missing or differs from run.meta")
    candidate_count = int(meta["caps_count"])
    if sum(bool(raw.strip()) for raw in caps.read_text().splitlines()) != candidate_count:
        raise AssertionError("catalogue line count differs from run.meta")
    anchor = int(meta["anchor"], 16)
    if len(meta["anchor"]) != 31 or anchor.bit_count() != 22:
        raise AssertionError("bad anchor in run.meta")

    rows: list[dict[str, str]] = []
    exit_codes: list[int] = []
    witnesses: list[dict[str, object]] = []
    shard_ledger: list[dict[str, object]] = []
    resource_rows: list[dict[str, float | int]] = []
    stdout_mtimes: list[float] = []
    for rp in range(55):
        stem = directory / f"{rp:02d}"
        for suffix in (".out", ".time", ".exit"):
            if not Path(str(stem) + suffix).is_file():
                raise AssertionError(f"missing shard artifact {stem}{suffix}")
        stdout_path = Path(str(stem) + ".out")
        resource_path = Path(str(stem) + ".time")
        row = parse_key_values(stdout_path)
        resource = parse_resource_log(resource_path)
        code = int(Path(str(stem) + ".exit").read_text().strip())
        if int(row["root_row_pair"]) != rp:
            raise AssertionError(f"shard {rp} reports wrong root pair")
        if row["anchor"] != meta["anchor"] or int(row["candidate_count"]) != candidate_count:
            raise AssertionError(f"shard {rp} used wrong anchor or catalogue count")
        expected_code = {"SAT": 10, "COMPLETE_NO_WITNESS": 20, "INCOMPLETE": 30}.get(row["status"])
        if expected_code is None or code != expected_code:
            raise AssertionError(f"shard {rp} status/exit mismatch: {row['status']}/{code}")
        witness_path = Path(str(stem) + ".witness.hex")
        if row["status"] == "SAT":
            if not witness_path.is_file():
                raise AssertionError(f"SAT shard {rp} has no witness")
            witnesses.append(verify_witness(witness_path, anchor))
        shard_ledger.append({
            "root_row_pair": rp,
            "status": row["status"],
            "exit_code": code,
            "roots_examined": int(row["roots_examined"]),
            "pair_candidates": int(row["pair_candidates"]),
            "triple_candidates": int(row["triple_candidates"]),
            "final_pool_candidates": int(row["final_pool_candidates"]),
            "search_seconds": float(row["seconds"]),
            "external_real_seconds": resource["real_seconds"],
            "external_user_seconds": resource["user_seconds"],
            "external_system_seconds": resource["system_seconds"],
            "maximum_resident_set_size_bytes": resource["maximum_resident_set_size_bytes"],
            "stdout_sha256": sha256(stdout_path),
            "resource_log_sha256": sha256(resource_path),
            "exit_file_sha256": sha256(Path(str(stem) + ".exit")),
            "witness_sha256": sha256(witness_path) if witness_path.is_file() else None,
        })
        rows.append(row)
        resource_rows.append(resource)
        stdout_mtimes.append(stdout_path.stat().st_mtime)
        exit_codes.append(code)

    statuses = [row["status"] for row in rows]
    if "SAT" in statuses:
        mathematical_status = "SAT"
    elif all(status == "COMPLETE_NO_WITNESS" for status in statuses):
        mathematical_status = "UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE"
    else:
        mathematical_status = "INCOMPLETE"

    aggregate = {
        key: sum(int(row[key]) for row in rows)
        for key in (
            "roots_examined", "pair_candidates", "triple_candidates",
            "final_pool_candidates", "pair_pools_built", "triple_pools_built",
            "final_pools_built",
        )
    }
    if mathematical_status == "UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE":
        if aggregate["roots_examined"] != candidate_count:
            raise AssertionError("complete shards did not examine every catalogue mask as one root")
        if aggregate["final_pool_candidates"] != 0:
            raise AssertionError("UNSAT shards report a nonempty final pool")

    result = {
        "status": "PASS" if mathematical_status != "INCOMPLETE" else "NONTERMINAL",
        "mathematical_status": mathematical_status,
        "claim_boundary": "catalogue completeness must be established by its separate exhaustive enumeration audit",
        "anchor_hex": meta["anchor"],
        "catalogue": str(caps),
        "catalogue_recorded_path": meta["caps"],
        "catalogue_sha256": sha256(caps),
        "run_metadata_sha256": sha256(directory / "run.meta"),
        "join_binary_sha256": sha256(binary),
        "join_binary_recorded_path": meta["binary"],
        "candidate_count": candidate_count,
        "shards": len(rows),
        "status_histogram": {status: statuses.count(status) for status in sorted(set(statuses))},
        "exit_code_histogram": {str(code): exit_codes.count(code) for code in sorted(set(exit_codes))},
        "aggregate": aggregate,
        "sum_search_seconds": sum(float(row["seconds"]) for row in rows),
        "maximum_shard_search_seconds": max(float(row["seconds"]) for row in rows),
        "resources": {
            "sum_external_real_seconds": sum(float(row["real_seconds"]) for row in resource_rows),
            "sum_external_user_seconds": sum(float(row["user_seconds"]) for row in resource_rows),
            "sum_external_system_seconds": sum(float(row["system_seconds"]) for row in resource_rows),
            "maximum_resident_set_size_bytes": max(
                int(row["maximum_resident_set_size_bytes"]) for row in resource_rows
            ),
            "makespan_seconds_runmeta_to_last_stdout_mtime": (
                max(stdout_mtimes) - (directory / "run.meta").stat().st_mtime
            ),
            "measurement_note": (
                "resource sums are over 55 BSD /usr/bin/time -l shard records; "
                "makespan is filesystem-mtime derived and operational, not proof evidence"
            ),
        },
        "witnesses": witnesses,
        "shard_ledger": shard_ledger,
    }
    output = args.json or directory / "audit.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
