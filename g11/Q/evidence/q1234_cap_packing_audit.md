# Independent source audit: `q1234_cap_packing.cpp`

Source SHA-256:

`2227dba3f45b344abd38e445b9636ecaa6f30258ae68f9c7e992029c990e2fa7`

Included frozen P1 source SHA-256:

`5c43c81a5b4a830c9a18c4eaf7197d9b8a4d8eefc7881f8960fbf4057a6127e0`

## Reduction and fixed-cap coverage

A fixed size-22 cap followed by three disjoint size-21 caps uses 85
points and leaves 36.  A split of those points into two caps, each of
size at most 21, has unordered sizes exactly

`21+15`, `20+16`, `19+17`, or `18+18`,

which are Q1 through Q4.  Conversely Q2--Q4 contain exactly three
size-21 classes, and Q1 contains four, any three of which can be selected
while the fourth appears in the residual split.

The unique size-22 colour is fixed to one of the 89 audited D4
representatives.  For each fixed mask, all reconstructed size-21 caps
disjoint from it are retained in increasing global mask order.  The
three chosen local IDs are strictly increasing, which removes their
colour permutations.  In Q1 this does not fully remove the choice of
which fourth equal-size cap is left to the residual, but that causes
duplication only.

The 89 fixed indices are sharded by index modulo the shard count.  With
six shards, indices 0 through 4 receive 15 fixed caps and index 5
receives 14; all 89 are covered once.

## Local compatibility and prefix search

For one fixed cap, `LocalCompatibility` builds point-incidence and
singleton-row/column bitsets over precisely the disjoint size-21
candidates.  A computed compatibility bitset removes every cap sharing:

* a grid point;
* the unique singleton row; or
* the unique singleton column.

The final word is masked to the candidate count.  The per-local cache is
safe: the outer cache vector has fixed size, assigning an inner vector
does not invalidate references to other entries, and each entry is
published only after it is complete.

The first loop checks every local candidate.  `clear_through` makes every
second local ID larger and compatible with the first.  Every third comes
from a copy of that bitset, is larger than the second, and is intersected
with the second's compatibility bitset.  Thus the selected three are
pairwise compatible and appear once in increasing order.  Conversely
every increasing compatible triple survives these incidence operations.

Singleton-row and singleton-column compatibility is necessary.  The
fixed size-22 cap has two points per row.  If `t` selected size-21 caps
share a singleton row, the two residual colours must cover `3+t` points
there, so their capacity four requires `t <= 1`.  Columns are identical.

After the fixed cap and respectively one, two, or three selected caps,
the line-capacity tests use four, three, or two remaining colours.  The
test

`selected coverage >= line length - 2*remaining colours`

is necessary for every valid completion and hence cannot prune a
solution.  After the third cap it exactly guarantees at most four
residual points on every line.

## Exact residual search

The 36 residual points are bijected with bits 0 through 35.  Every
maximal line with three or four residual points becomes a constraint on
exactly those local bits.  Lines with fewer than three need no
constraint, and the depth-three capacity invariant excludes larger
ones.

Propagation maintains at most two assigned zeros and at most two
assigned ones on each constraint.  A count above two is a conflict; a
count equal to two forces every free bit on that line to the other value.
The global rules analogously maintain at most 21 bits of either value.
Every force is a logical consequence, detects inconsistent earlier
assignments, and strictly enlarges the assigned set.

At a propagation fixed point, search selects an unassigned bit and tries
both values recursively.  The score and preferred first value affect
order only.  Hence the DPLL is complete.  A fully assigned model is
accepted exactly when both global counts are at most 21.  Since they sum
to 36, this gives exactly the four residual size pairs above.

Local bit 0, corresponding to the least residual grid point, is fixed to
zero.  Every residual bipartition has exactly one orientation under
colour swap satisfying this condition.  This remains complete for
unequal sizes because the caller does not preassign which residual name
has the larger size.  Q4's equal-size swap is also removed.

The 36-bit shifts, signed local IDs, 628-entry guarded constraint array,
and 16-bit occurrence counters are within range.  A returned residual
model is independently checked for disjoint cover, both size bounds, and
all 628 line bounds before a solution is printed.  The printed profile
sorts the two residual sizes and maps 21, 20, 19, or 18 to Q1--Q4.

## Inputs and build

The fixed table has 89 distinct masks and the constructor validates every
one for size 22 and the cap property.  The inherited loader reconstructs
the 1,019,640 size-21 masks and checks their sizes, row/column
multiplicities, uniqueness, and required diagonal feasibility.  Its
loader does not itself repeat the all-line cap check; that property and
the table's completeness were established by the separate exhaustive
input audit described in `p1_cap_packing_audit.md`.  The frozen input
hashes are:

```
caps22_d4.hex          234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40
caps21_r0_diag.hex     c4ba6b9aa11f4b9b7d1f7c2cd74eada8b727c40851c57e25a553142c4e12df3e
caps21_r1_diag.hex     62d025e2de26afe788057cc1a4525302d8a56c1be8ae4baf3d6d129f115b3895
caps21_r2_diag.hex     14f89035771e3428d0d6465d02ebea8430fb101cd0d6e3c972a8e98062d180e5
caps21_r3_diag.hex     92f7ea6aec073e2b335e089a56634f08ba34d1dab18e6b3c3935b70c2a157b42
caps21_r4_diag.hex     b1df4d6c48aeaad56d674b688e9398d05ef529409a9f4502fac212a7f4f78060
caps21_r5_diag.hex     47d59957a0f5f3d83298041cf4d8a3f99c5f5dc5211524c42e74235ea2561f9e
```

Syntax-only compilation succeeds with only the inherited unused-parameter
warning.  No coverage, compatibility-cache, propagation, branching,
cardinality, D4, or equal-colour symmetry defect was found.
