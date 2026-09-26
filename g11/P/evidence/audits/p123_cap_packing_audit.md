# Independent source audit: `p123_cap_packing.cpp`

Audited source SHA-256:

`1304e1890ac7ecea4a4cbb536b4ed0c0ee5e0e3d7e6080bf3d87c2a324b9d37f`

Included frozen P1 source SHA-256:

`5c43c81a5b4a830c9a18c4eaf7197d9b8a4d8eefc7881f8960fbf4057a6127e0`

Compiled binary SHA-256:

`195f51106e616e026303206a43ded6e61edb0ed9c7001211d2971ed5cc0d7371`

## Profile reduction

Four disjoint size-21 caps use 84 points and leave 37.  If the residual
is split into two caps, each of size at most 21, their unordered sizes
must be exactly one of

`21+16`, `20+17`, or `19+18`.

These are precisely P1, P2, and P3.  Conversely every colouring in one
of those profiles contains at least four size-21 classes and therefore
appears in this reduction.

## Four-cap prefix coverage

The inherited cap files contain every size-21 cap that can occur in a
colouring.  The first cap is restricted to a D4-canonical representative
and all four IDs are increasing.  The standard global-minimum argument
shows that this covers every unordered four-set modulo D4 and colour
permutation.

At depth two the candidate bitset enforces disjointness and different
singleton rows and columns from the first cap.  Every third candidate
comes from that bitset and is checked against the second; every fourth
candidate comes from the resulting third list and is checked against the
third.  Inductively, all pairs in a prefix are compatible.  Conversely,
every compatible increasing four-set occurs in these loops.

Distinct singleton rows and columns are necessary: if `t` of the four
large caps have their singleton on one row, their complement has `3+t`
points in that row, while two residual caps can cover at most four.
Thus `t <= 1`; the column argument is identical.

The depth-`k` test

`selected coverage on L >= |L| - 2(6-k)`

is necessary for every subset of `k` colours.  At depth four it is
equivalent to at most four residual points on every line.  Hence no valid
prefix is pruned, and every residual checker call satisfies its asserted
line-capacity invariant.

## Exactness of the residual DPLL

The 37 residual points are bijected with bits 0 through 36.  A one bit
and a zero bit are the two residual colours.  For every maximal line
meeting the residual in three or four points, the checker stores exactly
that local-variable mask.

For each stored constraint, propagation maintains

`number of assigned ones <= 2` and
`number of assigned zeros <= 2`.

If either count exceeds two it reports a conflict.  If either count
equals two, all still-free variables on that line are forced to the
other value.  These rules are logical consequences of the two cap
bounds.  At a fixed point they need not decide every variable, so the
search branches on an unassigned variable and recursively tries both
truth values.  Therefore the propagation is sound and the branching is
complete.  On a fully assigned line, the same count checks are exactly
the cap conditions.  Lines with fewer than three residual points need
no constraint, and lines with more than four have already been rejected.
Every collinear triple lies on one of the 628 maximal lines.

The global propagation similarly maintains at most 21 ones and at most
21 zeros.  When either count reaches 21 it soundly forces every remaining
variable to the other value.  A leaf is accepted exactly when both
counts are at most 21.  Since they sum to 37, the accepted sizes are
precisely the three pairs above.

Bit 0 is initially assigned zero.  This is a complete residual-colour
symmetry break: for every two-cap split, exactly one of it and its colour
swap has bit 0 equal to zero.  It remains valid when the two sizes are
unequal because the two residual colour names are not otherwise fixed.

The `force` routine preserves the invariant `ones` is a subset of
`assigned`, detects a forced-value conflict before mutation, and assigns
all variables in its mask consistently.  Each successful propagation
strictly enlarges `assigned`, so the fixed-point loop terminates.  The
37-bit masks, signed 8-bit local IDs, 628-entry constraint array and
16-bit degree counters are all within their ranges.  Branch scoring
affects order only.

For a returned model, the code independently reconstructs the two global
masks and checks disjoint cover, size bounds, and all 628 line bounds
before reporting a solution.

## Build and smoke evidence

`clang++ -O3 -std=c++20 -Wall -Wextra -fsyntax-only` succeeds; the only
warning is the already known unused parameter in an unused function of
the included P1 source.

For representative zero, the prefix counters are forced to equal the
audited P1 search through depth four, and they do:

| depth | tested | passed |
|---:|---:|---:|
| 2 | 21,762 | 19,121 |
| 3 | 182,796,760 | 226,833 |
| 4 | 3,470,815 | 253 |

All 253 depth-four prefixes were sent to the residual checker.  It
visited 3,863 DPLL nodes, found 2,058 propagation conflicts, and found
zero satisfiable residuals.  The process exited 20.

Smoke output SHA-256:
`60770913a1f6ffe89e82cf299b7bc0bf7dec0f2fa895608ee920674fb4b10eb0`.

Conclusion: no completeness, propagation, symmetry, prefix-nesting, or
range error was found.  Subject to the separately audited cap-list
completeness, six normal UNSAT shard exits cover P1, P2, and P3.

