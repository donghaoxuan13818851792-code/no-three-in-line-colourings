#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$ROOT/bin/build"
CXXFLAGS=(-O3 -DNDEBUG -std=c++20 -Wall -Wextra -pedantic)
g++ "${CXXFLAGS[@]}" "$ROOT/src/p6_fixed_a_candidate_chunk64.cpp" -o "$ROOT/bin/build/p6_fixed_a_candidate_family_gcc"
g++ "${CXXFLAGS[@]}" "$ROOT/src/p6_residual_solver_candidate_input.cpp" -o "$ROOT/bin/build/p6_residual_solver_candidate_input_gcc"
g++ "${CXXFLAGS[@]}" "$ROOT/src/p6_residual_solver_agent1.cpp" -o "$ROOT/bin/build/p6_residual_solver_agent1_gcc"
g++ "${CXXFLAGS[@]}" "$ROOT/src/p6_pair_binary_nae_audit.cpp" -o "$ROOT/bin/build/p6_pair_binary_nae_audit_gcc"
if command -v clang++ >/dev/null 2>&1; then
  clang++ "${CXXFLAGS[@]}" "$ROOT/src/p6_fixed_a_candidate_chunk64.cpp" -o "$ROOT/bin/build/p6_fixed_a_candidate_family_clang"
  clang++ "${CXXFLAGS[@]}" "$ROOT/src/p6_residual_solver_candidate_input.cpp" -o "$ROOT/bin/build/p6_residual_solver_candidate_input_clang"
fi
if [[ ${SANITIZE:-0} == 1 ]]; then
  SAN=(-O1 -g -std=c++20 -fsanitize=address,undefined -fno-omit-frame-pointer)
  g++ "${SAN[@]}" "$ROOT/src/p6_fixed_a_candidate_chunk64.cpp" -o "$ROOT/bin/build/p6_fixed_a_candidate_family_asan_ubsan"
  g++ "${SAN[@]}" "$ROOT/src/p6_residual_solver_candidate_input.cpp" -o "$ROOT/bin/build/p6_residual_solver_candidate_input_asan_ubsan"
fi
sha256sum "$ROOT/bin/build/"* > "$ROOT/bin/build/BINARY_HASHES.sha256"
echo BUILD_PASS
