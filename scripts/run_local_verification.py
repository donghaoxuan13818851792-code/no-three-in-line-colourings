#!/usr/bin/env python3
"""Run bounded-storage local checks, parallel within P123 and serial by phase.

This invokes the unchanged independent P123 verifier on 60 disjoint residue
classes. Grouping these classes modulo six preserves comparison with every
historical primary shard. Failed/unfinished runs never count as UNSAT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
TOTAL = 127491
PARTS = 60
RESERVE = 5 * 1024**3
MAX_RSS_KIB = 14 * 1024**2
FIELDS = ('first', 't2', 'p2', 't3', 'p3', 't4', 'p4', 'instances', 'sat')
INDEPENDENT = re.compile(
    r'INDEPENDENT_UNSAT123_SHARD (?P<shard>\d+) 60 first_caps (?P<first>\d+)'
    r' examined2 (?P<t2>\d+) accepted2 (?P<p2>\d+)'
    r' examined3 (?P<t3>\d+) accepted3 (?P<p3>\d+)'
    r' examined4 (?P<t4>\d+) accepted4 (?P<p4>\d+)'
    r' residual_instances (?P<instances>\d+) residual_nodes (?P<nodes>\d+)'
    r' residual_conflicts (?P<conflicts>\d+) residual_sat (?P<sat>\d+)\s*')
PRIMARY = re.compile(
    r'UNSAT123_SHARD (?P<shard>\d+) 6 first_caps (?P<first>\d+)'
    r' tested2 (?P<t2>\d+) passed2 (?P<p2>\d+)'
    r' tested3 (?P<t3>\d+) passed3 (?P<p3>\d+)'
    r' tested4 (?P<t4>\d+) passed4 (?P<p4>\d+)'
    r' residual_instances (?P<instances>\d+) residual_nodes (?P<nodes>\d+)'
    r' residual_conflicts (?P<conflicts>\d+) residual_sat (?P<sat>\d+)\s*')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def save(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def terminate_job(process):
    """Stop the job's entire process group, including native checker children."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    # The group leader can exit before a native child that ignores SIGTERM.
    # Escalate for the remaining group even when waiting on the leader succeeds.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def run_followup(task, run, env, state):
    """Own the whole follow-up job through normal return or interruption."""
    name = task['name']
    with (run / f'{name}.out').open('w') as out, (run / f'{name}.err').open('w') as err:
        process = subprocess.Popen(task['command'], cwd=task.get('cwd', str(ROOT)),
                                   stdout=out, stderr=err, env=env,
                                   start_new_session=True)
        try:
            while process.poll() is None:
                resources = guard(run)
                state.update(updated_epoch=time.time(), **resources)
                save(run / 'state.json', state)
                time.sleep(3)
            return process.returncode
        except BaseException:
            terminate_job(process)
            raise


def guard(run):
    free = shutil.disk_usage(run).free
    if free < RESERVE:
        raise RuntimeError(f'DISK_RESERVE: free={free}, reserve={RESERVE}')
    output = subprocess.check_output(['ps', '-axo', 'pid,ppid,rss'], text=True)
    rows = [tuple(map(int, line.split())) for line in output.splitlines()[1:]]
    family = {os.getpid()}
    for _ in range(5):
        family.update(pid for pid, parent, _ in rows if parent in family)
    rss = sum(rss for pid, _, rss in rows if pid in family)
    if rss > MAX_RSS_KIB:
        raise RuntimeError(f'MEMORY_RESERVE: campaign_rss_kib={rss}')
    return {'free_disk_bytes': free, 'campaign_rss_kib': rss}


def parse_progress(path):
    if not path.exists():
        return 0, None
    lines = path.read_text(errors='replace').splitlines()
    for line in reversed(lines):
        m = re.search(r'independent_progress \d+/60 first_caps (\d+).* seconds ([\d.]+)', line)
        if m:
            return int(m[1]), float(m[2])
    return 0, None


