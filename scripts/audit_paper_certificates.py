#!/usr/bin/env python3
"""Independently check the manuscript's explicit matrices and small G11 layer.

Matrix validation uses both determinant triples and normalized line equations.
The G11 checks validate deposited catalogue members, graph/orbit arithmetic and
profile coverage; they do not assert exhaustive catalogue generation or certify
the unavailable R terminal proofs.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, combinations_with_replacement
import json
from math import gcd, isqrt
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[1]


def line_sets(n):
    equations = {}
    points = [(i % n, i // n) for i in range(n*n)]
    for i, j in combinations(range(n*n), 2):
        x1, y1 = points[i]; x2, y2 = points[j]
        a, b, c = y2-y1, x1-x2, x2*y1-x1*y2
        d = gcd(gcd(abs(a), abs(b)), abs(c))
        a, b, c = a//d, b//d, c//d
        if a < 0 or (a == 0 and b < 0):
            a, b, c = -a, -b, -c
        equations.setdefault((a,b,c), set()).update((i,j))
    return [sorted(v) for v in equations.values() if len(v) >= 3]


def audit_matrices():
    text = (ROOT/'paper/arxiv.tex').read_text()
    section = text.split(r'\section{Explicit upper-bound certificates}',1)[1].split(r'\section{Computational supplement}',1)[0]
    blocks = re.findall(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', section, re.S)
    assert len(blocks) == 3
    expected = {
        9: (5, [17,15,16,16,17], 2712, '43558895f3ed58cd7e8b7410742c28089526be9ff69fb22cdedf72a7866bf409'),
        10: (6, [20,20,20,20,10,10], 4448, '96efaf6aca921323fbdeeeb77d0dd54407b6ecb2bf786a2f457466d75912876a'),
        12: (7, [24,24,24,24,16,16,16], 10332, 'a379c6caf103cb60fce8c8baab051399418920cd013bf6df19f5dc5988a094a3'),
    }
    records = []
    for block, n in zip(blocks, (9,10,12)):
        parsed = [(int(i), list(map(int, row.split(',')))) for i,row in re.findall(r'\\paintrow\{(\d+)\}\{([\d,]+)\}',block)]
        assert [i for i,_ in parsed] == list(range(n,0,-1))
        rows = [row for _,row in parsed]
        assert len(rows) == n and all(len(row)==n for row in rows)
        colours = [v for row in rows for v in row]
        k, sizes, triples, sha = expected[n]
        assert set(colours) == set(range(1,k+1))
        assert [colours.count(i) for i in range(1,k+1)] == sizes
        canonical = ''.join(' '.join(map(str,row))+'\n' for row in rows).encode()
        actual_sha = hashlib.sha256(canonical).hexdigest()
        assert actual_sha == sha
        geometric = set()
        for i,j,kpoint in combinations(range(n*n),3):
            ax,ay=i%n,i//n; bx,by=j%n,j//n; cx,cy=kpoint%n,kpoint//n
            if (bx-ax)*(cy-ay)==(by-ay)*(cx-ax):
                assert not colours[i]==colours[j]==colours[kpoint], (n,i,j,kpoint)
                geometric.add((i,j,kpoint))
        by_lines = {triple for line in line_sets(n) for triple in combinations(line,3)}
        assert by_lines == geometric and len(geometric) == triples
        records.append({'grid':n,'colours':k,'class_sizes':sizes,'sha256':actual_sha,
                        'collinear_triples':triples,'monochromatic_collinear_triples':0,
                        'two_geometry_methods_agree':True})
    return records


def transform(mask, symmetry, n=11):
    result=0
    while mask:
        bit=mask & -mask; p=bit.bit_length()-1; x,y=p%n,p//n
        if symmetry>=4:x=n-1-x
        for _ in range(symmetry%4):x,y=y,n-1-x
        result |= 1 << (y*n+x); mask ^= bit
    return result


def audit_small_g11():
    n=11; full=(1<<121)-1
    profiles=[p for p in combinations_with_replacement(range(12),6) if sum(p)==11]
    distribution=Counter(p.count(0) for p in profiles)
    assert len(profiles)==44
    assert sum(v for k,v in distribution.items() if k>=3)==16
    assert distribution[2]==11 and distribution[1]==10 and distribution[0]==7
    caps=[int(x,16) for x in (ROOT/'g11/R/data/caps22_diag_independent.hex').read_text().split()]
    reps=[int(x,16) for x in (ROOT/'g11/R/data/caps22_d4.hex').read_text().split()]
    assert len(caps)==676 and len(set(caps))==676
    lines=[sum(1<<p for p in line) for line in line_sets(n)]
    assert len(lines)==628
    for mask in caps:
        assert mask <= full and mask.bit_count()==22
        assert all((mask&line).bit_count()<=2 for line in lines)
    images={c:[transform(c,s) for s in range(8)] for c in caps}
    assert set(reps)=={min(v) for v in images.values()} and len(reps)==89
    assert {m for v in images.values() for m in v}==set(caps)
    neighbours=[set() for _ in caps]; pairs=[]; feasible=[]
    for i,j in combinations(range(len(caps)),2):
        if caps[i]&caps[j]:continue
        pairs.append((i,j));neighbours[i].add(j);neighbours[j].add(i)
        residual=full^(caps[i]|caps[j])
        if all((residual&line).bit_count()<=8 for line in lines):feasible.append((i,j))
    assert len(pairs)==2138
    assert all(not(neighbours[i]&neighbours[j]) for i,j in pairs)
    assert len(feasible)==930
    orbits={min(tuple(sorted((images[caps[i]][s],images[caps[j]][s]))) for s in range(8)) for i,j in feasible}
    assert len(orbits)==119 and len(orbits)*distribution[2]==1309
    return {'profiles':44,'coverage_identity':[16,11,10,7],'caps_validated':676,
            'D4_orbits':89,'disjoint_pairs':2138,'triangle_free':True,
            'capacity_feasible_pairs':930,'pair_orbits':119,'R1_leaves':1309,
            'scope':'membership, orbit closure, graph, profile and leaf arithmetic only; no catalogue completeness or R proof-body claim'}


def audit_seed_and_displayed_arithmetic():
    text=(ROOT/'paper/arxiv.tex').read_text()
    def matrix(label):
        section=text.split(r'\label{'+label+'}',1)[1]
        body=section.split(r'\begin{pmatrix}',1)[1].split(r'\end{pmatrix}',1)[0]
        rows=[[int(v.strip()) for v in row.strip().split('&')] for row in body.split(r'\\') if row.strip()]
        assert len(rows)==8 and all(len(row)==8 for row in rows)
        return rows
    seed=matrix('eq:eight-seed');table=matrix('eq:eight-table')
    classes={c:{(x,y) for y in range(8) for x in range(8) if seed[y][x]==c} for c in range(1,5)}
    assert all(len(points)==16 for points in classes.values())
    determinants=0
    for points in classes.values():
        for (ax,ay),(bx,by),(cx,cy) in combinations(sorted(points),3):
            determinants+=1
            assert (bx-ax)*(cy-ay)!=(by-ay)*(cx-ax)
    mixed=0;memberships=0
    for y in range(8):
        for x in range(8):
            first,second=divmod(table[y][x],10)
            assert first in classes and second in classes
            for u,v in classes[first]:
                memberships+=1
                assert (2*x-1-u,2*y-1-v) not in classes[second]
            if first!=second:
                mixed+=1
                assert all(any((2*x-1-u,2*y-1-v) in points for u,v in points) for points in classes.values())
    assert determinants==2240 and memberships==1024 and mixed==8
    c6=text.split('three listed below contribute',1)[1].split('The supplement gives',1)[0]
    words=re.findall(r'\\\((\d+(?:\\,\d+)*)\\\)',c6)
    subtotals=[int(word.replace(r'\,','')) for word in words]
    total=int(re.search(r'C\(6\)=(\d+(?:\\,\d+)*)',c6)[1].replace(r'\,',''))
    assert len(subtotals)==4 and sum(subtotals)==total==2949015889
    return {'eight_seed_determinants':determinants,'absorption_memberships':memberships,
            'mixed_colour_sites_without_single_class_choice':mixed,
            'C6_displayed_subtotals':subtotals,'C6_sum':total,
            'C6_scope':'arithmetic of four displayed subtotals only, not 33-profile ledger audit or enumeration'}


def audit_admissible_prime_data():
    text=(ROOT/'paper/arxiv.tex').read_text()
    section=text.split(r'\label{eq:eight-primes}',1)[1].split(r'\end{equation}',1)[0]
    body=section.split(r'\begin{gathered}',1)[1].split(r'\end{gathered}',1)[0]
    listed=list(map(int,re.findall(r'\d+',body)))
    def prime(n):
        return n>=2 and (n==2 or (n%2!=0 and all(n%d for d in range(3,isqrt(n)+1,2))))
    directions=[(a,b) for a in range(-15,16) for b in range(-15,16) if gcd(abs(a),abs(b))==1]
    norms={a*a+b*b for a,b in directions}
    actual=sorted(q for q in norms if q%4==1 and prime(q))
    assert len(listed)==29 and listed==actual
    factors=set()
    for value in norms:
        divisor=2
        while divisor*divisor<=value:
            while value%divisor==0:
                factors.add(divisor);value//=divisor
            divisor+=1
        if value>1:factors.add(value)
    assert factors=={2,*listed}
    example=text.split('smallest admissible',1)[1].split('first grid',1)[0]
    p=int(re.search(r'p=(\d+(?:\\,\d+)*)',example)[1].replace(r'\,',''))
    assert p==185456518679 and prime(p) and p%8==7
    assert all(pow(p%q,(q-1)//2,q)==1 for q in listed)
    assert all(pow(norm,(p-1)//2,p)==1 for norm in norms)
    return {'primitive_directions_checked':len(directions),'distinct_norms_checked':len(norms),
            'listed_primes':listed,'all_prime_factors_accounted_for':True,
            'example_prime':p,'example_primality':'exact trial division through integer square root',
            'example_all_norms_quadratic_residues':True,
            'scope':'finite prime list and admissibility of displayed example; no smallest-prime search or infinite-family proof claim'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    start=time.time()
    result={'status':'PASS','upper_bound_matrices':audit_matrices(),'small_G11':audit_small_g11(),
            'seed_and_arithmetic':audit_seed_and_displayed_arithmetic(),
            'admissible_prime_data':audit_admissible_prime_data(),
            'elapsed_seconds':time.time()-start,'manuscript_sha256':hashlib.sha256((ROOT/'paper/arxiv.tex').read_bytes()).hexdigest()}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
