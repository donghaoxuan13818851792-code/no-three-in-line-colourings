#!/usr/bin/env python3
"""Cross-check cap20 shard files, shard log, and aggregate catalogue."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SIDE = 11
PAIRS = [(a, b) for a in range(SIDE) for b in range(a + 1, SIDE)]
LOG_PATTERN = re.compile(
    r"^(\d+),(\d+),(COMPLETE|INCOMPLETE) count (\d+).*?"
    r"self_secant_rejects (\d+) seconds [0-9.eE+-]+,exit=(\d+)$"
)


def pair_ids(mask: int) -> tuple[int, int]:
    row_degrees = [sum((mask >> (SIDE*r+c)) & 1 for c in range(SIDE))
                   for r in range(SIDE)]
    col_degrees = [sum((mask >> (SIDE*r+c)) & 1 for r in range(SIDE))
                   for c in range(SIDE)]
    rows = tuple(i for i, degree in enumerate(row_degrees) if degree == 1)
    cols = tuple(i for i, degree in enumerate(col_degrees) if degree == 1)
    if sorted(row_degrees) != [1, 1] + [2] * 9:
        raise ValueError("bad row degree pattern")
    if sorted(col_degrees) != [1, 1] + [2] * 9:
        raise ValueError("bad column degree pattern")
    return PAIRS.index(rows), PAIRS.index(cols)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shards", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    records: dict[tuple[int, int], tuple[int, int]] = {}
    for number, line in enumerate(args.log.read_text().splitlines(), 1):
        match = LOG_PATTERN.match(line)
        if not match:
            raise SystemExit(f"malformed log line {number}")
        rp, cp, status, count, self_secants, exit_code = match.groups()
        key = int(rp), int(cp)
        if key in records:
            raise SystemExit(f"duplicate log key {key}")
        if status != "COMPLETE" or int(exit_code) != 0:
            raise SystemExit(f"nonterminal log record {key}")
        records[key] = int(count), int(self_secants)

    expected = {(rp, cp) for rp in range(55) for cp in range(55)}
    if set(records) != expected:
        raise SystemExit("log does not contain exactly the 3025 shard keys")

    emitted: list[str] = []
    for rp, cp in sorted(expected):
        path = args.shards / f"{rp:02d}_{cp:02d}.hex"
        if not path.is_file():
            raise SystemExit(f"missing shard file {path}")
        words = path.read_text().splitlines()
        if len(words) != records[rp, cp][0]:
            raise SystemExit(f"file/log count mismatch in shard {(rp, cp)}")
        for line_number, word in enumerate(words, 1):
            if not re.fullmatch(r"[0-9a-f]{31}", word):
                raise SystemExit(f"malformed mask in {path}:{line_number}")
            if pair_ids(int(word, 16)) != (rp, cp):
                raise SystemExit(f"mask in wrong shard at {path}:{line_number}")
        emitted.extend(words)

    ordered = sorted(emitted)
    if len(set(ordered)) != len(ordered):
        raise SystemExit("duplicate mask across shard files")
    catalogue = args.catalogue.read_text().splitlines()
    if catalogue != ordered:
        raise SystemExit("aggregate catalogue differs from sorted shard union")
    result = {
        "status": "SHARD_AUDIT_OK",
        "records": len(records),
        "masks": len(ordered),
        "self_secant_rejects": sum(value[1] for value in records.values()),
        "catalogue_sha256": hashlib.sha256(args.catalogue.read_bytes()).hexdigest(),
    }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(output, end="")
    if args.json:
        args.json.write_text(output)


if __name__ == "__main__":
    main()
