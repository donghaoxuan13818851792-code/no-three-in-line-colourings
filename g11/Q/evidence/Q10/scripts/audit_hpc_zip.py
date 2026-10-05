#!/usr/bin/env python3
"""Audit Q10 HPC primary coverage directly from the delivered ZIP.

Uses the complete file hash index from run_zip_manifest_verifier.py. Catalogue
unions, immutable run identities, all shard records and terminal join logs are
checked. Saved geometry audits are primary records, not fresh proof replay.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import zipfile

REP_PATH = 'work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex'
REP_SHA = '234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40'
LEGACY = {17, 53, 76, 88}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('hash_index', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for line in args.hash_index.read_text().splitlines():
        row = json.loads(line)
        require(row['path'] not in hashes, 'duplicate file hash index path')
        hashes[row['path']] = row
    with zipfile.ZipFile(args.archive) as z:
        prefix = 'Q10_HPC_HANDOFF_PACKAGE/'
        entries = {i.filename[len(prefix):]: i for i in z.infolist()
                   if i.filename.startswith(prefix) and not i.is_dir()}
        expected_index = {n for n in entries if Path(n).name != 'HANDOFF_SHA256SUMS'
                          and not n.startswith('build/')}
        require(set(hashes) == expected_index, 'incomplete full-archive hash index')

        def read(name):
            return z.read(entries[name])

        def obj(name):
            return json.loads(read(name))

        def sha(name):
            return hashes[name]['sha256'] if name in hashes else hashlib.sha256(read(name)).hexdigest()

        missing_bindings = []
        def bind(path, value):
            if 'Q10_HPC_HANDOFF_PACKAGE/' in path:
                name = path.split('Q10_HPC_HANDOFF_PACKAGE/', 1)[1]
            elif '/work/' in path:
                # The earlier Mac run predates the collaborator root. Keep
                # its work/ suffix and demand exact byte identity.
                name = 'work/' + path.split('/work/', 1)[1]
            elif path.endswith('/capset_join'):
                # The supplied Slurm scripts copy build/linux/capset_join to
                # node-local /tmp. A relocated copy is accepted only by hash.
                name = 'build/linux/capset_join'
            else:
                name = path
            if name not in entries:
                missing_bindings.append({'recorded_path': path, 'sha256': value})
                return False
            require(sha(name) == value, 'source/binary binding mismatch: ' + name)
            return True

        manifest = {}
        for line in read('HANDOFF_SHA256SUMS').decode().splitlines():
            value, name = line.split(maxsplit=1)
            name = name.removeprefix('*').removeprefix('./')
            require(name not in manifest, 'duplicate received manifest entry')
            manifest[name] = value
        missing = sorted(manifest.keys() - hashes.keys())
        changed = sorted(n for n in manifest.keys() & hashes.keys() if sha(n) != manifest[n])
        added = sorted(hashes.keys() - manifest.keys())
        diff = {'manifested': len(manifest), 'indexed_files': len(hashes),
                'added': len(added), 'missing': missing, 'changed': changed}
        (args.output_directory / 'received_manifest_diff.json').write_text(json.dumps(diff, indent=2) + '\n')
        require(not missing and not changed, 'previously manifested evidence changed or missing')
        require(sha(REP_PATH) == REP_SHA, 'frozen outer representatives hash')
        reps = read(REP_PATH).decode().splitlines()
        require(len(reps) == len(set(reps)) == 89, 'outer representative universe')
        print('ARCHIVE_AND_FROZEN_INPUT_BINDING_PASS ' + json.dumps(diff), flush=True)

        ledger = []
        failures = []
        catalogues = {}
        total_records = total_masks = total_join_shards = 0
        for rep in range(89):
            if rep in LEGACY:
                if rep == 53:
                    meta = obj('work/math_agent/nonextendible_structure/rep53_result_audit.json')
                    require(meta['status'] == 'PASS', 'legacy rep53 audit status')
                else:
                    meta = obj(f'work/math_agent/nonextendible_structure/rep{rep}_result_meta.json')
                    require(meta['anchor_hex'] == reps[rep] and meta['mathematical_status'] == f'REPRESENTATIVE_{rep}_UNSAT', 'legacy fixed-anchor identity')
                ledger.append({'representative': rep, 'anchor': reps[rep],
                               'scope': 'legacy_fixed_anchor', 'primary_status': 'LEGACY_AUDIT_RETAINED',
                               'note': 'full legacy handoff verifier passed separately; all manifested bytes unchanged'})
                continue
            cat = 'work/solver_agent/cap20_rep1_runner_v1' if rep == 1 else f'runs/rep{rep}_catalogue'
            join = f'runs/rep{rep}_join'
            try:
                result = obj(cat + '/result.json')
                meta = obj(cat + '/run.meta.json')
                identity = meta['identity']
                identity_hash = hashlib.sha256((json.dumps(identity, sort_keys=True, separators=(',', ':')) + '\n').encode()).hexdigest()
                require(identity_hash == meta['identity_sha256'] == result['run_identity_sha256'], 'catalogue identity digest')
                require(identity['anchor_hex'] == reps[rep] and identity['fixture_mode'] is False
                        and identity['expected_key_count'] == 3025, 'catalogue anchor/scope')
                require(result['status'] == 'COMPLETE_AUDITED' and result['fixture_mode'] is False and result['records'] == 3025, 'nonterminal catalogue result')
                for key in ('generator', 'generator_source', 'auditor', 'caps', 'summarizer', 'shard_auditor'):
                    item = identity[key]
                    require(item is not None, 'missing source provenance')
                    bind(item['path'], item['sha256'])
                bind('work/solver_agent/run_cap20_catalogue.py', identity['runner_sha256'])
                catalogue_path = cat + '/all_masks.hex'
                require(sha(catalogue_path) == result['catalogue_sha256']
                        and sha(cat + '/shards.log') == result['log_sha256'], 'catalogue/log hash')
                record_names = {n for n in entries if n.startswith(cat + '/records/') and n.endswith('.json')}
                expected_names = {f'{cat}/records/{rp:02d}_{cp:02d}.json' for rp in range(55) for cp in range(55)}
                require(record_names == expected_names, 'catalogue record universe')
                emitted = []
                log_lines = []
                for rp in range(55):
                    for cp in range(55):
                        record = obj(f'{cat}/records/{rp:02d}_{cp:02d}.json')
                        require(record['row_pair'] == rp and record['col_pair'] == cp
                                and record['run_identity_sha256'] == identity_hash
                                and record['status'] == 'COMPLETE' and record['exit_code'] == 0
                                and record['stderr'] == '' and record['stdout'].startswith('COMPLETE count '), 'nonterminal/wrong catalogue shard')
                        command = record['command']
                        require(command[0] == identity['generator']['path'], 'catalogue command executable')
                        for flag, value in (('--anchor', reps[rep]), ('--row-pair', str(rp)),
                                            ('--col-pair', str(cp)), ('--caps', identity['caps']['path'])):
                            require(command.count(flag) == 1 and command[command.index(flag) + 1] == value, 'catalogue command input')
                        log_lines.append(f'{rp},{cp},{record["stdout"]},exit=0\n')
                        shard = f'{cat}/shards/{rp:02d}_{cp:02d}.hex'
                        data = read(shard)
                        masks = data.splitlines()
                        info = record['mask_file']
                        require(sha(shard) == info['sha256'] and len(data) == info['bytes']
                                and len(masks) == info['lines'] == record['parsed']['count'], 'catalogue shard output binding')
                        require(record['parsed']['count'] == record['parsed']['extendible'] + record['parsed']['nonextendible'], 'catalogue shard classification sum')
                        emitted.extend(masks)
                require(hashlib.sha256(''.join(log_lines).encode()).hexdigest() == result['log_sha256'], 'catalogue log/record equality')
                emitted.sort()
                require(all(len(m) == 31 and re.fullmatch(b'[0-9a-f]{31}', m) for m in emitted)
                        and all(a < b for a, b in zip(emitted, emitted[1:])), 'catalogue mask shape/duplicate')
                union = b''.join(m + b'\n' for m in emitted)
                require(hashlib.sha256(union).hexdigest() == result['catalogue_sha256']
                        and len(emitted) == result['catalogue_masks'], 'catalogue sorted shard union')
                count = len(emitted)
                total_records += 3025
                total_masks += count
                catalogues[rep] = {'catalogue_masks': count, 'catalogue_sha256': result['catalogue_sha256'],
                                   'run_identity_sha256': identity_hash}
                del emitted, union

                meta_path = join + '/run.meta'
                join_meta = dict(line.split(maxsplit=1) for line in read(meta_path).decode().splitlines())
                audit = obj(join + '/audit.json')
                require(join_meta['anchor'] == reps[rep] == audit['anchor_hex'], 'join anchor')
                require(join_meta['caps_sha256'] == audit['catalogue_sha256'] == result['catalogue_sha256']
                        and int(join_meta['caps_count']) == audit['candidate_count'] == count, 'join catalogue binding')
                require(sha(meta_path) == audit['run_metadata_sha256'], 'join run metadata hash')
                require(join_meta['binary_sha256'] == audit['join_binary_sha256'], 'join binary identity')
                bind(join_meta['binary'], join_meta['binary_sha256'])
                require(audit['status'] == 'PASS' and audit['mathematical_status'] == 'UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE'
                        and audit['exit_code_histogram'] == {'20': 55}, 'nonterminal join audit')
                rows = audit['shard_ledger']
                require([r['root_row_pair'] for r in rows] == list(range(55)), 'join root-pair coverage')
                aggregate = collections.Counter()
                for rp, row in enumerate(rows):
                    stem = f'{join}/{rp:02d}'
                    fields = dict(line.split(maxsplit=1) for line in read(stem + '.out').decode().splitlines() if len(line.split(maxsplit=1)) == 2)
                    require(row['status'] == fields['status'] == 'COMPLETE_NO_WITNESS'
                            and row['exit_code'] == int(read(stem + '.exit')) == 20
                            and fields['anchor'] == reps[rep] and int(fields['root_row_pair']) == rp
                            and int(fields['candidate_count']) == count, 'nonterminal join shard')
                    for suffix, key in (('.out', 'stdout_sha256'), ('.time', 'resource_log_sha256'), ('.exit', 'exit_file_sha256')):
                        require(sha(stem + suffix) == row[key], 'join shard log hash')
                    for key in ('roots_examined', 'pair_candidates', 'triple_candidates', 'final_pool_candidates'):
                        require(row[key] == int(fields[key]), 'join counters differ from audit')
                    for key in audit['aggregate']:
                        aggregate[key] += int(fields[key])
                require(dict(aggregate) == audit['aggregate'], 'join aggregate counters')
                total_join_shards += 55
                ledger.append({'representative': rep, 'anchor': reps[rep], 'scope': 'HPC_catalogue_and_join',
                               'primary_status': 'PRIMARY_TERMINAL_RECORDS_PASS', 'catalogue_shards': 3025,
                               'catalogue_masks': count, 'catalogue_sha256': result['catalogue_sha256'],
                               'join_shards': 55, 'join_audit_sha256': sha(join + '/audit.json'),
                               'join_binary_sha256': join_meta['binary_sha256']})
                print(f'Q10_REP_PRIMARY_PASS {rep} catalogue_masks={count} joins=55', flush=True)
            except (ValueError, KeyError) as error:
                failures.append({'representative': rep, 'error': str(error)})
                ledger.append({'representative': rep, 'anchor': reps[rep], 'primary_status': 'AUDIT_GAP', 'error': str(error)})
                print(f'Q10_REP_AUDIT_GAP {rep}: {error}', flush=True)
        unique_missing = list({(r['recorded_path'], r['sha256']): r for r in missing_bindings}.values())
        report = {'representatives': 89, 'legacy_fixed_anchors': sorted(LEGACY),
                  'new_terminal_representatives': sum(r['primary_status'] == 'PRIMARY_TERMINAL_RECORDS_PASS' for r in ledger),
                  'catalogue_records_checked': total_records, 'catalogue_masks_in_unions': total_masks,
                  'new_join_shards_checked': total_join_shards, 'failures': failures,
                  'missing_source_or_binary_bindings': unique_missing, 'manifest_diff': diff,
                  'fresh_geometry_audit': False, 'enumeration_or_join_search_replayed': False,
                  'full_DRAT_IDRUP_replay': False, 'independent_global_UNSAT_verification': False}
        (args.output_directory / 'representative_ledger.json').write_text(json.dumps(ledger, indent=2) + '\n')
        (args.output_directory / 'hpc_zip_audit.json').write_text(json.dumps(report, indent=2) + '\n')
        print(('Q10_HPC_PRIMARY_AUDIT_PASS ' if not failures else 'Q10_HPC_PRIMARY_AUDIT_WITH_GAPS ') + json.dumps(report, sort_keys=True))
        return int(bool(failures))


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        raise SystemExit('FAIL: ' + str(error))
