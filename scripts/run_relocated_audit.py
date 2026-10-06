#!/usr/bin/env python3
"""Execute an unchanged historical audit with explicit read-only path mapping.

Historical paths remain the strings used in command/provenance comparisons.
Filesystem operations resolve to the deposited package. All other checks,
including source hashes, terminal status and coverage checks, stay unchanged.
"""
import argparse
import builtins
import hashlib
import json
import os
import pathlib
import sys
import types


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--package', type=pathlib.Path, required=True)
    p.add_argument('--historical-root', required=True)
    p.add_argument('--script', required=True)
    args = p.parse_args()
    physical = args.package.resolve()
    historical = args.historical_root.rstrip('/')
    script = physical / args.script
    source = script.read_bytes()
    sys.dont_write_bytecode = True
    print(json.dumps({'adapter': 'historical-path relocation only',
                     'historical_root': historical, 'physical_root': str(physical),
                     'script': args.script, 'script_sha256': hashlib.sha256(source).hexdigest(),
                     'source_changed': False}), flush=True)

    class RelocatedPath(type(pathlib.Path())):
        def __fspath__(self):
            text = super().__str__()
            if text == historical or text.startswith(historical + '/'):
                return str(physical) + text[len(historical):]
            return text

        def resolve(self, strict=False):
            text = super().__str__()
            if text == historical or text.startswith(historical + '/'):
                return type(self)(os.path.normpath(text))
            return super().resolve(strict=strict)

    # Expose the adapter only to this audit's imports. Replacing pathlib.Path
    # globally changes the base class's constructor identity check on Python
    # 3.14 and can create an uninitialised PosixPath.
    original_import = builtins.__import__
    def audit_import(name, globals=None, locals=None, fromlist=(), level=0):
        module = original_import(name, globals, locals, fromlist, level)
        if name == 'pathlib' and 'Path' in fromlist:
            return types.SimpleNamespace(**{**vars(module), 'Path': RelocatedPath})
        return module
    logical_script = historical + '/' + args.script
    namespace = {'__name__': '__main__', '__file__': logical_script,
                 '__builtins__': {**vars(builtins), '__import__': audit_import}}
    sys.argv = [logical_script]
    exec(compile(source, logical_script, 'exec'), namespace)


if __name__ == '__main__':
    main()
