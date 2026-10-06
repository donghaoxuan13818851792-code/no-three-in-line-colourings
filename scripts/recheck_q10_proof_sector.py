#!/usr/bin/env python3
"""Check existing Q10 sector proofs; never invoke a SAT solver or rewrite inputs.

Replay 88 ordinary DRAT certificates concurrently, then the incremental rep1
certificate with its unchanged stateful checker. The claim is confined to the
at-least-two-extendible-size-20 sector, not arbitrary-cap global Q10.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=10);a=p.parse_args()
    assert 1<=a.workers<=10
    a.output.mkdir(exist_ok=True)
    pair=a.package/'work/package_agent/pair_proofs'
    original=json.loads((pair/'drat_pilots/ordinary_drat_ledger.json').read_text())
    assert set(map(int,original['cases']))==set(range(89))-{1}
    drat_src=a.package/'work/third_party/drat-trim/drat-trim.c';drat=a.output/'drat-trim'
    subprocess.run(['clang','-O3',str(drat_src),'-o',str(drat)],check=True)
    idrup_dir=pair/'idrup-check-src';idrup=a.output/'idrup-check'
    subprocess.run(['clang','-O3','-DNDEBUG','-DCADICAL',str(idrup_dir/'idrup-check.c'),str(idrup_dir/'idrup-build.c'),'-o',str(idrup)],check=True)
    metadata={'claim_boundary':'at-least-two-extendible-size-20 sector only',
              'ordinary_ledger_sha256':sha(pair/'drat_pilots/ordinary_drat_ledger.json'),
              'rep1_base_input_sha256':sha(a.package/'work/root/pair_selectors/rep1.inccnf'),
              'rep1_binding_auditor_sha256':sha(pair/'audit_idrup_interactions.py'),
              'ordinary_checker_source_sha256':sha(drat_src),'ordinary_checker_binary_sha256':sha(drat),
              'idrup_checker_source_hashes':{p.name:sha(p) for p in idrup_dir.glob('idrup-*.[ch]')},
              'idrup_checker_binary_sha256':sha(idrup),'new_solver_searches':0,
              'compiler':subprocess.check_output(['clang','--version'],text=True)}
    begin=time.time();records=[]
    def check(case):
        rep=case['representative'];cnf=a.package/case['cnf'];proof=a.package/case['proof']
        assert sha(cnf)==case['cnf_sha256'] and sha(proof)==case['proof_sha256'],rep
        assert cnf.stat().st_size==case['cnf_bytes'] and proof.stat().st_size==case['proof_bytes'],rep
        out=a.output/f'rep{rep}.check.log'
        start=time.time()
        with out.open('w') as f:
            result=subprocess.run(['/usr/bin/time','-p',str(drat),str(cnf),str(proof)],stdout=f,stderr=subprocess.STDOUT)
        text=out.read_text(errors='replace')
        trivial=proof.stat().st_size==0 and any(line.strip()=='0' for line in cnf.read_text().splitlines())
        verified=bool(re.search(r'^s VERIFIED$',text,re.M)) and (result.returncode==0 or (result.returncode==1 and trivial))
        assert verified,(rep,result.returncode)
        timings={k:float(v) for k,v in re.findall(r'^(real|user|sys)\s+([\d.]+)$',text,re.M)}
        return {'representative':rep,'verified':True,'checker_exit':result.returncode,'trivial_input_unsat':trivial,
                'cnf_sha256':case['cnf_sha256'],'proof_sha256':case['proof_sha256'],
                'wall_seconds':time.time()-start,**timings}
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for f in as_completed([pool.submit(check,c) for c in original['cases'].values()]):
            record=f.result();records.append(record)
            report={**metadata,'status':'RUNNING','phase':'ORDINARY_DRAT','verified_cases':len(records),'records':sorted(records,key=lambda r:r['representative'])}
            (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(f"Q10_DRAT_VERIFIED rep={record['representative']} done={len(records)}/88",flush=True)
    assert len(records)==88
    report.update(phase='REP1_IDRUP',updated_epoch=time.time());(a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    cnf=pair/'rep1_full.icnf';proof=pair/'rep1_full.idrup'
    binding=a.output/'rep1_binding.json'
    interaction_audit=subprocess.run([sys.executable,str(pair/'audit_idrup_interactions.py'),
        str(a.package/'work/root/pair_selectors/rep1.inccnf'),str(proof),
        '--transcript',str(cnf),'--json',str(binding)],capture_output=True,text=True)
    (a.output/'rep1_binding.log').write_text(interaction_audit.stdout+interaction_audit.stderr)
    assert interaction_audit.returncode==0 and json.loads(binding.read_text())['status']=='PASS'
    start=time.time();out=a.output/'rep1_idrup.check.log'
    with out.open('w') as f:
        result=subprocess.run(['/usr/bin/time','-p',str(idrup),str(cnf),str(proof)],stdout=f,stderr=subprocess.STDOUT)
    text=out.read_text(errors='replace')
    assert result.returncode==0 and re.search(r'^s VERIFIED$',text,re.M),(result.returncode,text[-1500:])
    times={k:float(v) for k,v in re.findall(r'^(real|user|sys)\s+([\d.]+)$',text,re.M)}
    report.update(status='PASS',phase='COMPLETE',elapsed_seconds=time.time()-begin,
                  incremental_rep1={'verified':True,'cnf_sha256':sha(cnf),'proof_sha256':sha(proof),'wall_seconds':time.time()-start,**times})
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Q10_EXISTING_SECTOR_PROOFS_VERIFIED 88_DRAT_PLUS_REP1_IDRUP')


if __name__=='__main__':main()
