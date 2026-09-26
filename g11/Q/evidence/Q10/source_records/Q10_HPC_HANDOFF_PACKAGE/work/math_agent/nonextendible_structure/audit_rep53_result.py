#!/usr/bin/env python3
"""Audit the complete representative-53 cap-enumeration -> join chain.

This is an artifact/coverage verifier, not a formal proof checker for the C++
programs.  It independently checks that all 55x55 enumeration shards are
terminal and uniquely keyed, that every shard's mask count agrees with its
log, that their exact union equals the published strict-sorted catalogue,
and that the unsharded join log exhausts every catalogue mask as a canonical
root and reaches no final candidate.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

REPRESENTATIVE_INDEX = 53
ANCHOR_HEX = "0060c001228180002c2000611140028"
CATALOGUE_SHA256 = "54ef39928a170625452cf843def3d86d0e242478405a4097236e5c6b3e150f34"
CATALOGUE_COUNT = 289_590
JOIN_LOG_SHA256 = "19c4b2392ccbd7631a31a8f23504fc19e0444e4d9d0a8da6c96c2aed934d2111"

SHARD_PATTERN = re.compile(
    r"^(\d+),(\d+),(COMPLETE|INCOMPLETE) count (\d+) "
    r"least_eligible (\d+) extendible (\d+) nonextendible (\d+) "
    r"nodes (\d+) leaves (\d+) tight_lines (\d+) "
    r"column_rejects (\d+) line_rejects (\d+) "
    r"self_secant_rejects (\d+) seconds ([0-9.eE+-]+),exit=(\d+)$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_hex(path: Path) -> list[int]:
    result: list[int] = []
    for raw in path.read_text().splitlines():
        text = raw.strip()
        if text:
            if len(text) != 31:
                raise AssertionError(f"bad mask in {path}: {text!r}")
            result.append(int(text, 16))
    return result


def parse_join(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        fields = raw.strip().split(maxsplit=1)
        if len(fields) == 2 and fields[0] in {
            "status", "anchor", "candidate_count", "root_row_pair",
            "roots_examined", "pair_candidates", "triple_candidates",
            "final_pool_candidates", "pair_pools_built",
            "triple_pools_built", "final_pools_built", "seconds",
        }:
            result[fields[0]] = fields[1]
    return result


def main() -> None:
    task_root = Path(__file__).resolve().parents[3]
    solver = task_root / "work/solver_agent"
    root = task_root / "work/root"
    package_data = task_root / "work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data"
    shard_log = solver / "cap20_rep53_v4_shards.log"
    shard_summary_path = solver / "cap20_rep53_v4_shards.summary.json"
    shard_dir = solver / "cap20_rep53_v4_shards"
    catalogue_path = solver / "cap20_rep53_all_masks_v4.hex"
    catalogue_audit_path = solver / "cap20_rep53_all_masks_v4.audit.log"
    reps_path = package_data / "caps22_d4.hex"
    join_log_path = root / "rep53_capset_join.log"

    reps = [int(s, 16) for s in reps_path.read_text().split()]
    if len(reps) != 89 or f"{reps[REPRESENTATIVE_INDEX]:031x}" != ANCHOR_HEX:
        raise AssertionError("representative 53 does not match the claimed anchor")

    records: dict[tuple[int, int], dict[str, int | float | str]] = {}
    for line_number, raw in enumerate(shard_log.read_text().splitlines(), 1):
        match = SHARD_PATTERN.fullmatch(raw.strip())
        if not match:
            raise AssertionError(f"unparsed shard log line {line_number}: {raw!r}")
        (rp, cp, status, count, least, extendible, nonextendible, nodes,
         leaves, tight, column_rejects, line_rejects, self_rejects,
         seconds, exit_code) = match.groups()
        key = (int(rp), int(cp))
        if key in records:
            raise AssertionError(f"duplicate shard key {key}")
        records[key] = {
            "status": status,
            "count": int(count),
            "least": int(least),
            "extendible": int(extendible),
            "nonextendible": int(nonextendible),
            "nodes": int(nodes),
            "leaves": int(leaves),
            "tight": int(tight),
            "column_rejects": int(column_rejects),
            "line_rejects": int(line_rejects),
            "self_rejects": int(self_rejects),
            "seconds": float(seconds),
            "exit": int(exit_code),
        }
    expected_keys = {(rp, cp) for rp in range(55) for cp in range(55)}
    if set(records) != expected_keys:
        raise AssertionError("shard keys do not cover exactly 55x55")
    if any(row["status"] != "COMPLETE" or row["exit"] != 0 for row in records.values()):
        raise AssertionError("not every enumeration shard terminated COMPLETE with exit 0")
    if any(row["count"] != row["leaves"] for row in records.values()):
        raise AssertionError("a shard's leaf count differs from its cap count")
    if any(row["count"] != row["extendible"] + row["nonextendible"] for row in records.values()):
        raise AssertionError("a shard's frozen-cap classification does not sum")

    # Check each exact shard payload against its own terminal record, then
    # compare the aggregate as an integer multiset with the canonical file.
    aggregate: list[int] = []
    shard_files = list(shard_dir.glob("*.hex"))
    if len(shard_files) != 3025:
        raise AssertionError(f"expected 3,025 shard files, got {len(shard_files)}")
    for rp, cp in sorted(expected_keys):
        path = shard_dir / f"{rp:02d}_{cp:02d}.hex"
        masks = read_hex(path)
        if len(masks) != records[rp, cp]["count"]:
            raise AssertionError(f"mask count mismatch for shard {(rp, cp)}")
        aggregate.extend(masks)
    if len(aggregate) != CATALOGUE_COUNT:
        raise AssertionError("aggregate shard count mismatch")

    catalogue = read_hex(catalogue_path)
    if sha256(catalogue_path) != CATALOGUE_SHA256:
        raise AssertionError("catalogue SHA-256 mismatch")
    if len(catalogue) != CATALOGUE_COUNT:
        raise AssertionError("catalogue count mismatch")
    if any(a >= b for a, b in zip(catalogue, catalogue[1:])):
        raise AssertionError("catalogue is not strict-sorted unique")
    if sorted(aggregate) != catalogue:
        raise AssertionError("catalogue differs from the exact shard multiset")

    expected_audit = (
        "AUDIT_OK count 289590 least_eligible 158232 extendible 6 "
        "nonextendible 289584 maximal_lines 628"
    )
    if catalogue_audit_path.read_text().strip() != expected_audit:
        raise AssertionError("independent catalogue audit log mismatch")

    summary = json.loads(shard_summary_path.read_text())
    expected_summary = {
        "records": 3025,
        "unique_keys": 3025,
        "complete_records": 3025,
        "incomplete_records": 0,
        "duplicate_record_count": 0,
        "missing_keys": [],
        "extra_keys": [],
        "nonzero_exit_records": 0,
        "exact_total_count": 289590,
        "exact_least_eligible_count": 158232,
        "exact_extendible_count": 6,
        "exact_nonextendible_count": 289584,
        "exact_self_secant_rejects": 0,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key}: got {summary.get(key)!r}, expected {expected!r}")
    if summary.get("input_sha256") != sha256(shard_log):
        raise AssertionError("summary does not hash the actual shard log")

    join = parse_join(join_log_path)
    expected_join = {
        "status": "COMPLETE_NO_WITNESS",
        "anchor": ANCHOR_HEX,
        "candidate_count": "289590",
        "root_row_pair": "-1",
        "roots_examined": "289590",
        "pair_candidates": "37666625",
        "triple_candidates": "490113",
        "final_pool_candidates": "0",
        "pair_pools_built": "289590",
        "triple_pools_built": "37666625",
        "final_pools_built": "490113",
    }
    for key, expected in expected_join.items():
        if join.get(key) != expected:
            raise AssertionError(f"join {key}: got {join.get(key)!r}, expected {expected!r}")
    if sha256(join_log_path) != JOIN_LOG_SHA256:
        raise AssertionError("join log SHA-256 mismatch")

    result = {
        "status": "PASS",
        "mathematical_status": "representative 53 exhaustively UNSAT relative to the frozen anchor dependency",
        "global_q10_status": "INCOMPLETE: 88 other representatives are not covered by this result",
        "audit_scope": (
            "checks exact shard coverage and payloads, catalogue identity and independent validation log, "
            "and the complete join result; source-code correctness is established by review/reproduction, "
            "not formally proved by this manifest"
        ),
        "representative_index": REPRESENTATIVE_INDEX,
        "anchor_hex": ANCHOR_HEX,
        "enumeration": {
            "shards": len(records),
            "all_complete_exit_zero": True,
            "candidate_count": len(catalogue),
            "least_eligible_count": sum(int(row["least"]) for row in records.values()),
            "extendible_count": sum(int(row["extendible"]) for row in records.values()),
            "nonextendible_count": sum(int(row["nonextendible"]) for row in records.values()),
            "self_secant_rejects": sum(int(row["self_rejects"]) for row in records.values()),
            "catalogue_sha256": sha256(catalogue_path),
            "shard_log_sha256": sha256(shard_log),
            "shard_summary_sha256": sha256(shard_summary_path),
            "independent_catalogue_audit_sha256": sha256(catalogue_audit_path),
        },
        "join": {
            "status": join["status"],
            "roots_examined": int(join["roots_examined"]),
            "pair_candidates": int(join["pair_candidates"]),
            "triple_candidates": int(join["triple_candidates"]),
            "final_pool_candidates": int(join["final_pool_candidates"]),
            "seconds": float(join["seconds"]),
            "log_sha256": sha256(join_log_path),
        },
    }
    output = Path(__file__).with_name("rep53_result_audit.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
