# Q10 dominance and unconditional row-search audit (2026-07-22)

## Correct predecessor calculation

Write the Q10 sizes as

`A=22, T=20, B=20, C=20, D=20, E=19`,

where `T` is the size-20 cap to which an unblocked extension point is
added.  The point has exactly one donor colour in a complete colouring.
After moving it to `T`, the sorted profiles are:

| donor | labelled change | sorted result | ledger branch | certified status |
|---|---|---|---|---|
| `A`, size 22 | `22->21`, `T:20->21` | `(21,21,20,20,20,19)` | P6 | UNKNOWN |
| `B`, `C`, or `D`, size 20 | donor `20->19`, `T:20->21` | `(22,21,20,20,19,19)` | Q9 | INCOMPLETE |
| `E`, size 19 | `19->18`, `T:20->21` | `(22,21,20,20,20,18)` | Q8 | INCOMPLETE |

The implemented conditional corner test accepts a corner already in the
fixed size-22 cap.  Consequently its rejection step does not require P6 to
be UNSAT, but it does require both Q8 and Q9 to be UNSAT.  Neither is
certified.  Q1--Q7 do not license this Q10 rejection.

## Coverage ledger actually present

The authoritative branch ledger is
`G11_six_colour_method_brief_v2/02_BRANCH_STATUS.csv`.  It marks P6 UNKNOWN,
Q8 INCOMPLETE, and Q9 INCOMPLETE.  The audited deficit partition is
`grid11_six_colour_status_transfer_20260720/Source_Profiles/profile_ledger_audit.txt`.

The unconditional Q8/Q9 plan has 89 fixed-cap branches, represented by 89
`Q89` formulas.  Its source/coverage audit is
the preserved Q8910 selector audit. That audit proves
the meaning and completeness of the *formulas*, but explicitly says all 89
branches must still be certified UNSAT.  It does not provide solver proofs.
The only generated example found locally is fixed-cap index 0; its solver
record says `command terminated abnormally` after about 1093 seconds and
contains no UNSAT result or checked proof.  Thus there is no Q8/Q9 proof
coverage ledger to cite.

For comparison, Q1--Q4 do have an independent completed audit at
the preserved Q1234 independent result audit, but those
profiles are not the Q10 donor outcomes above.

## Code correction and status of earlier runs

`q10_cap20_enum.cpp` now disables dominance by default.  The conditional
rule can only be enabled with the conspicuous option
`--allow-unverified-dominance`; such runs print a warning and use a
`CONDITIONAL_*` status.  They are heuristic construction searches and are
invalid for exhaustive Q10 coverage.  Every earlier run of that program
which used the dominance rule, including the 200-million-node fixed-index-0
benchmark, has the same conditional/heuristic status.

## Unconditional Q10 row search

`q10_row_search.cpp` does not use extension dominance or any predecessor
profile.  Its pruning is unconditional:

1. A size-22 fixed cap has two points in every row and column.  Each residual
   row has nine points.  Five residual cap colours, each occurring at most
   twice on a row, must therefore have multiplicities `2,2,2,2,1`.
   The singleton-row totals are `2,2,2,2,3`, giving sizes
   `20,20,20,20,19` exactly.
2. When a row is committed, a proposed point of colour `c` is forbidden if
   it lies on a secant through two earlier `c` points.  A triple with two
   points in the new row and an earlier point is impossible because the two
   new points determine the horizontal row.  Hence row transitions lose no
   cap assignment.
3. Column counts at most two are direct cap consequences.  Requiring future
   support for a colour absent from a column is necessary because the other
   five full colours cover at most ten of its eleven points.  The identical
   argument applies to each length-11 diagonal.
4. On a residual intersection of length `m`, let `S` be a subset of the five
   residual colours.  At most `2|S|` points can receive `S`, and the colours
   outside `S` cover at most `2(5-|S|)` points.  Thus the necessary interval
   is
   `max(0,m-2(5-|S|)) <= #(points assigned to S) <= min(m,2|S|)`.
   The domain Hall checks reject only when no assignment can meet this
   interval.
5. Ordering first occurrences of the four equal size-20 colours removes only
   their global S4 label symmetry.

The program now also treats the 89-cap input table as untrusted: it checks
the fixed set's size, row/column counts, and no-three-in-line property, and
the final validator rechecks all six colour classes.

These facts make the row/secant/column/Hall rules sound without Q1--Q9.
They do not make a node-limited run a proof: exit 30 remains INCOMPLETE.
