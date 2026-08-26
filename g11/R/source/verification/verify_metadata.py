#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
profiles=(
'0_0_1_1_1_8','0_0_1_1_2_7','0_0_1_1_3_6','0_0_1_1_4_5',
'0_0_1_2_2_6','0_0_1_2_3_5','0_0_1_2_4_4','0_0_1_3_3_4',
'0_0_2_2_2_5','0_0_2_2_3_4','0_0_2_3_3_3')
expected={f'{p}__pair_{i:03d}' for p in profiles for i in range(119)}
cnfs={p.stem:p for p in (root/'leaves/cnf').glob('*.cnf')}
solvers={p.stem:p for p in (root/'leaves/solver_reports').glob('*.json')}
vr={p.stem:p for p in (root/'proofs/verification_reports').glob('*.json')}
dr={p.name[:-len('.drat-check.log')]:p for p in (root/'proofs/verification_reports').glob('*.drat-check.log')}
lr={p.name[:-len('.lrat-check.log')]:p for p in (root/'proofs/verification_reports').glob('*.lrat-check.log')}
assert set(cnfs)==set(solvers)==set(vr)==set(dr)==set(lr)==expected
ledger=json.loads((root/'verification/final_ledger/batch-proof-report.json').read_text())
assert ledger['completed']==ledger['expected_entries']==1309
assert ledger['failures']==0 and ledger['verified'] is True
assert set(ledger['entries'])==expected
for n in sorted(expected):
    c=cnfs[n]; s=solvers[n]; v=vr[n]; d=dr[n]; l=lr[n]
    sj=json.loads(s.read_text()); vj=json.loads(v.read_text()); le=ledger['entries'][n]
    ch=sha(c); sh=sha(s); dh=sha(d); lh=sha(l)
    assert sj['name']==n and sj['exit_code']==20 and sj['stdout']=='s UNSATISFIABLE\n'
    assert sj['cnf_bytes']==c.stat().st_size and sj['cnf_sha256']==ch
    assert vj['name']==n and vj['verified'] is True
    assert vj['drat_trim_exit']==0 and vj['lrat_check_exit']==0
    assert vj['source_report_sha256']==sh and vj['cnf_sha256']==ch
    assert vj['drat_log_sha256']==dh and vj['lrat_log_sha256']==lh
    assert le['verified'] is True and le['source_report_sha256']==sh
    assert le['cnf_sha256']==ch and le['drat_log_sha256']==dh and le['lrat_log_sha256']==lh
print('METADATA AUDIT PASS leaves=1309 cnfs=1309 solver_reports=1309 verification_reports=1309 drat_logs=1309 lrat_logs=1309')
