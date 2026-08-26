#!/usr/bin/env python3
"""Print one lexicographically least D4 image of each input hex cap."""

from __future__ import annotations

import pathlib
import sys


def transform(mask: int, symmetry: int) -> int:
    result = 0
    for point in range(121):
        if not (mask >> point) & 1:
            continue
        x, y = divmod(point, 11)
        images = (
            (x, y),
            (x, 10 - y),
            (10 - x, y),
            (10 - x, 10 - y),
            (y, x),
            (y, 10 - x),
            (10 - y, x),
            (10 - y, 10 - x),
        )
        xx, yy = images[symmetry]
        result |= 1 << (11 * xx + yy)
    return result


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: canonicalize_caps.py CAPS_HEX_FILE")
    masks = {
        int(line, 16)
        for line in pathlib.Path(sys.argv[1]).read_text(encoding="ascii").splitlines()
        if line
    }
    canonical = sorted(min(transform(mask, s) for s in range(8)) for mask in masks)
    canonical = sorted(set(canonical))
    for mask in canonical:
        print(f"{mask:031x}")


if __name__ == "__main__":
    main()
