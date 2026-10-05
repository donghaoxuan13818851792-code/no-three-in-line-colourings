#!/usr/bin/env python3
"""Audit and summarize all 55x55 q10_cap20_enum shard records."""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path

PAT=re.compile(r"^(\d+),(\d+),(COMPLETE|INCOMPLETE) count (\d+)(?: least_eligible (\d+))?(?: extendible (\d+) nonextendible (\d+))? nodes (\d+) leaves (\d+) tight_lines (\d+) column_rejects (\d+) line_rejects (\d+)(?: self_secant_rejects (\d+))? seconds ([0-9.eE+-]+)(?:,exit=(\d+))?$")
def main():
 ap=argparse.ArgumentParser();ap.add_argument('log',type=Path);ap.add_argument('--json',type=Path);a=ap.parse_args()
 rows=[]
 for n,line in enumerate(a.log.read_text().splitlines(),1):
  m=PAT.match(line)
  if not m:raise SystemExit(f'malformed line {n}: {line!r}')
  rp,cp,status,count,least,ext,nonext,nodes,leaves,tight,cr,lr,self_sec,sec,exit_code=m.groups();rows.append({'row_pair':int(rp),'col_pair':int(cp),'status':status,'count':int(count),'least_eligible':int(least) if least is not None else None,'extendible':int(ext) if ext is not None else None,'nonextendible':int(nonext) if nonext is not None else None,'nodes':int(nodes),'leaves':int(leaves),'tight_lines':int(tight),'column_rejects':int(cr),'line_rejects':int(lr),'self_secant_rejects':int(self_sec) if self_sec is not None else None,'seconds':float(sec),'exit_code':int(exit_code) if exit_code is not None else None})
 keys=[(r['row_pair'],r['col_pair']) for r in rows]
 expected={(r,c) for r in range(55) for c in range(55)}
 exact=len(rows)==3025 and set(keys)==expected and all(r['status']=='COMPLETE' for r in rows) and all(r['exit_code'] in (None,0) for r in rows)
 result={'input':str(a.log),'input_sha256':hashlib.sha256(a.log.read_bytes()).hexdigest(),'records':len(rows),'unique_keys':len(set(keys)),'missing_keys':[list(x) for x in sorted(expected-set(keys))],'extra_keys':[list(x) for x in sorted(set(keys)-expected)],'duplicate_record_count':len(keys)-len(set(keys)),'complete_records':sum(r['status']=='COMPLETE' for r in rows),'incomplete_records':sum(r['status']=='INCOMPLETE' for r in rows),'nonzero_exit_records':sum(r['exit_code'] not in (None,0) for r in rows),'exact_total_count':sum(r['count'] for r in rows) if exact else None,'exact_least_eligible_count':sum(r['least_eligible'] for r in rows) if exact and all(r['least_eligible'] is not None for r in rows) else None,'exact_extendible_count':sum(r['extendible'] for r in rows) if exact and all(r['extendible'] is not None for r in rows) else None,'exact_nonextendible_count':sum(r['nonextendible'] for r in rows) if exact and all(r['nonextendible'] is not None for r in rows) else None,'exact_self_secant_rejects':sum(r['self_secant_rejects'] for r in rows) if exact and all(r['self_secant_rejects'] is not None for r in rows) else None,'total_nodes':sum(r['nodes'] for r in rows),'sum_shard_seconds':sum(r['seconds'] for r in rows),'max_shard_seconds':max((r['seconds'] for r in rows),default=0),'nonzero_shards':sum(r['count']>0 for r in rows),'max_shard_count':max((r['count'] for r in rows),default=0)}
 print(json.dumps(result,indent=2,sort_keys=True));
 if a.json:a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
