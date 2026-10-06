#!/usr/bin/env python3
"""Validate the existing 598 observed classes; do not claim exhaustive C(9)."""
import argparse
import csv
import hashlib
import io
from itertools import combinations
import json
from pathlib import Path
import zipfile


def normalize(text):
    labels={}
    return ''.join(str(labels.setdefault(c,len(labels)+1)) for c in text)


def images(text):
    result=[]
    for symmetry in range(8):
        transformed=['']*81
        for p,c in enumerate(text):
            x,y=p%9,p//9
            if symmetry>=4:x=8-x
            for _ in range(symmetry%4):x,y=y,8-x
            transformed[9*y+x]=c
        result.append(''.join(transformed))
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--csv',action='store_true',help='read the exact CSV excerpt directly instead of its ZIP')
    a=p.parse_args()
    member='grid9_five_colour_current_source_0.1.0/data/canonical_598/experiment_150000_class_representatives.csv'
    if a.csv:payload=a.archive.read_bytes()
    else:
        with zipfile.ZipFile(a.archive) as z:payload=z.read(member)
    rows=list(csv.DictReader(io.StringIO(payload.decode())))
    assert len(rows)==598 and {int(r['class_id']) for r in rows}==set(range(1,599))
    canonical=set();checks=0
    for row in rows:
        grid=row['representative'];assert len(grid)==81 and set(grid)==set('12345')
        for colour in '12345':
            points=[p for p,c in enumerate(grid) if c==colour]
            for i,j,k in combinations(points,3):
                checks+=1
                ax,ay=i%9,i//9;bx,by=j%9,j//9;cx,cy=k%9,k//9
                assert (bx-ax)*(cy-ay)!=(by-ay)*(cx-ax),row['class_id']
        transforms=images(grid);key=min(map(normalize,transforms))
        assert key==row['canonical'] and key not in canonical
        canonical.add(key)
        assert hashlib.sha256((key+'\n').encode()).hexdigest()==row['class_hash']
        matrix_text=''.join(' '.join(grid[i:i+9])+'\n' for i in range(0,81,9))
        assert hashlib.sha256(matrix_text.encode()).hexdigest()==row['representative_sha256']
        sizes=sorted(grid.count(c) for c in '12345')
        assert '-'.join(map(str,sizes))==row['sorted_colour_class_sizes']
        pure=sum(t==grid for t in transforms)
        up_to_colour=sum(normalize(t)==normalize(grid) for t in transforms)
        assert pure==int(row['pure_d4_stabilizer_size'])
        assert up_to_colour==int(row['geometric_stabilizer_up_to_colour_size'])
        assert 960//up_to_colour==int(row['d4_times_s5_orbit_size'])
        assert int(row['historical_frequency'])+int(row['new_range_frequency'])==int(row['frequency'])
    outcomes=sum(int(r['frequency']) for r in rows);assert outcomes==3817
    result={'status':'PASS','catalogue_member':member,'member_sha256':hashlib.sha256(payload).hexdigest(),
            'distinct_valid_classes':598,'observed_valid_outcomes':outcomes,'within_colour_triples_checked':checks,
            'geometry_canonicalisation_stabilizers_and_hashes':'PASS',
            'claim_boundary':'598 observed valid inequivalent classes; does not certify exhaustive manuscript count C(9)=743'}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
