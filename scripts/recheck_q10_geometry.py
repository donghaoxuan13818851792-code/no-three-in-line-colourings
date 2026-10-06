#!/usr/bin/env python3
"""Freshly compile the independently authored Q10 membership auditor.

Read one catalogue per worker directly from the exact handoff ZIP, check its
hash, and audit every mask. Scratch catalogues are removed after each worker.
This verifies membership and stored counters, not enumeration completeness or
the UNSAT decision of the packing join.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PREFIX='Q10_HPC_HANDOFF_PACKAGE/'
RESERVE=5*1024**3


def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=10);a=p.parse_args()
    assert 1<=a.workers<=10
    a.output.mkdir(exist_ok=True)
    archive_meta=json.loads((ROOT/'g11/Q/evidence/Q10/archive.json').read_text())
    assert a.archive.stat().st_size==archive_meta['bytes']
    archive_sha=digest(a.archive)
    assert archive_sha==archive_meta['sha256']
    src=ROOT/'g11/Q/evidence/Q10/received/work/solver_agent/q10_cap20_catalogue_audit.cpp'
    binary=a.output/'q10_cap20_catalogue_audit'
    subprocess.run(['clang++','-O3','-std=c++20',str(src),'-o',str(binary)],check=True)
    caps=ROOT/'g11/R/data/caps22_diag_independent.hex'
    metadata={'archive_sha256':archive_sha,'archive_bytes':a.archive.stat().st_size,
              'auditor_source_sha256':digest(src),'auditor_binary_sha256':digest(binary),
              'caps676_sha256':digest(caps),'workers':a.workers,
              'claim_boundary':'catalogue membership/geometry/capacity and counters only; no catalogue completeness or global UNSAT proof'}
    ledger=json.loads((ROOT/'g11/Q/evidence/Q10/audits/representative_ledger.json').read_text())
    representatives=(ROOT/'g11/R/data/caps22_d4.hex').read_text().split()
    assert len(ledger)==89 and {row['representative'] for row in ledger}==set(range(89))
    assert all(int(row['anchor'],16)==int(representatives[row['representative']],16) for row in ledger)
    completed=[];started=time.time()
    with zipfile.ZipFile(a.archive) as z:
        def obj(name):return json.loads(z.read(PREFIX+name))
        jobs=[]
        for row in ledger:
            rep=row['representative'];anchor=row['anchor']
            expected_audit=None
            if rep not in {17,53,76,88}:
                cat='work/solver_agent/cap20_rep1_runner_v1' if rep==1 else f'runs/rep{rep}_catalogue'
                result=obj(cat+'/result.json');path=cat+'/all_masks.hex'
                count=result['catalogue_masks'];sha=result['catalogue_sha256'];expected_audit=result['audit']
            elif rep==53:
                path='work/solver_agent/cap20_rep53_all_masks_v4.hex'
                result=obj('work/math_agent/nonextendible_structure/rep53_result_audit.json')
                # Its exact catalogue identity is in the saved result report.
                count=result['enumeration']['candidate_count'];sha=result['enumeration']['catalogue_sha256']
            else:
                result=obj(f'work/math_agent/nonextendible_structure/rep{rep}_result_meta.json')
                cat=result['catalogue'];path=cat['path'];count=cat['masks'];sha=cat['sha256']
            jobs.append({'rep':rep,'anchor':anchor,'path':path,'count':count,'sha256':sha,'expected_audit':expected_audit})
        assert sum(job['count'] for job in jobs)==75666410
        def check(job):
            rep=job['rep'];begin=time.time()
            with tempfile.TemporaryDirectory(prefix=f'rep{rep}-',dir=a.output) as tmp:
                catalogue=Path(tmp)/'all_masks.hex';h=hashlib.sha256()
                with z.open(PREFIX+job['path']) as source,catalogue.open('wb') as target:
                    while block:=source.read(1024*1024):
                        if shutil.disk_usage(a.output).free-len(block)<RESERVE:raise RuntimeError('disk reserve reached')
                        h.update(block);target.write(block)
                assert h.hexdigest()==job['sha256'],rep
                command=['/usr/bin/time','-p',str(binary),'--anchor',job['anchor'],'--catalogue',str(catalogue),'--caps',str(caps)]
                result=subprocess.run(command,capture_output=True,text=True)
                (a.output/f'rep{rep}.out').write_text(result.stdout)
                (a.output/f'rep{rep}.err').write_text(result.stderr)
                (a.output/f'rep{rep}.status').write_text(str(result.returncode)+'\n')
                m=re.fullmatch(r'AUDIT_OK count (\d+) least_eligible (\d+) extendible (\d+) nonextendible (\d+) maximal_lines 628\s*',result.stdout)
                assert result.returncode==0 and m,(rep,result.stdout,result.stderr)
                count,least,extendible,nonextendible=map(int,m.groups())
                assert count==job['count'] and extendible+nonextendible==count,rep
                if job['expected_audit'] is not None:assert result.stdout.strip()==job['expected_audit'],rep
                times={k:float(v) for k,v in re.findall(r'^(real|user|sys)\s+([\d.]+)$',result.stderr,re.M)}
                return {'representative':rep,'catalogue':job['path'],'catalogue_sha256':job['sha256'],
                        'masks_checked':count,'least_eligible':least,'extendible':extendible,
                        'nonextendible':nonextendible,'status':'PASS','wall_seconds':time.time()-begin,**times}
        with ThreadPoolExecutor(max_workers=a.workers) as pool:
            futures={pool.submit(check,j):j for j in jobs}
            for future in as_completed(futures):
                record=future.result();completed.append(record)
                report={**metadata,'status':'RUNNING','completed_representatives':len(completed),'elapsed_seconds':time.time()-started,'records':sorted(completed,key=lambda r:r['representative'])}
                (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
                print(f"Q10_GEOMETRY_PASS rep={record['representative']} masks={record['masks_checked']} completed={len(completed)}/89",flush=True)
    assert {r['representative'] for r in completed}==set(range(89))
    report.update(status='PASS',total_masks_checked=sum(r['masks_checked'] for r in completed),elapsed_seconds=time.time()-started)
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Q10_MEMBERSHIP_ALL_89_PASS',report['total_masks_checked'])


if __name__=='__main__':main()
