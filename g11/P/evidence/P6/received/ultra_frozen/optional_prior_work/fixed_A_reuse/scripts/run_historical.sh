#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
[[ $# -ge 1 ]] || { echo "usage: $0 OUTPUT_DIR [MAX_PAIRS]" >&2; exit 2; }
OUT=$1; MAX=${2:-0}
[[ -x "$ROOT/bin/build/p6_fixed_a_candidate_family_gcc" ]] || bash "$ROOT/scripts/build.sh"
args=(--branch "$ROOT/inputs/fixed_first_after_q89_maximality.tsv" --output-dir "$OUT" --candidate-bin "$ROOT/bin/build/p6_fixed_a_candidate_family_gcc" --candidate-source "$ROOT/src/p6_fixed_a_candidate_chunk64.cpp" --backend-bin "$ROOT/bin/build/p6_residual_solver_candidate_input_gcc" --backend-source "$ROOT/src/p6_residual_solver_candidate_input.cpp" --witness-verifier "$ROOT/scripts/verify_p6_witness.py" --chunk-size 64 --grouping source)
[[ $MAX == 0 ]] || args+=(--max-pairs "$MAX")
python3 "$ROOT/scripts/p6_fixed_a_family_driver.py" "${args[@]}"
