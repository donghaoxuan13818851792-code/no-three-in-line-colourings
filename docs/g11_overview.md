# G11 overview

## Problem

Decide whether the \(11\times11\) integer grid admits a six-colouring with no monochromatic collinear triple.

A colour class is therefore a no-three-in-line set (an arc).

## Long-line rigidity

Every row, every column, and each of the two main diagonals contains 11 points.

A single colour can occur at most twice on any line. Six colours must cover all 11 points, so the multiplicity pattern on every such line is necessarily

\[
(2,2,2,2,2,1).
\]

Consequences:

- every colour meets every row and every column;
- every colour meets both main diagonals;
- every colour class has size at most 22.

## Deficits

For colour class \(C_i\), define

\[
d_i = 22-|C_i|.
\]

Because each row contains either one or two points of colour \(i\), \(d_i\) is exactly the number of singleton rows for that colour. The same is true for columns.

Since the six classes cover 121 points,

\[
\sum_{i=1}^6 d_i = 6\cdot22-121=11.
\]

Thus the possible class-size profiles are reduced to integer partitions of the deficit total.

## Top-level profile families

The final exhaustive proof is organised by the number of size-22 colour classes:

- **R:** at least two size-22 classes;
- **Q:** exactly one size-22 class;
- **P:** no size-22 class.

The Q family contains ten positive-deficit patterns after the single zero deficit is fixed. The P family contains seven positive-deficit patterns.

## Proof obligations

For each branch the repository separates four levels:

1. **mathematical coverage** — why every hypothetical colouring enters a branch;
2. **catalogue/orbit coverage** — why every required outer object is represented;
3. **work-item coverage** — why the generated residual instances cover the branch without gaps;
4. **terminal correctness** — why every residual is genuinely SAT or UNSAT.

The final G11 theorem is valid only when all four levels are complete for every branch.
