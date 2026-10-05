#!/usr/bin/env python3
"""Execute the received verifier's manifest stage using read-only ZIP paths.

The supplied source and checks are unchanged. Only ROOT's filesystem access
is adapted to avoid fully expanding a large package. Subprocess-based later
stages are not executed by this adapter. All visited files are streamed with
ZIP CRC verification, and their hashes are retained in an external index.
"""
import argparse
import hashlib
import io
import json
from pathlib import PurePosixPath
import stat
import zipfile


class ZipPath:
    def __init__(self, archive, names, path):
        self.archive, self.names, self.path = archive, names, path.rstrip('/')

    def __truediv__(self, child):
        return ZipPath(self.archive, self.names, self.path + '/' + str(child))

    @property
    def name(self):
        return self.path.rsplit('/', 1)[-1]

    def is_file(self):
        return self.path in self.names and not self.names[self.path].is_dir()

    def is_symlink(self):
        return self.path in self.names and stat.S_ISLNK(self.names[self.path].external_attr >> 16)

    def is_relative_to(self, parent):
        return self.path == parent.path or self.path.startswith(parent.path + '/')

    def relative_to(self, parent):
        if not self.is_relative_to(parent):
            raise ValueError('path outside virtual handoff root')
        return PurePosixPath(self.path[len(parent.path) + 1:])

    def rglob(self, pattern):
        if pattern != '*':
            raise ValueError('unsupported ZIP glob')
        for name in self.names:
            if name.startswith(self.path + '/'):
                yield ZipPath(self.archive, self.names, name)

    def open(self, mode='r', encoding='utf-8', errors=None):
        if mode not in ('r', 'rb'):
            raise ValueError('ZIP adapter is read-only')
        f = self.archive.open(self.names[self.path])
        return f if mode == 'rb' else io.TextIOWrapper(f, encoding=encoding, errors=errors)

    def read_text(self, encoding='utf-8', errors=None):
        with self.open(encoding=encoding, errors=errors) as f:
            return f.read()

    def __str__(self):
        return self.path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    parser.add_argument('hash_index')
    parser.add_argument('--expected-verifier-sha256', required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.archive) as archive:
        names = {}
        for item in archive.infolist():
            parts = PurePosixPath(item.filename).parts
            if item.filename.startswith('/') or '..' in parts:
                raise SystemExit('FAIL: unsafe archive path')
            name = item.filename.rstrip('/')
            if name in names:
                raise SystemExit('FAIL: duplicate archive path: ' + name)
            names[name] = item
        verifier_names = [n for n in names if n.endswith('/verify_handoff.py')
                          and len(PurePosixPath(n).parts) == 2]
        if len(verifier_names) != 1:
            raise SystemExit('FAIL: ambiguous handoff root')
        verifier_name = verifier_names[0]
        source = archive.read(verifier_name)
        source_hash = hashlib.sha256(source).hexdigest()
        if source_hash != args.expected_verifier_sha256:
            raise SystemExit('FAIL: supplied verifier differs from reviewed source')
        namespace = {'__name__': 'received_zip_manifest_verifier', '__file__': verifier_name}
        exec(compile(source, verifier_name, 'exec'), namespace)
        root = ZipPath(archive, names, verifier_name.rsplit('/', 1)[0])
        namespace['ROOT'] = root
        original_digest = namespace['digest']
        print('SUPPLIED_VERIFIER_ZIP_MANIFEST_STAGE source_sha256=' + source_hash, flush=True)
        print('MODE read_only_ZIP_adapter; supplied checks unchanged; later stages excluded', flush=True)
        with open(args.hash_index, 'w') as index:
            visited = 0
            def indexed_digest(path):
                nonlocal visited
                value = original_digest(path)
                index.write(json.dumps({'path': str(path.relative_to(root)),
                                        'bytes': names[path.path].file_size,
                                        'sha256': value}, sort_keys=True) + '\n')
                visited += 1
                if visited % 50000 == 0:
                    index.flush()
                    print('ZIP_FILES_HASHED ' + str(visited), flush=True)
                return value
            namespace['digest'] = indexed_digest
            namespace['manifest_audit']()


if __name__ == '__main__':
    main()
