#!/usr/bin/env bash
#SBATCH --job-name=q10-join
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --output=q10-join-%j.out
#SBATCH --error=q10-join-%j.err
set -euo pipefail

: "${Q10_ROOT:?set Q10_ROOT to the shared handoff directory}"
: "${Q10_REP:?set Q10_REP to a zero-based representative index}"
: "${Q10_CATALOGUE:?set Q10_CATALOGUE to COMPLETE_AUDITED all_masks.hex}"
: "${Q10_JOIN_DIR:?set Q10_JOIN_DIR to durable shared join storage}"
: "${Q10_EXEC_DIR:?set Q10_EXEC_DIR to writable temporary execution storage}"
Q10_JOBS=${Q10_JOBS:-${SLURM_CPUS_PER_TASK:-16}}
Q10_SECONDS=${Q10_SECONDS:-1200}
cd "$Q10_ROOT"
if [ ! -x build/linux/capset_join ]; then ./tools/build_linux.sh; fi
mkdir -p "$Q10_EXEC_DIR"
cp work/math_agent/nonextendible_structure/run_capset_join_shards.sh "$Q10_EXEC_DIR/"
cp build/linux/capset_join "$Q10_EXEC_DIR/capset_join"
chmod +x "$Q10_EXEC_DIR/run_capset_join_shards.sh" "$Q10_EXEC_DIR/capset_join"
Q10_ANCHOR=$(sed -n "$((Q10_REP + 1))p" work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex)
test -n "$Q10_ANCHOR"
"$Q10_EXEC_DIR/run_capset_join_shards.sh" \
  "$Q10_ANCHOR" "$Q10_CATALOGUE" "$Q10_JOIN_DIR" "$Q10_JOBS" "$Q10_SECONDS"
python3 work/math_agent/nonextendible_structure/audit_join_shards.py \
  --directory "$Q10_JOIN_DIR" --caps "$Q10_CATALOGUE" --binary "$Q10_EXEC_DIR/capset_join"
