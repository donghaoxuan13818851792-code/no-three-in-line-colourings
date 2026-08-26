#!/usr/bin/env python3
"""Audit the disjointness graph of diagonal-feasible size-22 caps."""

from __future__ import annotations

import argparse
import itertools
import pathlib
import subprocess
import tempfile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "caps", nargs="?", type=pathlib.Path,
        default=pathlib.Path("work/math_agent/caps22_diag.hex"))
    parser.add_argument(
        "--full", action="store_true",
        help="recompile/rerun the exhaustive cap generator and require "
             "byte-identical output before checking the graph")
    args = parser.parse_args()
    path = args.caps
    if args.full:
        source = pathlib.Path("work/math_agent/enumerate_caps.cpp")
        with tempfile.TemporaryDirectory() as directory:
            executable = pathlib.Path(directory) / "enumerate_caps"
            subprocess.run(
                ["clang++", "-O3", "-std=c++20", str(source),
                 "-o", str(executable)],
                check=True)
            generated = subprocess.run(
                [str(executable), "22", "-1", "emit"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert generated.stdout == path.read_bytes()
        summary = generated.stderr.decode("ascii").strip()
        assert "oriented_solutions 1120" in summary
        assert "meets_long_diagonals 676" in summary
        print("generator", summary)

    caps = [int(line, 16) for line in path.read_text(encoding="ascii").splitlines()]
    assert len(caps) == len(set(caps)) == 676
    for cap in caps:
        assert cap.bit_count() == 22
        points = [divmod(point, 11) for point in range(121)
                  if (cap >> point) & 1]
        assert all(sum(x == row for x, _ in points) == 2
                   for row in range(11))
        assert all(sum(y == column for _, y in points) == 2
                   for column in range(11))
        assert any(x == y for x, y in points)
        assert any(x + y == 10 for x, y in points)
        for first, second, third in itertools.combinations(points, 3):
            assert ((second[0] - first[0]) * (third[1] - first[1])
                    != (second[1] - first[1]) * (third[0] - first[0]))
    adjacency = [set() for _ in caps]
    edges = 0
    for i, first in enumerate(caps):
        for j in range(i + 1, len(caps)):
            if first & caps[j]:
                continue
            adjacency[i].add(j)
            adjacency[j].add(i)
            edges += 1
    triangles = 0
    for i in range(len(caps)):
        for j in adjacency[i]:
            if j > i:
                triangles += sum(k > j for k in adjacency[i] & adjacency[j])
    print(f"vertices {len(caps)} edges {edges} triangles {triangles}")
    assert edges == 2138
    assert triangles == 0


if __name__ == "__main__":
    main()
