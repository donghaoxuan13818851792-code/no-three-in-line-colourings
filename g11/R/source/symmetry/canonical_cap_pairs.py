#!/usr/bin/env python3
"""Enumerate D4-and-swap orbit representatives of disjoint size-22 caps.

Input masks use the convention of ``work/math_agent/enumerate_caps.cpp``:
bit ``11*x+y`` represents the point ``(x,y)`` with zero-based coordinates.
Each output line contains the two masks of one canonical unordered pair.
"""

from __future__ import annotations

import argparse
import math
import pathlib


N = 11


def transform(mask: int, symmetry: int) -> int:
    result = 0
    for point in range(N * N):
        if not (mask >> point) & 1:
            continue
        x, y = divmod(point, N)
        images = (
            (x, y),
            (x, N - 1 - y),
            (N - 1 - x, y),
            (N - 1 - x, N - 1 - y),
            (y, x),
            (y, N - 1 - x),
            (N - 1 - y, x),
            (N - 1 - y, N - 1 - x),
        )
        xx, yy = images[symmetry]
        result |= 1 << (N * xx + yy)
    return result


def canonical_pair(first: int, second: int) -> tuple[int, int]:
    images = []
    for symmetry in range(8):
        a = transform(first, symmetry)
        b = transform(second, symmetry)
        images.append((a, b) if a < b else (b, a))
    return min(images)


def maximal_line_masks() -> list[int]:
    masks = []
    for dx in range(N):
        for dy in range(-(N - 1), N):
            if dx == 0:
                if dy != 1:
                    continue
            elif math.gcd(dx, abs(dy)) != 1:
                continue
            for x in range(N):
                for y in range(N):
                    if 0 <= x - dx < N and 0 <= y - dy < N:
                        continue
                    mask = 0
                    xx, yy = x, y
                    while 0 <= xx < N and 0 <= yy < N:
                        mask |= 1 << (N * xx + yy)
                        xx += dx
                        yy += dy
                    if mask.bit_count() >= 3:
                        masks.append(mask)
    if len(masks) != 628 or len(masks) != len(set(masks)):
        raise AssertionError("expected 628 distinct maximal relevant lines")
    return masks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("caps", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument(
        "--complement-capacity", action="store_true",
        help="retain only pairs whose complement meets every line in at "
             "most eight points, as required for four remaining colours")
    args = parser.parse_args()

    caps = [
        int(line, 16)
        for line in args.caps.read_text(encoding="ascii").splitlines()
        if line
    ]
    if len(caps) != len(set(caps)) or len(caps) != 676:
        raise ValueError("expected 676 distinct diagonal-feasible caps")
    cap_set = set(caps)
    if any(mask.bit_count() != 22 for mask in caps):
        raise ValueError("every cap must have 22 points")
    if any(transform(mask, symmetry) not in cap_set
           for mask in caps for symmetry in range(8)):
        raise ValueError("cap list is not closed under D4")

    edges = [
        (first, second)
        for index, first in enumerate(caps)
        for second in caps[index + 1:]
        if not first & second
    ]
    if len(edges) != 2138:
        raise ValueError(f"expected 2138 disjoint pairs, got {len(edges)}")
    if args.complement_capacity:
        line_masks = maximal_line_masks()
        edges = [
            (first, second) for first, second in edges
            if all(
                (line & ~(first | second)).bit_count() <= 8
                for line in line_masks
            )
        ]
        if len(edges) != 930:
            raise ValueError(
                f"expected 930 capacity-feasible pairs, got {len(edges)}")
    representatives = sorted({
        canonical_pair(first, second) for first, second in edges
    })

    with args.output.open("w", encoding="ascii") as out:
        for first, second in representatives:
            out.write(f"{first:031x} {second:031x}\n")
    print(
        f"caps={len(caps)} retained_pairs={len(edges)} "
        f"d4_swap_orbits={len(representatives)}")


if __name__ == "__main__":
    main()
