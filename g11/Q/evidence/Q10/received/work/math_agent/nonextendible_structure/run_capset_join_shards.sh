#!/bin/sh
# Run the 55 exact minimum-deficit-row shards of capset_join.
#
# Usage:
#   run_capset_join_shards.sh ANCHOR CAPS OUTPUT_DIR [JOBS] [SECONDS]
#
# capset_join uses exit 20 for COMPLETE_NO_WITNESS, 10 for SAT, 30 for
# INCOMPLETE, and 50 for input/error.  Each child wrapper records that code
# and itself exits zero so xargs executes all 55 independent shards.
set -eu

if [ "$#" -lt 3 ] || [ "$#" -gt 5 ]; then
  echo "usage: $0 ANCHOR CAPS OUTPUT_DIR [JOBS] [SECONDS]" >&2
  exit 2
fi

join_anchor=$1
join_caps=$2
join_output=$3
join_jobs=${4:-4}
join_seconds=${5:-1200}
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
join_binary="$script_dir/capset_join"

if [ ! -x "$join_binary" ]; then
  echo "missing executable $join_binary" >&2
  exit 2
fi
if [ ! -f "$join_caps" ]; then
  echo "missing catalogue $join_caps" >&2
  exit 2
fi
mkdir -p "$join_output"

# Store immutable run identity before dispatch.  The audit program checks it
# against the actual catalogue and all 55 result files.
join_caps_abs=$(CDPATH= cd -- "$(dirname -- "$join_caps")" && pwd)/$(basename -- "$join_caps")
join_caps_sha=$(shasum -a 256 "$join_caps_abs" | awk '{print $1}')
join_caps_count=$(wc -l < "$join_caps_abs" | tr -d ' ')
join_binary_sha=$(shasum -a 256 "$join_binary" | awk '{print $1}')
{
  echo "anchor $join_anchor"
  echo "caps $join_caps_abs"
  echo "caps_sha256 $join_caps_sha"
  echo "caps_count $join_caps_count"
  echo "jobs $join_jobs"
  echo "seconds_per_shard $join_seconds"
  echo "binary $join_binary"
  echo "binary_sha256 $join_binary_sha"
} > "$join_output/run.meta"

export join_anchor join_caps_abs join_output join_seconds join_binary
seq 0 54 | xargs -P "$join_jobs" -n 1 sh -c '
  rp=$0
  stem=$(printf "%s/%02d" "$join_output" "$rp")
  set +e
  /usr/bin/time -l "$join_binary" \
    --anchor "$join_anchor" \
    --caps "$join_caps_abs" \
    --root-row-pair "$rp" \
    --seconds "$join_seconds" \
    --witness "$stem.witness.hex" \
    > "$stem.out" 2> "$stem.time"
  code=$?
  set -e
  echo "$code" > "$stem.exit"
  exit 0
'

echo "finished 55 capset_join shards in $join_output"
