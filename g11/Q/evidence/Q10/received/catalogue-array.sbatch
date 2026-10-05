#!/usr/bin/env bash
#SBATCH --job-name=q10-cat
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=16G
#SBATCH --time=24:00:00
#SBATCH --array=0-83%83
#SBATCH --output=logs/q10-cat-%A_%a.out
#SBATCH --error=logs/q10-cat-%A_%a.err

set -euo pipefail

: "${Q10_ROOT:?}"
: "${Q10_RUN_BASE:?}"

# 84 representatives requiring catalogues:
# skip rep 1, whose catalogue is supplied;
# skip completed reps 17, 53, 76 and 88.
REPS=(0 {2..16} {18..52} {54..75} {77..87})
REP=${REPS[$SLURM_ARRAY_TASK_ID]}

export Q10_REP="$REP"
export Q10_RUN_DIR="$Q10_RUN_BASE/rep${REP}_catalogue"
export Q10_JOBS="$SLURM_CPUS_PER_TASK"
export Q10_SECONDS=1200

exec bash "$Q10_ROOT/slurm/catalogue_resume.sbatch"
