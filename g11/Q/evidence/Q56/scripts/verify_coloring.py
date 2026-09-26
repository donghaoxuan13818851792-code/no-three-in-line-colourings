#!/usr/bin/env python3
"""Independent determinant verifier for a future 11x11 colour matrix."""
import argparse,itertools
p=argparse.ArgumentParser(); p.add_argument('matrix'); a=p.parse_args()
rows=[list(map(int,x.split())) for x in open(a.matrix) if x.strip()]
if len(rows)!=11 or any(len(x)!=11 for x in rows): raise SystemExit('matrix must be 11x11')
labels=[c for x in rows for c in x]
if all(0<=c<=5 for c in labels): pass
elif all(1<=c<=6 for c in labels): rows=[[c-1 for c in x] for x in rows]
else: raise SystemExit('labels must be 0..5 or 1..6')
bad=[]; triples=0; relevant=0
for a0,b0,c0 in itertools.combinations(range(121),3):
    triples += 1
    ax,ay=a0%11,a0//11; bx,by=b0%11,b0//11; cx,cy=c0%11,c0//11
    if (bx-ax)*(cy-ay)==(by-ay)*(cx-ax):
        relevant += 1
        if rows[ay][ax]==rows[by][bx]==rows[cy][cx]: bad.append((a0,b0,c0))
if triples!=287980 or relevant!=6992: raise SystemExit('geometry count mismatch')
if bad: raise SystemExit('monochromatic collinear triple: '+repr(bad[:5]))
print('COLORING_VERIFY PASS determinant_triples=287980 collinear_triples=6992')
