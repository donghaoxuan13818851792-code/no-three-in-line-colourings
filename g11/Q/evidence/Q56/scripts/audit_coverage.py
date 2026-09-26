#!/usr/bin/env python3
"""Strict audit of the immutable nine-shard canonical result."""
from pathlib import Path
import hashlib,re,sys

ROOT=Path(__file__).resolve().parents[1]
def fail(message): raise SystemExit('FINAL_SHARD_AUDIT FAIL: '+message)
def digest(path):
 h=hashlib.sha256()
 try:
  with path.open('rb') as f:
   for block in iter(lambda:f.read(1<<20),b''): h.update(block)
 except OSError as e: fail(f'cannot hash {path}: {e}')
 return h.hexdigest()
def require(path):
 if not path.is_file(): fail(f'missing artifact {path.relative_to(ROOT)}')
 return path
def parse_tab(path):
 rows=[]
 for raw in require(path).read_text().splitlines():
  line=raw.replace('\\t','\t')
  if line and not line.startswith('#'): rows.append(line.split('\t'))
 return rows

manifest={}
for raw in require(ROOT/'results/run_manifest.tsv').read_text().splitlines():
 if '\t' in raw:
  k,v=raw.replace('\\t','\t').split('\t',1); manifest[k]=v
expected={'source_sha256':ROOT/'src/q567_residual_cap_search.cpp',
          'executable_sha256':ROOT/'canonical/q567_residual_cap_search_macos_arm64',
          'input_sha256':ROOT/'data/q567_all_residuals.tsv',
          'catalogue_sha256':ROOT/'data/caps22_d4.hex'}
for key,path in expected.items():
 if manifest.get(key) is None: fail(f'missing {key} in run_manifest.tsv')
 actual=digest(require(path))
 if actual!=manifest[key]: fail(f'{key} hash mismatch expected={manifest[key]} actual={actual}')
input_rows=require(ROOT/'data/q567_all_residuals.tsv').read_text().splitlines()
representatives=sorted({int(line.split('\t')[0]) for line in input_rows if line.strip()})
if len(input_rows)!=1325039 or representatives!=list(range(89)):
 fail('input ledger row/representative count mismatch')

rows=parse_tab(ROOT/'data/FINAL_SHARD_LEDGER.tsv')
if len(rows)!=9: fail(f'expected exactly 9 ledger rows, found {len(rows)}')
labels=[]; parsed=[]
for q in rows:
 if len(q)!=9: fail(f'malformed ledger row: {q}')
 label,s,e,n,command,out,err,code,pid=q
 if label in labels: fail(f'duplicate shard {label}')
 labels.append(label)
 try: s,e,n=int(s),int(e),int(n)
 except ValueError: fail(f'non-integer interval in {label}')
 if e<=s or n!=e-s: fail(f'bad interval/count in {label}')
 parsed.append((s,e,n,label,command,out,err,code,pid))
if set(labels)!={f'w{i:02d}' for i in range(9)}: fail('wrong canonical shard labels')
parsed.sort()
if parsed[0][0]!=0 or parsed[-1][1]!=1325039: fail('global endpoints are not [0,1325039)')
for prev,cur in zip(parsed,parsed[1:]):
 if prev[1]!=cur[0]: fail(f'gap or overlap between {prev[3]} and {cur[3]}')
if sum(x[2] for x in parsed)!=1325039: fail('total prefix count mismatch')

for s,e,n,label,command,out_rel,err_rel,code_rel,pid_rel in parsed:
 out=ROOT/out_rel; err=ROOT/err_rel; code=ROOT/code_rel; pid=ROOT/pid_rel
 for p in (out,err,code,pid,ROOT/f'results/{label}.launch.tsv',ROOT/f'results/{label}.meta.tsv'): require(p)
 text=out.read_text(); stderr=err.read_text()
 final_lines=re.findall(r'^UNSAT_Q567_RESIDUAL_RANGE .*$',text,re.M)
 if len(final_lines)!=1: fail(f'{label} must have exactly one final UNSAT line')
 if re.search(r'^(SAT_Q567|INCOMPLETE_Q567|UNKNOWN|ERROR)\b',text+stderr,re.M): fail(f'{label} has forbidden status/error')
 try: exit_code=int(code.read_text().strip())
 except ValueError: fail(f'{label} malformed exit code')
 if exit_code!=20: fail(f'{label} exit code {exit_code}, expected 20')
 m=re.fullmatch(r'UNSAT_Q567_RESIDUAL_RANGE prefixes_completed (\d+) current_prefix (\d+) .*',final_lines[0])
 if not m or int(m.group(1))!=n or int(m.group(2))!=e-1: fail(f'{label} count/terminal mismatch')
 launch=dict(x.split('\t',1) for x in (ROOT/f'results/{label}.launch.tsv').read_text().splitlines() if '\t' in x)
 if launch.get('label')!=label or launch.get('start')!=str(s) or launch.get('end')!=str(e): fail(f'{label} launch record mismatch')
 if f'--count {n}' not in launch.get('command',''): fail(f'{label} launch command mismatch')
 meta=dict(x.split('\t',1) for x in (ROOT/f'results/{label}.meta.tsv').read_text().splitlines() if '\t' in x)
 for k,v in [('status','UNSAT'),('exit_code','20'),('prefixes_completed',str(n)),('current_prefix',str(e-1)),('source_sha256',manifest['source_sha256']),('executable_sha256',manifest['executable_sha256']),('input_sha256',manifest['input_sha256']),('catalogue_sha256',manifest['catalogue_sha256'])]:
  if meta.get(k)!=v: fail(f'{label} metadata {k} mismatch')
print('FINAL_SHARD_AUDIT PASS workers=9 status=UNSAT')
