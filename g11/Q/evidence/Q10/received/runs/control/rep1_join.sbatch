#!/usr/bin/env bash
#SBATCH --job-name=q10-rep1-join
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --output=/data/home/ahw807/Q10_HPC_HANDOFF_PACKAGE/runs/logs/rep1-join-%j.out
#SBATCH --error=/data/home/ahw807/Q10_HPC_HANDOFF_PACKAGE/runs/logs/rep1-join-%j.err

set -euo pipefail
export LC_ALL=C

ROOT=/data/home/ahw807/Q10_HPC_HANDOFF_PACKAGE
CAT="$ROOT/work/solver_agent/cap20_rep1_runner_v1/all_masks.hex"
CAT_RESULT="$ROOT/work/solver_agent/cap20_rep1_runner_v1/result.json"
OUT="$ROOT/runs/rep1_join"

REP=1
JOBS=16
SECONDS_PER_SHARD=7200

ANCHOR_FILE="$ROOT/work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex"
AUDITOR="$ROOT/work/math_agent/nonextendible_structure/audit_join_shards.py"
SOURCE_BINARY="$ROOT/build/linux/capset_join"

# Refuse to run unless the supplied rep1 catalogue passed its audit.
jq -e '.status == "COMPLETE_AUDITED"' "$CAT_RESULT" >/dev/null

test -f "$CAT"
test -x "$SOURCE_BINARY"
test -f "$AUDITOR"
test -f "$ANCHOR_FILE"

/usr/bin/time --version 2>&1 | grep -q GNU || {
    echo "ERROR: GNU /usr/bin/time is required"
    exit 1
}

EXEC_ROOT=${SLURM_TMPDIR:-/tmp}
EXEC="$EXEC_ROOT/q10-rep1-$SLURM_JOB_ID"

mkdir -p "$EXEC"
mkdir -p "$OUT"

cp "$SOURCE_BINARY" "$EXEC/capset_join"
chmod +x "$EXEC/capset_join"
BIN="$EXEC/capset_join"

ANCHOR=$(sed -n "$((REP + 1))p" "$ANCHOR_FILE")
test -n "$ANCHOR"

CAPS_SHA=$(sha256sum "$CAT" | awk '{print $1}')
CAPS_COUNT=$(wc -l < "$CAT" | tr -d ' ')
BINARY_SHA=$(sha256sum "$BIN" | awk '{print $1}')

{
    echo "anchor $ANCHOR"
    echo "caps $CAT"
    echo "caps_sha256 $CAPS_SHA"
    echo "caps_count $CAPS_COUNT"
    echo "jobs $JOBS"
    echo "seconds_per_shard $SECONDS_PER_SHARD"
    echo "binary $BIN"
    echo "binary_sha256 $BINARY_SHA"
} > "$OUT/run.meta"

run_one()
{
    rp=$1
    stem=$(printf '%s/%02d' "$OUT" "$rp")
    raw="$stem.gnu-time"
    errors="$stem.stderr"

    set +e
    /usr/bin/time \
        -o "$raw" \
        -f '%e %U %S %M' \
        "$BIN" \
        --anchor "$ANCHOR" \
        --caps "$CAT" \
        --root-row-pair "$rp" \
        --seconds "$SECONDS_PER_SHARD" \
        --witness "$stem.witness.hex" \
        > "$stem.out" 2> "$errors"
    code=$?
    set -e

    if read -r real user system rss_kb < "$raw"; then
        rss_bytes=$((rss_kb * 1024))

        {
            printf '%s real %s user %s sys\n' "$real" "$user" "$system"
            printf '%s maximum resident set size\n' "$rss_bytes"

            if [[ -s "$errors" ]]; then
                cat "$errors"
            fi
        } > "$stem.time"
    else
        echo "Unable to read GNU time output" > "$stem.time"
    fi

    echo "$code" > "$stem.exit"
    rm -f "$raw" "$errors"
}

export OUT BIN ANCHOR CAT SECONDS_PER_SHARD
export -f run_one

seq 0 54 | xargs -P "$JOBS" -n 1 bash -c 'run_one "$0"'

python3 "$AUDITOR" \
    --directory "$OUT" \
    --caps "$CAT" \
    --binary "$BIN" \
    --json "$OUT/audit.json" \
    > "$OUT/audit.stdout"

jq \
    '{status, mathematical_status, maximum_shard_search_seconds, resources}' \
    "$OUT/audit.json"
