# Audit of `binary_residual_cnf.py`

Audited source:

the packaged `src/binary_residual_cnf.py`

SHA-256:

`8a9a28fd244e893cf9c10e94b5f5735dd16d4ef751be24c5cc28485da948b7a0`

No solver was run in this audit.

## Exact meaning of the formula

The four validated fixed masks have sizes 22, 21, 21, and 21 and are
pairwise disjoint, so their complement `R` has 36 points.  The variables
1 through 36 are in bijection with the points of `R`; a true variable
puts its point in the first residual colour and a false variable puts it
in the second.  Thus every Boolean assignment partitions every residual
point exactly once, without needing point-cover clauses.

For every three residual points on every maximal relevant line, the
generator emits

* the all-negative clause, forbidding all three from the first colour;
* the all-positive clause, forbidding all three from the second colour.

Consequently both truth classes are caps.  Conversely, if both classes
are caps, every one of these clauses holds.  The 628 maximal lines
contain every collinear triple, so the line part is exact.

The precheck `|R intersect L| <= 4` is safe and complete as a pruning
test: two caps can cover at most four points of a line.  It is not needed
for the logical exactness of the later clauses, but correctly rejects an
impossible prefix early.

On every length-11 line the two non-emptiness clauses require each
residual colour to occur.  They are redundant and valid: the other five
colours cover at most ten of the eleven points.  In particular, they
exclude a zero row or column.  Together with size and cap constraints,
they imply the required residual row and column deficit patterns; no
separate row/column target clauses are necessary for exactness.

It follows that the CNF, before the optional equal-size symmetry clause,
is satisfiable if and only if the fixed prefix has a completion by two
caps of the requested sizes.

## Cardinality encoding

The imported `local_repair.at_most` is a Sinz-style sequential counter.
For the 36 primary literals, the first call enforces

`number of true literals <= first_size`.

The second call is made on the negated primary literals and enforces

`number of false literals <= 36 - first_size`.

Since the two counts sum to 36, their conjunction is equivalent to
equality in both bounds.  It gives the intended residual sizes:

| profile | first | second |
|---|---:|---:|
| Q2 | 20 | 16 |
| Q3 | 19 | 17 |
| Q4 | 18 | 18 |

The auxiliary ranges are disjoint: the first starts at 37, and the second
starts one above the maximum variable returned by the first.  The DIMACS
header uses the final maximum.  I additionally exhaustively tested
`at_most` for every primary assignment with 0 through 5 literals and
bounds from -1 through `n+1`; existential satisfiability over the
auxiliary variables agreed with the mathematical at-most predicate in
every case.

## Symmetry

For Q2 and Q3 the two residual colours have different sizes, so their
labels are distinguished.  For Q4 they both have size 18.  Variable 1
corresponds to the least-index residual point, and clause `[1]` orients
that point into the first colour.  Exactly one of a residual split and
its colour swap satisfies this clause, so it is a sound and complete
breaking of the two-colour interchange symmetry.

This orientation is not the same convention as comparing the two mask
integers numerically, but either convention removes the same order-two
symmetry.  The script does not canonicalize permutations of the three
fixed size-21 caps; that is an upstream prefix-enumeration concern and
can cause duplication only, not omission or unsoundness.

## Input validation

The generator checks:

* all mask bits lie among the 121 grid points;
* fixed sizes are exactly 22, 21, 21, 21;
* fixed masks are pairwise disjoint;
* every fixed mask is a cap on all 628 maximal lines;
* the size-22 cap has multiplicity two in every row and column;
* each size-21 cap has one singleton row and column; and
* the three singleton rows, and separately columns, are distinct.

The last distinctness tests are necessary.  If `t` of the three
size-21 caps shared a singleton row, the two residual colours would have
to cover `3+t` points of that row, which is impossible when `t >= 2`.
The same argument applies to columns.

## Paths and artifacts

The packaged source resolves its sibling helper directory relative to
`Path(__file__)`, so extraction location does not affect imports.
correctly locates both imported modules.  This remains independent of
the process working directory.

The output argument is resolved relative to the caller's working
directory and stored as an absolute path in metadata.  The generator and
CNF paths in the JSON are therefore machine-specific; hashes and logical
content remain reproducible, but a manifest intended to move between
machines should not compare those path strings literally.  Concurrent
writers must also use distinct output paths because the temporary name
is deterministically `OUTPUT.tmp`.

The CNF body, header clause count, final variable count, ASCII byte count
and SHA-256 construction are internally consistent by inspection.
`--audit-lines` additionally compares the maximal-line enumeration with
all collinear point triples.  Running `python3 -m py_compile` and the
command-line help path succeeded.

Conclusion: no logical, cardinality, symmetry, or import-root defect was
found.  The only noted limitations are portable absolute-path metadata
and the expected duplicate-prefix responsibility left to the caller.

## Addendum: P2/P3 generalization

The generator was subsequently generalized.  The audited new source
SHA-256 is

`5dea47c646487e36d74e96ddcbf2014fc0e070cac2e2c5f000152d43ec643c73`.

The original Q path now explicitly recognizes fixed sizes
`22,21,21,21`; the new P path recognizes `21,21,21,21`.  Every other
fixed-size sequence is rejected.  For P, the four masks leave 37 points
and the permitted first sizes are:

| profile | first | second |
|---|---:|---:|
| P2 | 20 | 17 |
| P3 | 19 | 18 |

The same two at-most counters therefore impose the exact required
sizes.  P rejects first size 18.  Neither P pair has equal sizes, so no
additional colour-swap symmetry clause is needed.

The singleton validation is correctly generalized: a fixed mask of size
`s` must have `22-s` singleton rows and the same number of singleton
columns, while every section is still required to have multiplicity one
or two.  All four P singleton rows and all four singleton columns must
be distinct.  This is necessary because if two selected size-21 caps
shared a singleton row, the residual would have at least five points on
that row, exceeding the capacity of two residual caps.

Residual size, line-capacity, NAE triple clauses, length-11 non-emptiness,
cardinality allocation and artifact construction otherwise remain
unchanged and apply verbatim to 37 variables.  Syntax compilation and
the generalized help path succeed.

No defect was introduced by the P generalization.  As a minor metadata
versioning observation, the schema string remains
`grid11-binary-residual-cnf-v1` despite its enlarged family support;
consumers should key on the newly supplied `family`, `profile`, and
`fixed_sizes` fields rather than assuming that v1 means Q-only.
