#!/usr/bin/env python3
"""Check an exact ZIP payload against its received two-space SHA256 manifest.

No archive member is extracted. Missing, extra, duplicate, unsafe or changed
payload files fail the audit. The manifest is itself bound by a recorded hash.
This is an integrity check, not a terminal or mathematical correctness audit.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('manifest',help='exact manifest member path inside ZIP')
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    with args.archive.open('rb') as f:
        archive_sha=hashlib.file_digest(f,'sha256').hexdigest()
    with zipfile.ZipFile(args.archive) as z:
        names=z.namelist()
        assert len(names)==len(set(names)), 'duplicate archive member'
        payload=z.read(args.manifest)
        prefix=args.manifest.rsplit('/',1)[0]+'/'
        expected={}
        for line in payload.decode().splitlines():
            match=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
            assert match, 'invalid manifest line'
            sha,relative=match.groups()
            path=PurePosixPath(relative)
            assert not path.is_absolute() and '..' not in path.parts
            assert relative not in expected, 'duplicate manifest entry'
            expected[relative]=sha
        actual={n[len(prefix):] for n in names
                if n.startswith(prefix) and not n.endswith('/') and n!=args.manifest}
        missing=sorted(set(expected)-actual)
        extra=sorted(actual-set(expected))
        changed=[]
        for relative,sha in expected.items():
            if relative not in actual:continue
            with z.open(prefix+relative) as f:
                if hashlib.file_digest(f,'sha256').hexdigest()!=sha:changed.append(relative)
        outside=[n for n in names if not n.startswith(prefix) and not n.endswith('/')]
        status='PASS' if not(missing or extra or changed or outside) else 'FAIL'
        report={'status':status,'scope':'exact archive payload integrity only',
                'archive_bytes':args.archive.stat().st_size,'archive_sha256':archive_sha,
                'manifest':args.manifest,'manifest_sha256':hashlib.sha256(payload).hexdigest(),
                'listed_files':len(expected),'missing':missing,'extra':extra,
                'mismatched':changed,'outside_payload_files':outside}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if status=='PASS' else 1)


if __name__=='__main__':main()