def audit_p123(run):
    build = json.loads((run / 'build.json').read_text())
    source = ROOT / 'g11/P/work/independent_agent/p123_independent_verifier.cpp'
    assert build['source_modified'] is False
    assert build['source_sha256'] == digest(source)
    assert build['included_source_sha256'] == digest(source.with_name('p1_independent_search.cpp'))
    assert build['input_hashes'] == {p.name: digest(p) for p in
        sorted((ROOT / 'g11/P/work/math_agent').glob('caps21_r*_diag.hex'))}
    groups = [{k: 0 for k in FIELDS} for _ in range(6)]
    records = []
    for shard in range(PARTS):
        stem = run / 'p123' / f'part{shard:02d}'
        assert stem.with_suffix('.status').read_text().strip() == '20', shard
        m = INDEPENDENT.fullmatch(stem.with_suffix('.out').read_text())
        assert m, shard
        values = {k: int(v) for k, v in m.groupdict().items()}
        assert values['shard'] == shard
        assert values['first'] == len(range(shard, TOTAL, PARTS))
        assert values['sat'] == 0
        count = 0
        residual = stem.with_suffix('.residuals.hex')
        with residual.open() as f:
            for line in f:
                text = line.rstrip('\n')
                assert len(text) == 31 and re.fullmatch('[0-9a-f]{31}', text)
                mask = int(text, 16)
                assert mask < 1 << 121 and mask.bit_count() == 37
                count += 1
        assert count == values['instances']
        for k in FIELDS:
            groups[shard % 6][k] += values[k]
        records.append({'shard': shard, **values, 'residual_sha256': digest(residual),
                        'out_sha256': digest(stem.with_suffix('.out')),
                        'log_sha256': digest(stem.with_suffix('.log')),
                        'status_sha256': digest(stem.with_suffix('.status'))})
    for shard, group in enumerate(groups):
        primary_path = ROOT / 'g11/P/work/sat_agent' / f'p123_full_shard{shard}.out'
        m = PRIMARY.fullmatch(primary_path.read_text())
        assert m, primary_path
        primary = {k: int(v) for k, v in m.groupdict().items()}
        for k in FIELDS:
            assert group[k] == primary[k], (shard, k, group[k], primary[k])
    assert sum(g['first'] for g in groups) == TOTAL
    assert sum(g['instances'] for g in groups) == 708638
    result = {'status': 'PASS', 'scope': 'full independent P1-P3 prefix and terminal replay',
              'first_caps': TOTAL, 'residuals': 708638, 'parts': PARTS,
              'partition': 'representative index modulo 60; grouped modulo 6',
              'primary_group_counters': groups, 'records': records}
    save(run / 'p123_audit.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=10)
    parser.add_argument('--audit-only', action='store_true',
                        help='audit an existing 60-part replay without starting searches')
    args = parser.parse_args()
    if not 1 <= args.workers <= 10:
        parser.error('--workers must be between 1 and 10')
    run = args.run.resolve()
    if args.audit_only:
        result = audit_p123(run)
        print('INDEPENDENT_P123_ALL_60_PASS', result['first_caps'], result['residuals'])
        return
    run.mkdir(parents=True, exist_ok=True)
    if (run / 'state.json').exists():
        raise SystemExit('Run directory already has state.json; use a fresh directory to preserve evidence and avoid duplicate computation.')
    (run / 'p123').mkdir(exist_ok=True)
    os.nice(5)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    started = time.time()
    state = {'pid': os.getpid(), 'started_epoch': started, 'workers': args.workers,
             'phase': 'P123', 'status': 'RUNNING', 'total_parts': PARTS,
             'completed': [], 'active': [], 'reserve_bytes': RESERVE}
    save(run / 'state.json', state)
    active = {}
    pending = list(range(PARTS))
    completed = []
    try:
        guard(run)
        source = ROOT / 'g11/P/work/independent_agent/p123_independent_verifier.cpp'
        binary = run / 'p123_independent_verifier'
        with (run / 'compile.log').open('w') as f:
            subprocess.run(['clang++', '-O3', '-std=c++20', str(source), '-o', str(binary)],
                           stdout=f, stderr=subprocess.STDOUT, check=True, env=env)
        save(run / 'build.json', {'source_sha256': digest(source),
             'included_source_sha256': digest(source.with_name('p1_independent_search.cpp')),
             'binary_sha256': digest(binary), 'source_modified': False,
             'compiler': subprocess.check_output(['clang++', '--version'], text=True),
             'input_hashes': {p.name: digest(p) for p in sorted((ROOT / 'g11/P/work/math_agent').glob('caps21_r*_diag.hex'))}})
        while pending or active:
            resources = guard(run)
            while pending and len(active) < args.workers:
                shard = pending.pop(0)
                stem = run / 'p123' / f'part{shard:02d}'
                out = stem.with_suffix('.out').open('w')
                log = stem.with_suffix('.log').open('w')
                cmd = ['/usr/bin/time', '-p', str(binary), str(shard), str(PARTS),
                       str(stem.with_suffix('.residuals.hex')),
                       str(ROOT / 'g11/P/work/math_agent')]
                p = subprocess.Popen(cmd, stdout=out, stderr=log, env=env,
                                     start_new_session=True)
                save(stem.with_suffix('.run.json'), {'command': cmd, 'pid': p.pid,
                     'started_epoch': time.time(), 'partition': {'residue': shard, 'modulus': PARTS}})
                active[shard] = (p, out, log, time.time())
            for shard, (p, out, log, begin) in list(active.items()):
                code = p.poll()
                if code is None:
                    continue
                out.close(); log.close()
                stem = run / 'p123' / f'part{shard:02d}'
                stem.with_suffix('.status').write_text(str(code) + '\n')
                times = re.findall(r'^(real|user|sys)\s+([\d.]+)$', stem.with_suffix('.log').read_text(), re.M)
                elapsed = {key: float(val) for key, val in times}
                completed.append({'shard': shard, 'exit_code': code,
                                  'wall_seconds': time.time() - begin, **elapsed})
                del active[shard]
                if code != 20:
                    raise RuntimeError(f'P123 part {shard}: exit {code}; no UNSAT completion claimed')
            state.update(updated_epoch=time.time(), completed=completed,
                         active=[{'shard': s, 'pid': p.pid,
                                  'anchors_completed': parse_progress(run / 'p123' / f'part{s:02d}.log')[0],
                                  'elapsed_seconds': time.time()-begin}
                                 for s, (p, _, _, begin) in active.items()],
                         **resources)
            save(run / 'state.json', state)
            time.sleep(3)
        state.update(phase='P123_AUDIT', active=[], updated_epoch=time.time())
        save(run / 'state.json', state)
        audit_p123(run)
        state['p123_status'] = 'PASS'
        state['phase'] = 'FOLLOWUP_CHECKS'
        save(run / 'state.json', state)
        followups = run / 'followups.json'
        state['followups'] = []
        if followups.exists():
            for task in json.loads(followups.read_text()):
                guard(run)
                name = task['name']
                state['current_task'] = name
                save(run / 'state.json', state)
                begin = time.time()
                code = run_followup(task, run, env, state)
                (run / f'{name}.status').write_text(str(code)+'\n')
                state['followups'].append({'name': name, 'exit_code': code,
                                          'wall_seconds': time.time()-begin})
                save(run / 'state.json', state)
        state.update(status='COMPUTATION_FINISHED', phase='REPORT_REVIEW',
                     updated_epoch=time.time(), wall_seconds=time.time()-started)
        save(run / 'state.json', state)
    except BaseException as exc:
        for p, out, log, _ in active.values():
            terminate_job(p)
            out.close(); log.close()
        state.update(status='STOPPED_WITH_ERROR', error=str(exc), updated_epoch=time.time())
        save(run / 'state.json', state)
        raise


if __name__ == '__main__':
    main()
