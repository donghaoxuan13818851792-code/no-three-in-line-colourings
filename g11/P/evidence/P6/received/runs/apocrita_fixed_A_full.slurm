#!/bin/bash

#SBATCH --job-name=p6_fixedA_full
#SBATCH --output=runs/apocrita_fixed_A_full_%j.out
#SBATCH --error=runs/apocrita_fixed_A_full_%j.err
#SBATCH --time=24:00:00
#SBATCH --mem=2G
#SBATCH --ntasks=1

set -u

cd "$SLURM_SUBMIT_DIR"

echo "Job started"
echo "Running on: $(hostname)"
echo "Working directory: $(pwd)"
echo "Start time: $(date)"

ultra_frozen/optional_prior_work/fixed_A_reuse/scripts/run_historical.sh \
    runs/apocrita_fixed_A_full

status=$?

echo "Driver exit status: $status"
echo "End time: $(date)"

exit $status
