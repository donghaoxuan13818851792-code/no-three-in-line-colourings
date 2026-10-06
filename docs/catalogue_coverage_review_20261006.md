# Catalogue and search scope review — 6 October 2026

This is a repository review note, not an edit of the frozen preprint and not
a new global UNSAT certificate. Execution checks from the local campaign
must remain separate from the mathematical arguments below.

## Q10 reference predicate

For a frozen size-22 anchor A, the size-20 catalogue used by
`q10_cap20_enum.cpp` has the following reference family F(A):

1. B is a 20-point arc contained in G11 minus A.
2. Every row and column contains one or two points of B. Exactly two rows
   and two columns contain one point.
3. For every grid line L,
   `|L minus (A union B)| <= 8`.

These conditions are necessary for any size-20 colour class in a Q10
completion: after A and B, four remaining colour classes can cover at most
eight points of any line. In particular, each length-11 row and column
requires at least one point of B because A contributes two. Cardinality 20
then forces exactly two singleton rows and columns. The main-diagonal lower
bounds are included by the same line-capacity inequality.

## Generator structure and coverage obligations

The 55 unordered singleton-row pairs and 55 unordered singleton-column pairs
partition F(A) into 3,025 disjoint cases. For a fixed case, each row pattern
enumerates every permitted one- or two-point subset of its nine non-anchor
points. Column quotas enforce the fixed singleton-column choice. Choosing
the next unassigned row by its number of compatible patterns changes order,
not the set of row-pattern combinations.

Secant blocking excludes points that would create a collinear triple with
already selected points. The additional within-pattern test rejects only
triples using a new two-point pattern and an earlier point. Terminal scans
check all 628 maximal lines directly.

The column feasibility test counts available points in unassigned rows; this
is an upper bound on what later row patterns can contribute. The tight-line
feasibility test likewise counts available unblocked points without imposing
all future row-pattern restrictions, so it is an upper bound. Rejecting a
state only when this upper bound cannot meet the necessary lower bound is
sound. Restoring chosen points, blocked points, assigned rows and column
counts after every branch is essential to the argument.

A time limit is checked separately: an interrupted enumerator prints
`INCOMPLETE` and returns 30. Only complete exit-zero cases belong in the
catalogue coverage ledger. File hashes and the 3,025-key identity alone do
not prove exhaustive execution; the final source/run binding, exact case
coverage and terminal records are separate obligations.

The local membership replay validates every supplied member against this
predicate. A membership pass does **not** show that every member of F(A) was
emitted. The mathematical explanation above supplies a reviewable generator
argument; a separately implemented reconstruction or independently checkable
exhaustive coverage certificate remains the independent execution obligation.

## Q10 residual join

`capset_join.cpp` orders the four size-20 classes by catalogue index, filters
for disjointness, and retains the necessary residual line capacities after
each selected class. The remaining capacities are six, four and two points
per line as the number of unselected colour classes decreases. Final witness
checking constructs the forced 19-point complement and tests every maximal
line. The 55 root-row-pair cases partition the possible first selected class.

This explains the reference search and the necessity of the capacity cuts.
It does not replace verification of every bitset filter, every root shard,
the actual terminal decisions or an independent global UNSAT certificate.
The existing DRAT/IDRUP sector proofs cover only the documented extendible
sector and cannot supply that global conclusion.

## P123 independent terminal problem

Four disjoint size-21 classes leave 37 points. With every colour class of
size at most 21, the remaining unordered sizes are exactly (21,16), (20,17)
or (19,18), the P1/P2/P3 residual cases. The independent verifier expands
grid lines into explicit NAE triples and imposes both residual colour-size
upper bounds of 21. Fixing one residual point's colour removes only the
interchange of the two residual colours.

The sixty residue classes used locally are disjoint and cover all 127,491
representative indices. Every sixth-class group is the union of ten local
classes, permitting detailed comparison with the historical six-shard
production counters. Fresh independent execution remains conditional on
the frozen size-21 catalogue and the branch reductions.

## P6 and P45 boundaries

P6's manuscript transfer predicate excludes extensions into the residual
outside its two fixed size-21 classes. The frozen preprint itself asks for
confirmation that the recorded final filter matches this predicate. A replay
using delivered candidate lists cannot establish their completeness or the
266,771,874-pair global coverage.

The available P45 compression package explicitly records global P4 and P5
as `UNRESOLVED` and reports no global UNSAT certificate. Its 57,755 fixed
branch results and cross-method counter agreement must not be promoted to
the manuscript's 544,481,464-triple global scope.
