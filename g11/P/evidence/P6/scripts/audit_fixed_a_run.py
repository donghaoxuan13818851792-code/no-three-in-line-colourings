#!/usr/bin/env python3
"""Audit received fixed-A evidence. This does not prove candidate completeness.

Usage: python3 audit_fixed_a_run.py /path/to/P6_RESEARCH_HANDOFF_PACKAGE
The original handoff verifier is intentionally retained without modification.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

FULL = (1 << 121) - 1
FAMILY = Path('ultra_frozen/optional_prior_work/fixed_A_reuse')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def json_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def canonical_pair(a, b):
    # Generate the D4 orbit by successive rotation and reflection, without
    # depending on the received driver's transform numbering.
    def rotation(m):
        return sum(1 << (11 * (q % 11) + 10 - q // 11)
                   for q in range(121) if m >> q & 1)

    def reflection(m):
        return sum(1 << (11 * (q // 11) + 10 - q % 11)
                   for q in range(121) if m >> q & 1)

    pairs = []
    for _ in range(4):
        pairs.extend([tuple(sorted((a, b))),
                      tuple(sorted((reflection(a), reflection(b))))])
        a, b = rotation(a), rotation(b)
    return min(pairs)


def audit(root):
    require(root.is_dir(), 'missing extracted handoff root')
    run = root / 'runs/apocrita_fixed_A_full'
    summary = json.loads((run / 'branch_summary.json').read_text())
    bound_files = {
        'input_ledger': 'inputs/fixed_first_after_q89_maximality.tsv',
        'candidate_source': 'src/p6_fixed_a_candidate_chunk64.cpp',
        'candidate_binary': 'bin/build/p6_fixed_a_candidate_family_gcc',
        'backend_source': 'src/p6_residual_solver_candidate_input.cpp',
        'backend_binary': 'bin/build/p6_residual_solver_candidate_input_gcc',
        'witness_verifier': 'scripts/verify_p6_witness.py',
    }
    for key, name in bound_files.items():
        require(digest(root / FAMILY / name) == summary[key + '_sha256'],
                'summary hash mismatch: ' + key)
    require(digest(run / 'decision_ledger.jsonl') == summary['decision_ledger_sha256'],
            'decision ledger hash mismatch')
    print('SOURCE_INPUT_BINARY_HASH_BINDING_PASS files=7', flush=True)

    # Record exactly how the received stale manifest differs. A mismatch is
    # reported, not rewritten or silently accepted as a supplied-verifier pass.
    manifest = {}
    for line in (root / 'HANDOFF_SHA256SUMS').read_text().splitlines():
        checksum, name = line.split(maxsplit=1)
        name = name.removeprefix('*').removeprefix('./')
        require(name not in manifest, 'duplicate manifest path')
        manifest[name] = checksum
    actual = {}
    for p in root.rglob('*'):
        require(not p.is_symlink(), 'symlink in handoff')
        if p.is_file() and p.name != 'HANDOFF_SHA256SUMS' and not p.is_relative_to(root / 'build'):
            actual[p.relative_to(root).as_posix()] = digest(p)
    missing = sorted(manifest.keys() - actual.keys())
    changed = sorted(name for name in manifest.keys() & actual.keys()
                     if manifest[name] != actual[name])
    added = sorted(actual.keys() - manifest.keys())
    print('RECEIVED_MANIFEST_DIFF ' + json.dumps({
        'listed': len(manifest), 'actual': len(actual), 'added': len(added),
        'missing': missing, 'changed': changed}, sort_keys=True), flush=True)
    require(not missing and not changed, 'received previously manifested content changed')

    with (root / FAMILY / bound_files['input_ledger']).open(newline='') as f:
        inputs = list(csv.DictReader(f, delimiter='\t'))
    decisions = json_rows(run / 'decision_ledger.jsonl')
    pairs = json_rows(run / 'pair_records.jsonl')
    n = len(inputs)
    require(n == 10787 and len(decisions) == n and len(pairs) == n, 'wrong ledger cardinality')
    ids = ['fixedA-rank' + f'{int(x["rank"]):05d}' for x in inputs]
    require(len(set(ids)) == n, 'duplicate input identity')
    require([x['source_record_id'] for x in decisions] == ids, 'decision coverage/order mismatch')
    require([x['source_record_id'] for x in pairs] == ids, 'pair coverage/order mismatch')
    require(len({x['cap_hex'] for x in inputs}) == n, 'duplicate fixed-orientation B cap')
    chunks = sorted((run / 'chunks').iterdir())
    require(len(chunks) == 169, 'wrong chunk count')
    batch_candidates = batch_nodes = batch_unique = candidates = 0
    canonical_keys = set()
    for ci, chunk in enumerate(chunks):
        require(chunk.name == f'chunk-{ci:05d}-source-source', 'unexpected chunk identity')
        low, high = ci * 64, min((ci + 1) * 64, n)
        members = [line.split('\t') for line in (chunk / 'chunk.tsv').read_text().splitlines()]
        require(len(members) == high - low, 'chunk membership count')
        require((chunk / 'candidate_batch.exit').read_text().strip() == '0', 'nonterminal candidate batch')
        require(not (chunk / 'candidate_batch.stderr').read_bytes(), 'candidate batch stderr')
        stdout = (chunk / 'candidate_batch.stdout').read_text()
        m = re.search(r'^CANDIDATE_BATCH_COMPLETE records (\d+) nodes (\d+) leaves \d+ unique_leaf_caps (\d+) candidate_occurrences (\d+) ', stdout)
        require(m is not None and int(m[1]) == high - low, 'candidate batch summary')
        batch_nodes += int(m[2])
        batch_unique += int(m[3])
        batch_candidates += int(m[4])
        counts = re.findall(r'^RECORD (\d+) (\S+) candidates (\d+)$', stdout, re.M)
        require(len(counts) == high - low, 'candidate stdout record universe')
        for offset, i in enumerate(range(low, high)):
            inp, decision, pair, sid = inputs[i], decisions[i], pairs[i], ids[i]
            a = int(summary['first_a_hex'], 16)
            b, r = int(inp['cap_hex'], 16), int(inp['residual_hex'], 16)
            require(a.bit_count() == b.bit_count() == 21 and r.bit_count() == 79
                    and a & b == a & r == b & r == 0 and a | b | r == FULL,
                    'input partition: ' + sid)
            expected_member = [f'{a:031x}', f'{b:031x}', f'{r:031x}', sid]
            require(members[offset] == expected_member, 'chunk membership binding: ' + sid)
            require([pair['original_a_hex'], pair['original_b_hex'], pair['original_residual_hex']] == expected_member[:3], 'pair original masks: ' + sid)
            ca, cb = canonical_pair(a, b)
            key = hashlib.sha256(f'{ca:031x}\t{cb:031x}\n'.encode()).hexdigest()
            require(pair['canonical_a_hex'] == f'{ca:031x}' and pair['canonical_b_hex'] == f'{cb:031x}'
                    and pair['residual_hex'] == f'{FULL ^ ca ^ cb:031x}'
                    and pair['pair_key_sha256'] == key and pair['pair_id'] == 'p6pair-' + key[:24],
                    'D4/pair-swap binding: ' + sid)
            canonical_keys.add(key)
            require(decision['terminal'] is True and decision['exit_code'] == 20
                    and decision['status'] == 'UNSAT_P6_RESIDUAL' and decision['family_chunk'] == ci,
                    'nonterminal decision: ' + sid)
            require(decision['representative_residual_hex'] == f'{r:031x}'
                    and decision['equivalence_key'] == 'exact-residual:' + f'{r:031x}', 'decision residual: ' + sid)
            require(json.loads((run / 'records' / (sid + '.json')).read_text()) == decision,
                    'individual decision mismatch: ' + sid)
            pg = run / 'pairgrids' / (sid + '.pairgrid')
            expected_grid = ''.join(('1' if a >> q & 1 else '2' if b >> q & 1 else '0') + '\n' for q in range(121)).encode()
            require(pg.read_bytes() == expected_grid and digest(pg) == decision['input_sha256'], 'pairgrid binding: ' + sid)
            require(decision['solver_source_sha256'] == summary['backend_source_sha256']
                    and decision['solver_binary_sha256'] == summary['backend_binary_sha256'], 'backend binding: ' + sid)
            candidate = chunk / 'candidates' / (sid + '.tsv')
            require(digest(candidate) == decision['candidate_ledger_sha256'], 'candidate hash: ' + sid)
            count, previous = 0, -1
            with candidate.open() as f:
                require(next(f).strip() == 'mask\tsingleton_rows\tsingleton_cols', 'candidate header')
                for line in f:
                    fields = line.rstrip('\n').split('\t')
                    require(len(fields) == 3, 'candidate record shape')
                    mask = int(fields[0], 16)
                    require(len(fields[0]) == 31 and mask > previous and mask.bit_count() == 20
                            and mask & ~r == 0 and all(0 <= int(v) < 2048 for v in fields[1:]),
                            'candidate membership/order: ' + sid)
                    previous = mask
                    count += 1
            require(count == decision['candidate_count'] and counts[offset] == (str(offset), sid, str(count)), 'candidate counts: ' + sid)
            candidates += count
            backend = chunk / 'backend' / sid
            result = backend.with_suffix('.stdout')
            require(backend.with_suffix('.exit').read_text().strip() == '20'
                    and not backend.with_suffix('.stderr').read_bytes()
                    and result.read_text().startswith('UNSAT_P6_RESIDUAL ')
                    and digest(result) == decision['result_sha256'], 'terminal log binding: ' + sid)
        if (ci + 1) % 32 == 0:
            print(f'CHUNKS_CHECKED {ci + 1}/169', flush=True)
    for key, value in {'declared_pair_count': n, 'input_total_pair_count': n,
                       'UNSAT_count': n, 'SAT_count': 0, 'ERROR_count': 0, 'INCOMPLETE_count': 0,
                       'completed_candidate_chunks': 169, 'planned_chunks': 169,
                       'candidate_occurrences': candidates, 'shared_candidate_nodes': batch_nodes,
                       'chunk_unique_leaf_caps_sum': batch_unique}.items():
        require(summary[key] == value, 'branch summary mismatch: ' + key)
    require(summary['terminal'] is True and summary['historical_fixed_oriented'] is True
            and summary['chunk_size'] == 64 and candidates == batch_candidates, 'branch terminal scope')
    print('FIXED_A_EVIDENCE_AUDIT_PASS ' + json.dumps({
        'fixed_orientation_inputs': n, 'canonical_pair_keys': len(canonical_keys),
        'chunks': len(chunks), 'candidate_occurrences': candidates,
        'terminal_unsat': n, 'global_P6': 'INCOMPLETE',
        'candidate_enumeration_replayed': False, 'independent_UNSAT_proof': False}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('handoff_root', type=Path)
    args = parser.parse_args()
    try:
        audit(args.handoff_root.resolve())
    except (ValueError, OSError, KeyError, StopIteration) as error:
        raise SystemExit('FAIL: ' + str(error))
