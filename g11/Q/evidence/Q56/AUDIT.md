# Audit and mathematical scope

The six colour-class profiles are sorted by size. Q5 and Q6 fix the certified
22-cap representative and reduce the remaining cells to exact cap enumeration
plus a residual two-colour problem. Every relevant line has at most two points
in a cap; the solver constructs all 628 maximal relevant lines and applies
exact cardinality, row, column, secant, and no-three-in-line constraints.

The only dominance premises are audited Q1--Q4 results:

* Q5: donor 20 -> Q3; donor 17 -> Q2.
* Q6: donor 19 -> Q4; donor 18 -> Q3.

Each move changes donor size by −1 and the receiving 20-class by +1; sorting
the resulting profile gives exactly the named Q2--Q4 branch. No P6, Q7, Q8,
Q9, Q10, unverified Q10 dominance, or heuristic defect/Hamming pruning is
used. See `audits/DOMINANCE_SCOPE.md` and the preserved residual-solver audit.

`scripts/audit_coverage.py` independently checks every shard's exit code,
UNSAT marker, completed count, terminal prefix, output presence, hashes, and
exact interval cover. `scripts/verify_coloring.py` tests all C(121,3)=287,980
determinant triples and checks all 6,992 collinear triples of any future 11x11
six-colour candidate.
