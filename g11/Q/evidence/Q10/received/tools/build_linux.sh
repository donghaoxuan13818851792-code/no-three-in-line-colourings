#!/usr/bin/env bash
set -euo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT="$ROOT/build/linux"
CXX=${CXX:-c++}
mkdir -p "$OUT"
"$CXX" -O3 -std=c++20 "$ROOT/work/solver_agent/q10_cap20_enum.cpp" -o "$OUT/q10_cap20_enum"
"$CXX" -O3 -std=c++20 "$ROOT/work/solver_agent/q10_cap20_catalogue_audit.cpp" -o "$OUT/q10_cap20_catalogue_audit"
"$CXX" -O3 -std=c++20 "$ROOT/work/math_agent/nonextendible_structure/capset_join.cpp" -o "$OUT/capset_join"
printf 'Linux production binaries built in %s\n' "$OUT"
