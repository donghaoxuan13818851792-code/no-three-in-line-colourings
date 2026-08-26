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

Thus the possible class-size profiles are reduced to nondecreasing six-part deficit vectors with total 11.

## Complete profile coverage

There are exactly 44 deficit profiles before using the size-22 compatibility obstruction. They split according to the number of zero deficits, equivalently the number of size-22 colour classes:

- 16 profiles with at least three zero deficits;
- 11 profiles with exactly two zero deficits;
- 10 profiles with exactly one zero deficit;
- 7 profiles with no zero deficits.

The central coverage identity is therefore

\[
\boxed{44 = 16 + 11 + 10 + 7}.
\]

The 16 profiles with at least three size-22 classes are impossible because three pairwise disjoint size-22 colour classes would form a triangle in the verified size-22 disjointness graph, while that graph is triangle-free.

After this reduction, the remaining 28 profiles are

\[
\boxed{28 = 11_R + 10_Q + 7_P}.
\]

## Top-level profile families

The final exhaustive proof is organised as follows:

- **R:** at least two size-22 classes.
  - **R0:** three or more size-22 classes; eliminated by triangle-freeness of the size-22 disjointness graph.
  - **R1:** exactly two size-22 classes; 11 residual deficit profiles proceed to the certified two-size-22 computation.
- **Q:** exactly one size-22 class; 10 profiles.
- **P:** no size-22 class; 7 profiles.

The R computation is therefore not simply a 1,309-leaf search over the whole phrase “at least two size-22 classes”. The 1,309 residual leaves cover only R1 after R0 has already been removed mathematically/computationally by the verified triangle-free graph obstruction.

See [`../g11/R/README.md`](../g11/R/README.md) for the R evidence chain.

## Proof obligations

For each branch the repository separates four levels:

1. **mathematical coverage** — why every hypothetical colouring enters a branch;
2. **catalogue/orbit coverage** — why every required outer object is represented;
3. **work-item coverage** — why the generated residual instances cover the branch without gaps;
4. **terminal correctness** — why every residual is genuinely SAT or UNSAT.

The final G11 theorem is valid only when all four levels are complete for every branch.
