#!/usr/bin/env python3
"""Reviewer-facing exhaustive reconstruction of the frozen size-22 catalogue.

This wrapper is repository-authored. It does not replace the frozen generator or
canonicalizer; it only gives them stable repository-relative paths and checks
that their outputs are byte-identical to the frozen data committed under
``g11/R/data``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
R_ROOT = HERE.parents[1]
GENERATOR = HERE / "enumerate_caps.cpp"
CANONICALIZER = R_ROOT / "source" / "caps" / "canonicalize_caps.py"
FROZEN_CAPS = R_ROOT / "data" / "caps22_diag_independent.hex"
FROZEN_D4 = R_ROOT / "data" / "caps22_d4.hex"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compiler() -> str:
    candidates = [os.environ.get("CXX"), "clang++", "g++", "c++"]
    for candidate in candidates:
        if candidate and shutil.which(candidate):
            return candidate
    raise SystemExit("No C++20 compiler found (tried CXX, clang++, g++, c++).")


def main() -> None:
    for path in (GENERATOR, CANONICALIZER, FROZEN_CAPS, FROZEN_D4):
        if not path.is_file():
            raise SystemExit(f"missing required file: {path}")

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        executable = tmp / "enumerate_caps"
        subprocess.run(
            [compiler(), "-O3", "-std=c++20", str(GENERATOR), "-o", str(executable)],
            check=True,
        )
        generated = subprocess.run(
            [str(executable), "22", "-1", "emit"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        summary = generated.stderr.decode("ascii").strip()
        if "oriented_solutions 1120" not in summary:
            raise AssertionError(f"unexpected generator total: {summary}")
        if "meets_long_diagonals 676" not in summary:
            raise AssertionError(f"unexpected diagonal-feasible total: {summary}")

        frozen_caps = FROZEN_CAPS.read_bytes()
        if generated.stdout != frozen_caps:
            raise AssertionError("generated 676-cap catalogue is not byte-identical to frozen data")

        canonical = subprocess.run(
            [sys.executable, str(CANONICALIZER), str(FROZEN_CAPS)],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        frozen_d4 = FROZEN_D4.read_bytes()
        if canonical != frozen_d4:
            raise AssertionError("generated D4 catalogue is not byte-identical to frozen data")

        caps_lines = generated.stdout.count(b"\n")
        d4_lines = canonical.count(b"\n")
        if caps_lines != 676 or d4_lines != 89:
            raise AssertionError((caps_lines, d4_lines))

        print(summary)
        print(
            "CATALOGUE_RECONSTRUCTION_PASS "
            f"caps={caps_lines} caps_sha256={sha256_bytes(generated.stdout)} "
            f"d4_orbits={d4_lines} d4_sha256={sha256_bytes(canonical)} "
            "caps_byte_identical=yes d4_byte_identical=yes"
        )


if __name__ == "__main__":
    main()
