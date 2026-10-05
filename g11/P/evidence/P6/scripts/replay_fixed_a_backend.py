#!/usr/bin/env python3
"""Re-execute the frozen backend against received candidate lists.

Requires a freshly compiled backend and the full received handoff. This checks
candidate validity and terminal search over the supplied lists. It does not
re-enumerate those lists or independently establish their completeness.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time


def replay(root, binary, output, workers):
    run = root / 'runs/apocrita_fixed_A_full'
    decisions = [json.loads(line) for line in (run / 'decision_ledger.jsonl').read_text().splitlines()]
    output.parent.mkdir(parents=True, exist_ok=True)

    def execute(record):
        sid = record['source_record_id']
        chunk = run / 'chunks' / f'chunk-{record["family_chunk"]:05d}-source-source'
        start = time.monotonic()
        command = [str(binary), '--pair', str(run / 'pairgrids' / (sid + '.pairgrid')),
                   '--load-candidates', str(chunk / 'candidates' / (sid + '.tsv')),
                   '--out', str(output.parent / (sid + '.unexpected-witness.grid'))]
        cp = subprocess.run(command, capture_output=True, timeout=600)
        old = (chunk / 'backend' / (sid + '.stdout')).read_text().split()
        new = cp.stdout.decode().split()
        # Timing fields differ between machines; deterministic search counters
        # must match the frozen primary output.
        ignored = {'candidate_seconds', 'post_candidate_seconds', 'seconds'}
        def counters(tokens):
            return {tokens[i]: tokens[i + 1] for i in range(1, len(tokens), 2)
                    if tokens[i] not in ignored}
        passed = (cp.returncode == 20 and not cp.stderr and bool(new)
                  and new[0] == 'UNSAT_P6_RESIDUAL' and counters(new) == counters(old))
        return {'source_record_id': sid, 'exit_code': cp.returncode,
                'passed': passed, 'stdout': cp.stdout.decode(errors='replace'),
                'stderr': cp.stderr.decode(errors='replace'),
                'wall_seconds': round(time.monotonic() - start, 6)}

    start = time.monotonic()
    passed = 0
    with output.open('w') as f, ThreadPoolExecutor(max_workers=workers) as pool:
        for count, row in enumerate(pool.map(execute, decisions), 1):
            f.write(json.dumps(row, sort_keys=True) + '\n')
            passed += row['passed']
            if count % 1000 == 0:
                f.flush()
                print(f'BACKEND_REPLAY_PROGRESS {count}/{len(decisions)} passed={passed}', flush=True)
    summary = {'inputs': len(decisions), 'passed': passed,
               'failed': len(decisions) - passed, 'workers': workers,
               'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
               'replay_ledger_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
               'wall_seconds': round(time.monotonic() - start, 6),
               'candidate_enumeration_replayed': False,
               'structurally_independent_verifier': False, 'global_P6': 'INCOMPLETE'}
    output.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(('FIXED_A_BACKEND_REPLAY_PASS ' if passed == len(decisions) == 10787
           else 'FIXED_A_BACKEND_REPLAY_FAIL ') + json.dumps(summary, sort_keys=True))
    return 0 if passed == len(decisions) == 10787 else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('handoff_root', type=Path)
    parser.add_argument('fresh_binary', type=Path)
    parser.add_argument('output_ledger', type=Path)
    parser.add_argument('--workers', type=int, default=2, choices=range(1, 5))
    args = parser.parse_args()
    raise SystemExit(replay(args.handoff_root.resolve(), args.fresh_binary.resolve(),
                           args.output_ledger.resolve(), args.workers))
