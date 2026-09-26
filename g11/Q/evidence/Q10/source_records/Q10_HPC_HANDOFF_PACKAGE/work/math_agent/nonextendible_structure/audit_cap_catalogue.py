#!/usr/bin/env python3
"""Independent audit for capset-join catalogues and optional witnesses.

The catalogue audit deliberately does not import the enumerator or C++ join
solver.  It reconstructs all 628 maximal lines, all 6,992 triples, validates
strict ordering/uniqueness and checks every mask's exact Q10-compatible
size-20 conditions.  Completeness of a catalogue remains a property of the
upstream exhaustive shard enumeration and must be audited separately.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from math import gcd
from pathlib import Path

N = 11
P = N * N
FULL = (1 << P) - 1


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
    assert len(result) == len(set(result)) == 628
    return result


def mask_of(points: tuple[int, ...] | list[int]) -> int:
    return sum(1 << p for p in points)


def read_masks(path: Path) -> list[int]:
    result: list[int] = []
    for raw in path.read_text().splitlines():
        text = raw.strip()
        if text and not text.startswith("#"):
            if len(text) != 31:
                raise AssertionError(f"non-31-digit mask: {text!r}")
            result.append(int(text, 16))
    return result


def pair_id(deficits: list[int]) -> int:
    pairs = list(itertools.combinations(range(N), 2))
    return pairs.index(tuple(deficits))


def validate_witness(path: Path, lines: list[tuple[int, ...]]) -> dict[str, object]:
    masks = read_masks(path)
    if len(masks) != 6:
        raise AssertionError("witness must contain six masks")
    sizes = [mask.bit_count() for mask in masks]
    if sizes != [22, 20, 20, 20, 20, 19]:
        raise AssertionError(f"wrong witness sizes {sizes}")
    occupied = 0
    for mask in masks:
        if occupied & mask:
            raise AssertionError("witness masks overlap")
        occupied |= mask
        if any((mask & mask_of(line)).bit_count() > 2 for line in lines):
            raise AssertionError("witness has a monochromatic triple")
    if occupied != FULL:
        raise AssertionError("witness does not cover exactly the grid")
    triples = set(t for line in lines for t in itertools.combinations(line, 3))
    if len(triples) != 6992:
        raise AssertionError("bad triple reconstruction")
    bad = sum(all((masks[colour] >> p) & 1 for p in triple)
              for colour in range(6) for triple in triples)
    if bad:
        raise AssertionError("witness fails direct 6,992-triple audit")
    return {
        "status": "PASS",
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sizes": sizes,
        "covered_points": occupied.bit_count(),
        "checked_maximal_lines_per_colour": len(lines),
        "checked_collinear_triples_per_colour": len(triples),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor", required=True)
    parser.add_argument("--caps", type=Path, required=True)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--witness", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    if len(args.anchor) != 31:
        raise AssertionError("anchor must have 31 hex digits")
    anchor = int(args.anchor, 16)
    if anchor.bit_count() != 22 or anchor & ~FULL:
        raise AssertionError("bad anchor mask")
    lines = maximal_lines()
    line_masks = [mask_of(line) for line in lines]
    triples = set(t for line in lines for t in itertools.combinations(line, 3))
    if len(triples) != 6992:
        raise AssertionError("geometry does not contain exactly 6,992 triples")
    anchor_counts = [(anchor & line_mask).bit_count() for line_mask in line_masks]
    if any(count > 2 for count in anchor_counts):
        raise AssertionError("anchor contains a triple")

    masks = read_masks(args.caps)
    if args.expected_count is not None and len(masks) != args.expected_count:
        raise AssertionError(f"got {len(masks)} masks, expected {args.expected_count}")
    if any(a >= b for a, b in itertools.pairwise(masks)):
        raise AssertionError("catalogue is not strictly increasing and unique")

    # Pair-line lookup is independent of the maximal-line generator above: it
    # uses the determinant equation directly for each pair of points.
    pair_lines = [[0] * P for _ in range(P)]
    for a in range(P):
        ar, ac = divmod(a, N)
        for b in range(a + 1, P):
            br, bc = divmod(b, N)
            line = 0
            for p in range(P):
                pr, pc = divmod(p, N)
                if (br - ar) * (pc - ac) == (bc - ac) * (pr - ar):
                    line |= 1 << p
            pair_lines[a][b] = pair_lines[b][a] = line

    tight_lines = [
        (line_mask, len(line), anchor_count)
        for line_mask, line, anchor_count in zip(line_masks, lines, anchor_counts)
        if len(line) - anchor_count > 8
    ]
    signature_histogram: Counter[tuple[int, int]] = Counter()
    for index, mask in enumerate(masks):
        if mask & ~FULL or mask.bit_count() != 20:
            raise AssertionError(f"mask {index} is not a grid size-20 set")
        if mask & anchor:
            raise AssertionError(f"mask {index} intersects the anchor")
        points = [p for p in range(P) if (mask >> p) & 1]
        for a, b in itertools.combinations(points, 2):
            if (mask & pair_lines[a][b]).bit_count() > 2:
                raise AssertionError(f"mask {index} contains a collinear triple")
        row_counts = [sum(p // N == r for p in points) for r in range(N)]
        col_counts = [sum(p % N == c for p in points) for c in range(N)]
        if sorted(row_counts) != [1, 1] + [2] * 9:
            raise AssertionError(f"mask {index} has bad row multiplicities")
        if sorted(col_counts) != [1, 1] + [2] * 9:
            raise AssertionError(f"mask {index} has bad column multiplicities")
        row_deficits = [r for r, count in enumerate(row_counts) if count == 1]
        col_deficits = [c for c, count in enumerate(col_counts) if count == 1]
        signature_histogram[pair_id(row_deficits), pair_id(col_deficits)] += 1
        for line_mask, length, anchor_count in tight_lines:
            if length - anchor_count - (mask & line_mask).bit_count() > 8:
                raise AssertionError(f"mask {index} fails residual four-colour line capacity")

    result: dict[str, object] = {
        "status": "PASS",
        "claim_boundary": "validates catalogue contents, not exhaustive completeness of its enumeration",
        "anchor_hex": f"{anchor:031x}",
        "anchor_size": anchor.bit_count(),
        "caps_path": str(args.caps),
        "caps_sha256": hashlib.sha256(args.caps.read_bytes()).hexdigest(),
        "candidate_count": len(masks),
        "strictly_increasing_unique": True,
        "all_candidates_size20": True,
        "all_candidates_disjoint_from_anchor": True,
        "all_candidates_no_three_in_line": True,
        "all_candidates_have_two_deficit_rows_and_columns": True,
        "all_candidates_pass_four_colour_line_capacity": True,
        "checked_maximal_lines": len(lines),
        "checked_collinear_triples": len(triples),
        "tight_line_count_for_single_cap": len(tight_lines),
        "nonempty_signature_cells": len(signature_histogram),
        "signature_histogram": {
            f"{rp},{cp}": count for (rp, cp), count in sorted(signature_histogram.items())
        },
    }
    if args.witness:
        result["witness_audit"] = validate_witness(args.witness, lines)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "signature_histogram"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
