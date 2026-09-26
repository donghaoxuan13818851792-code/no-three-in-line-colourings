# Exact cap-packing reduction for profiles P1--P3

The three profiles have class sizes

* P1: 21,21,21,21,21,16;
* P2: 21,21,21,21,20,17;
* P3: 21,21,21,21,19,18.

This computation is used after the independently separated size-22
branch.  Hence every colour class has size at most 21.

## Common four-cap reduction

Every P1--P3 colouring contains at least four size-21 colour classes.
Choose four of them.  They occupy 84 points and leave a 37-point
residual.  If that residual is partitioned into two caps, each has size
at most 21.  Up to interchange, their sizes can only be

`21+16`, `20+17`, or `19+18`.

These are exactly P1, P2, and P3.  Conversely every colouring in one of
the three profiles supplies such a four-cap prefix and residual
bipartition.

## Complete size-21 family and symmetry

The six frozen cap files contain every diagonal-feasible size-21 cap for
singleton rows zero through five.  Reflecting the first five files in
the middle row supplies singleton rows ten through six.  The loader
sorts the masks, rejects duplicates, validates their row and column
multiplicities, and asserts the audited total 1,019,640.

For any unordered four-cap packing, apply the eight D4 symmetries and
choose the globally least image of any of its four masks.  The designated
first mask is individually D4-canonical.  It is therefore complete to
take the first cap from the 127,491 individually canonical masks and to
require the other three IDs to be larger and increasing.  The six shards
use the representative index modulo six, so they are disjoint and
exhaustive.

## Prefix search

Every selected prefix is pairwise disjoint and has distinct singleton
rows and singleton columns.  The latter condition is necessary: if two
of the four selected caps shared a singleton row, their complement would
have at least five points on that row, which two residual caps cannot
cover.  Columns are identical.

After choosing `k` caps with union `U`, every maximal relevant line `L`
must satisfy

`|U intersect L| >= |L| - 2(6-k)`.

Each unselected cap contributes at most two points to a line, so this is
a necessary pruning rule.  The nested increasing candidate lists test
the one new pairwise compatibility relation at each depth and retain
every compatible ordered representative.  The program independently
constructs all 628 maximal lines and asserts their audited length
distribution before applying the rule.

At depth four the rule says that the 37-point residual has at most four
points on every relevant line.

## Exact residual DPLL

The residual points are bijected with Boolean variables.  Zero and one
are the two residual colours.  For every maximal line meeting the
residual in three or four points, propagation maintains at most two
assigned zeros and at most two assigned ones.  A count above two is a
conflict; a count equal to two forces every remaining point on that line
to the other value.

Global propagation likewise maintains at most 21 points of either
value.  At a fixed point the search chooses one unassigned variable and
recursively tries both values.  Thus the propagation is sound and the
branching is exhaustive.  Fixing the least residual point to zero removes
the interchange of the two residual colours without losing a partition.
Every returned model is reconstructed as two grid masks and rechecked
for disjoint cover, both size bounds, and all 628 line bounds.

Consequently a reported model is a valid P1--P3 colouring, and exhaustion
of every prefix proves that none exists.

## Complete run

All six shards exited with the normal UNSAT code 20.  Their aggregate
counters are:

| quantity | total |
|---|---:|
| first caps | 127,491 |
| tested depth 2 | 1,331,602,820 |
| passed depth 2 | 514,209,820 |
| tested depth 3 | 1,512,534,032,571 |
| passed depth 3 | 1,505,452,322 |
| tested depth 4 | 9,327,491,112 |
| passed depth 4 / residual instances | 708,638 |
| residual DPLL nodes | 10,280,082 |
| residual conflicts | 5,494,360 |
| satisfiable residuals | 0 |

The prefix counts through depth four agree exactly with the independently
audited P1 cap-packing enumeration.  A separately authored verifier also
reconstructs the cap list and lines using two 64-bit words and all point
pairs, re-enumerates every prefix, streams every residual mask, and solves
each residual by explicit NAE-triple DPLL rather than the line-count
solver used here.

## Reproduction

Build:

```text
clang++ -O3 -std=c++20 -Wall -Wextra \
  work/sat_agent/p123_cap_packing.cpp \
  -o work/sat_agent/p123_cap_packing
```

Run shard `s=0,...,5`:

```text
work/sat_agent/p123_cap_packing --shard s 6
```

The frozen hashes, per-shard outputs and logs are recorded in
`p123_cap_packing_manifest.tsv`.
