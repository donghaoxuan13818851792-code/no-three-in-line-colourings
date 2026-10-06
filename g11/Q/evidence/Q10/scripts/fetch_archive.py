#!/usr/bin/env python3
"""Stream and verify release chunks into one exact original ZIP.

No separate chunk files are created. The destination filesystem must keep
at least 5 GB free. An interrupted download remains as .partial for inspection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    meta = json.loads((Path(__file__).resolve().parents[1] / 'archive.json').read_text())
    destination = args.destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.partial')
    if destination.exists() or temporary.exists():
        raise SystemExit('Destination or .partial already exists; choose a new destination.')
    reserve = 5_000_000_000
    if shutil.disk_usage(destination.parent).free - meta['bytes'] < reserve:
        raise SystemExit('Not enough space to retain a 5 GB reserve.')
    if sum(part['bytes'] for part in meta['parts']) != meta['bytes']:
        raise SystemExit('Malformed archive part sizes.')
    whole = hashlib.sha256()
    with temporary.open('xb') as target:
        for index, part in enumerate(meta['parts'], 1):
            checksum = hashlib.sha256()
            size = 0
            with urllib.request.urlopen(part['url'], timeout=120) as source:
                while block := source.read(1 << 20):
                    if shutil.disk_usage(destination.parent).free - len(block) < reserve:
                        raise SystemExit('5 GB reserve reached; incomplete .partial retained.')
                    size += len(block)
                    if size > part['bytes']:
                        raise SystemExit('Oversized release chunk; incomplete .partial retained.')
                    checksum.update(block)
                    whole.update(block)
                    target.write(block)
            if size != part['bytes'] or checksum.hexdigest() != part['sha256']:
                raise SystemExit('Chunk hash/size mismatch: ' + part['filename'])
            print(f'CHUNK_VERIFIED {index}/{len(meta["parts"])}', flush=True)
    if whole.hexdigest() != meta['sha256'] or temporary.stat().st_size != meta['bytes']:
        raise SystemExit('Complete archive hash/size mismatch; .partial retained.')
    temporary.rename(destination)
    print('ORIGINAL_ARCHIVE_SHA256_PASS ' + meta['sha256'])


if __name__ == '__main__':
    main()
