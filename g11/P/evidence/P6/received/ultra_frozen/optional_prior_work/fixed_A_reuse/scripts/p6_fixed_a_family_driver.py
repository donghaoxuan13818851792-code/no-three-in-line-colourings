#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,pathlib,re,resource,subprocess,time
FULL=(1<<121)-1
FILTERS=['catalogue_membership','distinct_disjoint','singleton_row_distinct','singleton_col_distinct','long11_coverage','residual_line_capacity_4','q56_certified_filter','q7_certified_filter','q89_certified_filter']

def sha_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def sha_file(p:pathlib.Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def hx(x:int)->str:return f'{x:031x}'
def ph(s:str)->int:
 if len(s)!=31 or s.lower()!=s or any(c not in '0123456789abcdef' for c in s):raise ValueError(f'bad mask {s!r}')
 x=int(s,16)
 if x>>121:raise ValueError('high mask bits')
 return x
def atomic_bytes(p:pathlib.Path,b:bytes):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.partial');q.write_bytes(b);os.replace(q,p)
def atomic_json(p:pathlib.Path,d):atomic_bytes(p,(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n').encode())
def txy(t,x,y):return ((x,y),(10-y,x),(10-x,10-y),(y,10-x),(10-x,y),(x,10-y),(y,x),(10-y,10-x))[t]
def tm(m,t):
 z=0
 while m:
  q=m&-m;p=q.bit_length()-1;x,y=txy(t,p%11,p//11);z|=1<<(11*y+x);m-=q
 return z
def canonical(a,b):
 best=None
 for t in range(8):
  aa,bb=tm(a,t),tm(b,t)
  for sw in (False,True):
   x,y=(bb,aa) if sw else (aa,bb)
   if x>y:continue
   q=(x,y,t,sw)
   if best is None or q[:2]<best[:2]:best=q
 return best
def singleton(m):
 rs=[r for r in range(11) if sum((m>>(11*r+c))&1 for c in range(11))==1]
 cs=[c for c in range(11) if sum((m>>(11*r+c))&1 for r in range(11))==1]
 if len(rs)!=1 or len(cs)!=1:raise ValueError('size21 singleton profile')
 return rs[0],cs[0]
def parse_time(p:pathlib.Path):
 s=p.read_text(errors='replace')
 def f(pat,cast=float,default=0):
  m=re.search(pat,s);return cast(m.group(1)) if m else default
 return {'user_seconds':f(r'User time \(seconds\): ([0-9.]+)'), 'system_seconds':f(r'System time \(seconds\): ([0-9.]+)'), 'peak_rss_kb':f(r'Maximum resident set size \(kbytes\): (\d+)',int)}
def read_branch(path:pathlib.Path):
 lines=path.read_text().splitlines()
 if not lines:raise ValueError('empty branch')
 historical=lines[0].split('\t')[0]=='rank';rows=[];A=None
 if historical:
  for x in csv.DictReader(lines,delimiter='\t'):
   rank=int(x['rank']);b=ph(x['cap_hex']);r=ph(x['residual_hex']);a=FULL^b^r;sid=f'fixedA-rank{rank:05d}';rows.append({'source_record_id':sid,'rank':rank,'a':a,'b':b,'r':r})
 else:
  for line in lines:
   x=line.split('\t')
   if len(x)!=4:raise ValueError('canonical branch fields')
   a,b,r=map(ph,x[:3]);rows.append({'source_record_id':x[3],'rank':None,'a':a,'b':b,'r':r})
 for i,x in enumerate(rows):
  if A is None:A=x['a']
  if x['a']!=A or x['b'].bit_count()!=21 or x['r'].bit_count()!=79 or (x['a']|x['b']|x['r'])!=FULL or x['a']&x['b'] or x['a']&x['r'] or x['b']&x['r']:raise ValueError(f'bad branch record {i}')
  x['source_index']=i;x['singleton_row'],x['singleton_col']=singleton(x['b'])
 if len({x['source_record_id'] for x in rows})!=len(rows) or len({x['b'] for x in rows})!=len(rows):raise ValueError('duplicate branch identity')
 return historical,A,rows
def pair_record(x,branch_name):
 ca,cb,t,sw=canonical(x['a'],x['b']);cr=FULL^ca^cb;digest=hashlib.sha256(f'{hx(ca)}\t{hx(cb)}\n'.encode()).hexdigest()
 return {'schema':'p6-pair-record-v2','pair_id':'p6pair-'+digest[:24],'canonical_a_hex':hx(ca),'canonical_b_hex':hx(cb),'residual_hex':hx(cr),
 'source_shard_id':branch_name,'source_record_id':x['source_record_id'],'filter_stage':'q89_certified_filter','filters_passed':FILTERS,
 'pair_key_sha256':digest,'original_a_hex':hx(x['a']),'original_b_hex':hx(x['b']),'original_residual_hex':hx(x['r']),
 'to_canonical_transform_id':t,'swapped':sw}
def write_pairgrid(p,x):
 vals=['1' if x['a']>>q&1 else '2' if x['b']>>q&1 else '0' for q in range(121)];atomic_bytes(p,('\n'.join(vals)+'\n').encode())
def run_timed(cmd,rawbase:pathlib.Path):
 tm=rawbase.with_suffix('.time');stdout=rawbase.with_suffix('.stdout');stderr=rawbase.with_suffix('.stderr');command=rawbase.with_suffix('.command')
 command.parent.mkdir(parents=True,exist_ok=True);atomic_bytes(command,(' '.join(subprocess.list2cmdline([str(x)]) for x in cmd)+'\n').encode())
 cp=subprocess.run(['/usr/bin/time','-v','-o',str(tm.with_name(tm.name+'.partial')),*map(str,cmd)],capture_output=True)
 os.replace(tm.with_name(tm.name+'.partial'),tm);atomic_bytes(stdout,cp.stdout);atomic_bytes(stderr,cp.stderr);atomic_bytes(rawbase.with_suffix('.exit'),(str(cp.returncode)+'\n').encode())
 return cp,parse_time(tm)
def valid_resume_record(p,pair_sha,backend_src_sha,backend_bin_sha):
 try:
  d=json.loads(p.read_text());return d if d.get('terminal') is True and d.get('input_sha256')==pair_sha and d.get('solver_source_sha256')==backend_src_sha and d.get('solver_binary_sha256')==backend_bin_sha else None
 except Exception:return None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--branch',type=pathlib.Path,required=True);ap.add_argument('--output-dir',type=pathlib.Path,required=True);ap.add_argument('--candidate-bin',type=pathlib.Path,required=True);ap.add_argument('--candidate-source',type=pathlib.Path,required=True);ap.add_argument('--backend-bin',type=pathlib.Path,required=True);ap.add_argument('--backend-source',type=pathlib.Path,required=True);ap.add_argument('--witness-verifier',type=pathlib.Path,required=True);ap.add_argument('--chunk-size',type=int,default=8);ap.add_argument('--grouping',choices=['source','singleton'],default='source');ap.add_argument('--max-pairs',type=int,default=0);ap.add_argument('--candidate-seconds',type=float,default=0);ap.add_argument('--backend-seconds',type=float,default=0);ap.add_argument('--resume',action='store_true');a=ap.parse_args()
 if not 1<=a.chunk_size<=64:raise SystemExit('chunk size 1..64')
 start=time.monotonic();ru0=resource.getrusage(resource.RUSAGE_SELF);rc0=resource.getrusage(resource.RUSAGE_CHILDREN)
 historical,A,allrows=read_branch(a.branch.resolve());rows=allrows[:a.max_pairs or None];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 prior_summary=None
 if a.resume and (out/'branch_summary.json').exists():
  try:prior_summary=json.loads((out/'branch_summary.json').read_text())
  except Exception:prior_summary=None
 cbin=a.candidate_bin.resolve();bbin=a.backend_bin.resolve();csrc=a.candidate_source.resolve();bsrc=a.backend_source.resolve();wverify=a.witness_verifier.resolve()
 hashes={'input_ledger_sha256':sha_file(a.branch),'candidate_source_sha256':sha_file(csrc),'candidate_binary_sha256':sha_file(cbin),'backend_source_sha256':sha_file(bsrc),'backend_binary_sha256':sha_file(bbin),'witness_verifier_sha256':sha_file(wverify)}
 pairs=[pair_record(x,a.branch.name) for x in rows];atomic_bytes(out/'pair_records.jsonl',''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in pairs).encode())
 groups={}
 if a.grouping=='source':groups[('source','source')]=list(rows)
 else:
  for x in rows:groups.setdefault((x['singleton_row'],x['singleton_col']),[]).append(x)
 chunks=[]
 for key in sorted(groups,key=str):
  g=groups[key]
  for k in range(0,len(g),a.chunk_size):chunks.append((key,g[k:k+a.chunk_size]))
 records_by_id={};prep_user=prep_sys=backend_user=backend_sys=0.0;peak=0;candidate_occ=0;shared_nodes=0;chunk_unique=0;completed_chunks=0;sat_found=False
 for ci,(key,chunk) in enumerate(chunks):
  if sat_found:break
  cdir=out/'chunks'/f'chunk-{ci:05d}-{key[0]}-{key[1]}';cdir.mkdir(parents=True,exist_ok=True)
  unresolved=[]
  for x in chunk:
   pg=out/'pairgrids'/f'{x["source_record_id"]}.pairgrid';write_pairgrid(pg,x);pgh=sha_file(pg);recp=out/'records'/f'{x["source_record_id"]}.json'
   old=valid_resume_record(recp,pgh,hashes['backend_source_sha256'],hashes['backend_binary_sha256']) if a.resume else None
   if old:records_by_id[x['source_record_id']]=old
   else:unresolved.append((x,pg,pgh,recp))
  if not unresolved:continue
  branchfile=cdir/'chunk.tsv';atomic_bytes(branchfile,''.join(f'{hx(x["a"])}\t{hx(x["b"])}\t{hx(x["r"])}\t{x["source_record_id"]}\n' for x,_,_,_ in unresolved).encode())
  canddir=cdir/'candidates';cmd=[cbin,'--branch',branchfile,'--begin','0','--end',str(len(unresolved)),'--dump-dir',canddir]
  if a.candidate_seconds:cmd += ['--seconds',str(a.candidate_seconds)]
  cp,tmv=run_timed(cmd,cdir/'candidate_batch');prep_user+=tmv['user_seconds'];prep_sys+=tmv['system_seconds'];peak=max(peak,tmv['peak_rss_kb'])
  text=cp.stdout.decode(errors='replace')
  m=re.search(r'nodes (\d+).*unique_leaf_caps (\d+).*candidate_occurrences (\d+)',text)
  if m:shared_nodes+=int(m.group(1));chunk_unique+=int(m.group(2));candidate_occ+=int(m.group(3))
  if cp.returncode!=0:
   for x,pg,pgh,recp in unresolved:
    d={'schema':'p6-decision-record-v2','decision_id':'family-'+x['source_record_id'],'equivalence_key':'exact-residual:'+hx(x['r']),'representative_residual_hex':hx(x['r']),
     'solver_source_sha256':hashes['backend_source_sha256'],'solver_binary_sha256':hashes['backend_binary_sha256'],'input_sha256':pgh,'status':'INCOMPLETE_P6_RESIDUAL' if cp.returncode==30 else 'ERROR_FAMILY_CANDIDATE_GENERATION','exit_code':cp.returncode,'terminal':False,'wall_seconds':0.0,'user_seconds':0.0,'system_seconds':0.0,'peak_rss_kb':0,'result_sha256':sha_bytes(cp.stdout),'source_record_id':x['source_record_id'],'family_chunk':ci}
    atomic_json(recp,d);records_by_id[x['source_record_id']]=d
   continue
  completed_chunks+=1
  for x,pg,pgh,recp in unresolved:
   cand=canddir/f'{x["source_record_id"]}.tsv'
   if not cand.exists():raise RuntimeError(f'missing candidate ledger {cand}')
   raw=cdir/'backend'/x['source_record_id'];wpartial=raw.with_suffix('.witness.partial');wfinal=raw.with_suffix('.witness.grid');cmd=[bbin,'--pair',pg,'--load-candidates',cand,'--out',wpartial]
   if a.backend_seconds:cmd += ['--seconds',str(a.backend_seconds)]
   bp,bt=run_timed(cmd,raw);backend_user+=bt['user_seconds'];backend_sys+=bt['system_seconds'];peak=max(peak,bt['peak_rss_kb']);stdout=bp.stdout.decode(errors='replace');status=stdout.split()[0] if stdout else 'ERROR_EMPTY_OUTPUT';terminal=status in {'SAT_P6_RESIDUAL','UNSAT_P6_RESIDUAL'} and bp.returncode in {10,20};witness_sha='';witness_verification={}
   if status=='SAT_P6_RESIDUAL' and terminal:
    if not wpartial.exists():status='ERROR_MISSING_WITNESS';terminal=False
    else:
     vp=subprocess.run(['python3',str(wverify),str(wpartial)],capture_output=True);atomic_bytes(raw.with_suffix('.witness_verify.stdout'),vp.stdout);atomic_bytes(raw.with_suffix('.witness_verify.stderr'),vp.stderr);witness_verification={'exit_code':vp.returncode,'stdout_sha256':sha_bytes(vp.stdout),'stderr_sha256':sha_bytes(vp.stderr)}
     if vp.returncode!=0:status='ERROR_WITNESS_VERIFICATION';terminal=False
     else:os.replace(wpartial,wfinal);witness_sha=sha_file(wfinal)
   elif wpartial.exists():wpartial.unlink()
   d={'schema':'p6-decision-record-v2','decision_id':'family-'+x['source_record_id'],'equivalence_key':'exact-residual:'+hx(x['r']),'representative_residual_hex':hx(x['r']),
    'solver_source_sha256':hashes['backend_source_sha256'],'solver_binary_sha256':hashes['backend_binary_sha256'],'input_sha256':pgh,'status':status,'exit_code':bp.returncode,'terminal':terminal,
    'wall_seconds':0.0,'user_seconds':bt['user_seconds'],'system_seconds':bt['system_seconds'],'peak_rss_kb':bt['peak_rss_kb'],'result_sha256':sha_bytes(bp.stdout),
    'source_record_id':x['source_record_id'],'family_chunk':ci,'witness_sha256':witness_sha,'witness_verification':witness_verification,'candidate_ledger_sha256':sha_file(cand),'candidate_count':sum(1 for _ in cand.open())-1}
   atomic_json(recp,d);records_by_id[x['source_record_id']]=d
   if status=='SAT_P6_RESIDUAL' and terminal:sat_found=True;break
 ordered=[]
 for x in rows:
  d=records_by_id.get(x['source_record_id'])
  if d is None:
   d={'schema':'p6-decision-record-v2','decision_id':'family-'+x['source_record_id'],'equivalence_key':'exact-residual:'+hx(x['r']),'representative_residual_hex':hx(x['r']),'solver_source_sha256':hashes['backend_source_sha256'],'solver_binary_sha256':hashes['backend_binary_sha256'],'input_sha256':'0'*64,'status':'INCOMPLETE_P6_RESIDUAL','exit_code':30,'terminal':False,'wall_seconds':0.0,'user_seconds':0.0,'system_seconds':0.0,'peak_rss_kb':0,'result_sha256':'0'*64,'source_record_id':x['source_record_id']}
  ordered.append(d)
 ledger_bytes=''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in ordered).encode();atomic_bytes(out/'decision_ledger.jsonl',ledger_bytes)
 ru1=resource.getrusage(resource.RUSAGE_SELF);rc1=resource.getrusage(resource.RUSAGE_CHILDREN);total_user=(ru1.ru_utime-ru0.ru_utime)+(rc1.ru_utime-rc0.ru_utime);total_sys=(ru1.ru_stime-ru0.ru_stime)+(rc1.ru_stime-rc0.ru_stime);wall=time.monotonic()-start
 ledger_sha=sha_bytes(ledger_bytes)
 if a.resume and completed_chunks==0 and backend_user==backend_sys==prep_user==prep_sys==0.0 and prior_summary is not None:
  compatible=(prior_summary.get('decision_ledger_sha256')==ledger_sha and prior_summary.get('input_ledger_sha256')==hashes['input_ledger_sha256'] and prior_summary.get('candidate_binary_sha256')==hashes['candidate_binary_sha256'] and prior_summary.get('backend_binary_sha256')==hashes['backend_binary_sha256'] and prior_summary.get('declared_pair_count')==len(rows))
  if compatible:
   check={'schema':'p6-family-resume-check-v1','all_records_reused':True,'decision_ledger_sha256':ledger_sha,'run_user_seconds':total_user,'run_system_seconds':total_sys,'run_wall_seconds':wall}
   atomic_json(out/'resume_check_summary.json',check);print(json.dumps(prior_summary,sort_keys=True));return
 counts={k:0 for k in ['SAT','UNSAT','INCOMPLETE','ERROR']}
 for d in ordered:
  s=d['status'];counts['SAT' if s=='SAT_P6_RESIDUAL' else 'UNSAT' if s=='UNSAT_P6_RESIDUAL' else 'ERROR' if s.startswith('ERROR') else 'INCOMPLETE']+=1
 terminal=(counts['SAT']>0 and counts['ERROR']==0) or (counts['UNSAT']==len(rows) and counts['INCOMPLETE']==counts['ERROR']==0)
 summary={'schema':'p6-family-branch-summary-v1','first_a_hex':hx(A),'input_ledger_path':str(a.branch.resolve()),'input_ledger_sha256':hashes['input_ledger_sha256'],'input_total_pair_count':len(allrows),'declared_pair_count':len(rows),'historical_fixed_oriented':historical,
  'chunk_size':a.chunk_size,'grouping':a.grouping,'group_count':len(groups),'singleton_groups':len({(x['singleton_row'],x['singleton_col']) for x in rows}),'planned_chunks':len(chunks),'completed_candidate_chunks':completed_chunks,'SAT_count':counts['SAT'],'UNSAT_count':counts['UNSAT'],'INCOMPLETE_count':counts['INCOMPLETE'],'ERROR_count':counts['ERROR'],'terminal':terminal,
  'preparation_user_seconds':prep_user,'preparation_system_seconds':prep_sys,'backend_user_seconds':backend_user,'backend_system_seconds':backend_sys,'total_user_seconds':total_user,'total_system_seconds':total_sys,'total_wall_seconds':wall,'amortized_user_seconds_per_pair':total_user/len(rows),'peak_rss_kb':peak,
  'candidate_occurrences':candidate_occ,'chunk_unique_leaf_caps_sum':chunk_unique,'shared_candidate_nodes':shared_nodes,'decision_ledger_sha256':ledger_sha,**hashes}
 atomic_json(out/'branch_summary.json',summary);print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
