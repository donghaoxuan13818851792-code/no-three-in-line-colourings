#!/usr/bin/env python3
"""Independent exhaustive verifier for a claimed P6 11x11 colouring."""
from __future__ import annotations
import argparse, json, sys
from collections import Counter
from pathlib import Path

N=11
EXPECTED=sorted([21,21,20,20,20,19], reverse=True)

def verify(path: Path) -> dict:
    text=path.read_text(encoding='utf-8')
    toks=text.split()
    result={'schema':'p6-independent-witness-verifier-v1','path':str(path),'token_count':len(toks)}
    if len(toks)!=121:
        result.update(valid=False,reason='expected exactly 121 integer colour labels')
        return result
    try: vals=[int(x) for x in toks]
    except ValueError:
        result.update(valid=False,reason='non-integer colour label')
        return result
    labels=sorted(set(vals))
    if len(labels)!=6:
        result.update(valid=False,reason='expected exactly six colour labels',labels=labels)
        return result
    counts=Counter(vals)
    result['class_sizes']={str(k):counts[k] for k in labels}
    if sorted(counts.values(),reverse=True)!=EXPECTED:
        result.update(valid=False,reason='wrong class-size multiset')
        return result
    collinear=0; violations=[]; all_triples=0
    for a in range(121):
        ar,ac=divmod(a,N)
        for b in range(a+1,121):
            br,bc=divmod(b,N)
            for c in range(b+1,121):
                all_triples+=1
                cr,cc=divmod(c,N)
                if (br-ar)*(cc-ac)==(bc-ac)*(cr-ar):
                    collinear+=1
                    if vals[a]==vals[b]==vals[c]:
                        violations.append({'points':[a,b,c],
                                           'coords':[[ar,ac],[br,bc],[cr,cc]],
                                           'colour':vals[a]})
    result.update(unordered_triples_checked=all_triples,collinear_triples_checked=collinear,
                  monochromatic_collinear_triples=len(violations),violations=violations[:100])
    if all_triples!=287980 or collinear!=6992:
        result.update(valid=False,reason='internal exhaustive triple-count mismatch')
    elif violations:
        result.update(valid=False,reason='monochromatic collinear triple found')
    else:
        result.update(valid=True,reason='all P6 witness conditions passed')
    return result

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('grid',type=Path);ap.add_argument('--json-out',type=Path)
    a=ap.parse_args()
    try:r=verify(a.grid)
    except Exception as e:
        print(f'P6_WITNESS_VERIFIER_ERROR {e}',file=sys.stderr);return 2
    payload=json.dumps(r,indent=2,sort_keys=True)+'\n'
    if a.json_out:a.json_out.write_text(payload)
    print(('P6_WITNESS_VALID' if r.get('valid') else 'P6_WITNESS_REJECTED'),json.dumps(r,separators=(',',':')))
    return 0 if r.get('valid') else 1
if __name__=='__main__':raise SystemExit(main())
