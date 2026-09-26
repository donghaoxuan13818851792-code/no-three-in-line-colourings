# Exact cap-packing reduction for profiles Q1--Q4

The first four profiles having exactly one size-22 colour have sizes

* Q1: 22,21,21,21,21,15;
* Q2: 22,21,21,21,20,16;
* Q3: 22,21,21,21,19,17;
* Q4: 22,21,21,21,18,18.

## Common fixed-cap reduction

The unique size-22 class is one of the 89 audited D4 representatives.
After fixing it, choose three pairwise-disjoint size-21 caps.  The four
fixed classes occupy 85 points and leave 36.  A bipartition of the
residual into caps of size at most 21 has unordered sizes

`21+15`, `20+16`, `19+17`, or `18+18`,

exactly Q1--Q4.  Q2--Q4 have exactly three size-21 classes.  Q1 has four;
choosing any three leaves the fourth in the residual split.  This causes
duplication but no omission.

The size-22 representatives remove D4 symmetry.  For one fixed cap, all
of the 1,019,640 audited size-21 masks disjoint from it are retained in
increasing global mask order.  Requiring the three selected local IDs to
increase removes their colour permutations.

## Local compatibility and capacity

For each fixed size-22 cap, point-incidence and singleton-row/column
bitsets give the exact compatibility relation on its local size-21
candidates.  The second candidate is larger than and compatible with the
first.  The third is larger than the second and is taken from the
intersection of both earlier compatibility sets.  Thus every increasing
compatible triple occurs exactly once.

After the fixed cap and respectively one, two, or three selected caps,
the search applies the necessary line-capacity bound with four, three,
or two colours remaining:

`selected coverage on L >= |L| - 2*(remaining colours)`.

After the third selected cap this guarantees that no relevant line
contains more than four residual points.

## Exact residual search

The 36 residual points become Boolean variables for the final two
colours.  For every maximal line with three or four residual points, the
same sound fixed-point rules as in the P1--P3 computation maintain at
most two points of either truth value.  Global counts are at most 21.
The search recursively tries both values of every variable not fixed by
propagation, with the least residual point fixed to zero to remove colour
interchange.

Every returned model is rechecked as a disjoint cover of the residual,
with both sizes at most 21 and both masks meeting all 628 cap bounds.
Therefore a model is a Q1--Q4 colouring, while exhaustive failure for all
89 fixed-cap representatives proves that none exists.

## Complete run

The fixed-cap indices were partitioned modulo six.  Five shards handled
15 representatives and one handled 14.  All six exited with UNSAT code
20.  Aggregate counters were:

| quantity | total |
|---|---:|
| fixed size-22 representatives | 89 |
| tested first size-21 caps | 1,000,619 |
| passed first-cap capacity | 412,995 |
| tested second caps | 7,470,942 |
| passed second-cap capacity | 1,325,039 |
| tested third caps | 10,929 |
| passed third caps / residual instances | 670 |
| residual DPLL nodes | 10,210 |
| residual conflicts | 5,440 |
| satisfiable residuals | 0 |

The source received an independent read-only audit covering the fixed
D4 table, Q1's any-three-of-four reduction, cached local compatibility,
increasing-ID nesting, the three capacity levels, and the complete
36-bit residual DPLL.

## Reproduction

Build:

```text
clang++ -O3 -std=c++20 -Wall -Wextra \
  work/sat_agent/q1234_cap_packing.cpp \
  -o work/sat_agent/q1234_cap_packing
```

Run shard `s=0,...,5`:

```text
work/sat_agent/q1234_cap_packing --shard s 6
```

Frozen input hashes and per-shard evidence are recorded in
`q1234_cap_packing_manifest.tsv`.
