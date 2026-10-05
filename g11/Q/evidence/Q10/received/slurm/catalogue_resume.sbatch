#!/usr/bin/env bash
#SBATCH --job-name=q10-catalogue
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --output=q10-catalogue-%j.out
#SBATCH --error=q10-catalogue-%j.err
set -euo pipefail

: "${Q10_ROOT:?set Q10_ROOT to the shared handoff directory}"
: "${Q10_REP:?set Q10_REP to a zero-based representative index}"
: "${Q10_RUN_DIR:?set Q10_RUN_DIR to durable shared checkpoint storage}"
Q10_JOBS=${Q10_JOBS:-${SLURM_CPUS_PER_TASK:-16}}
Q10_SECONDS=${Q10_SECONDS:-1200}
cd "$Q10_ROOT"
if [ ! -x build/linux/q10_cap20_enum ]; then ./tools/build_linux.sh; fi
Q10_ANCHOR=$(sed -n "$((Q10_REP + 1))p" work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex)
test -n "$Q10_ANCHOR"
python3 work/solver_agent/run_cap20_catalogue.py \
  --run-dir "$Q10_RUN_DIR" --anchor "$Q10_ANCHOR" \
  --generator build/linux/q10_cap20_enum \
  --generator-source work/solver_agent/q10_cap20_enum.cpp \
  --caps work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_diag.hex \
  --auditor build/linux/q10_cap20_catalogue_audit \
  --summarizer work/solver_agent/summarize_cap20.py \
  --shard-auditor work/solver_agent/audit_cap20_shards.py \
  --jobs "$Q10_JOBS" --time-per-shard "$Q10_SECONDS"
