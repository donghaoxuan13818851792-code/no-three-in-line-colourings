#!/usr/bin/env python3
from pathlib import Path
import hashlib,sys
if len(sys.argv)!=3: raise SystemExit('usage: verify_prefix_ledger.py generated.tsv frozen.tsv')
generated,frozen=map(Path,sys.argv[1:])
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
if not generated.is_file() or not frozen.is_file(): raise SystemExit('missing ledger')
rows=generated.read_text().splitlines(); ids=sorted({int(x.split('\t')[0]) for x in rows if x.strip()})
if len(rows)!=1325039 or ids!=list(range(89)): raise SystemExit('row/representative count mismatch')
if digest(generated)!=digest(frozen): raise SystemExit('SHA-256 mismatch')
print('PREFIX_LEDGER_AUDIT PASS rows=1325039 representatives=89 sha256='+digest(generated))
