# Correctness and coverage of the P4/P5 canonical outer reduction

## 1. Original represented family

Let `C21` be the frozen complete catalogue of oriented diagonal-feasible size-21 caps after the certified nonextendibility filter. The audited outer cover fixes each D4-canonical cap representative in turn and scans an unordered pair of other catalogue caps. It retains triples satisfying:

- pairwise disjointness;
- pairwise distinct singleton rows;
- pairwise distinct singleton columns;
- the audited necessary line-capacity tests;
- nonextendibility of all three size-21 caps.

The supplied nine-shard ledger proves that this duplicate-retaining family is a complete cover of every P4/P5 outer triple modulo choosing a distinguished member and applying D4.

## 2. Canonical key

For an unordered triple `T={A,B,C}`, let

`K(T) = min { sort(gA,gB,gC) : g in D4 }`,

where masks are compared as unsigned 121-bit integers and sorted tuples are compared lexicographically.

All three cap masks are distinct because they are nonempty, equal-sized, and pairwise disjoint.

## 3. Lemma: the first member of K(T) is individually D4-canonical

Write `K(T)=(k0,k1,k2)` with `k0<k1<k2`. Suppose some `h in D4` satisfied `h(k0)<k0`. Then the first member of `sort(hk0,hk1,hk2)` would be at most `h(k0)`, hence strictly below `k0`. That transformed tuple would be lexicographically smaller than `K(T)`, a contradiction.

Therefore `k0` occurs in the audited list of individual D4 representatives.

## 4. Exactly-one canonical augmentation theorem

Retain a fixed-first occurrence `(F,A,B)` exactly when:

- `F<A` and `F<B`; and
- `sort(F,A,B)=K({F,A,B})`.

### Existence

For any outer triple orbit, take its canonical tuple `(k0,k1,k2)`. By the lemma, `k0` is an allowed fixed representative. The audited pair loop for fixed `k0` contains the unordered pair `(k1,k2)`, because all compatibility properties are D4-invariant. This occurrence satisfies both acceptance conditions.

### Uniqueness

Any accepted occurrence has sorted tuple equal to the unique value `K(T)`. The strict minimum condition forces its distinguished cap to be `k0`. The fixed-cap generator emits the unordered pair `(k1,k2)` once. Hence no second accepted occurrence exists.

Thus the rule retains exactly one occurrence from every `D4 x S3` orbit of valid outer cap triples.

## 5. Information retained and discarded

Retained:

- all three size-21 cap masks;
- the 58-point residual complement;
- the fixed-representative position;
- exact ordering/canonical convention.

Discarded:

- only other choices of distinguished size-21 colour;
- other D4 orientations;
- permutations of the three equal size-21 colour labels.

No geometric or completion constraint is discarded.

## 6. Preservation of completion feasibility

D4 maps grid lines to grid lines and preserves cap sizes, disjointness, colour quotas, and the no-three-collinear condition. Permuting the three size-21 colour labels has no effect on the residual completion problem. Therefore all discarded occurrences have the same P4/P5 completion status as the retained occurrence.

## 7. SAT reconstruction

A retained TSV record stores `cap1`, `cap2`, `cap3`, and `residual`. If the exact residual solver returns three residual colour masks, the six masks give a complete 11x11 colouring. The existing reconstruction utility and independent 287,980-triple verifier remain mandatory. An omitted orientation is reconstructed by applying the inverse D4 transform and the corresponding colour permutation.

## 8. UNSAT coverage

An exact UNSAT decision for the retained residual excludes every outer triple in its orbit. Complete global UNSAT would require:

- the audited full canonical outer ledger;
- one terminal exact decision for every retained residual record after any separately audited residual deduplication;
- no UNKNOWN, timeout, missing, or duplicate ledger positions;
- independently checkable residual evidence and all used dependency certificates.

The present work completes and audits the outer reduction, but does not execute every retained residual decision. P4 and P5 therefore remain unresolved.

## 9. Independent audits

The delivered audits check:

- exact coverage of first-cap positions `0..127490` across nine count shards;
- agreement of original occurrence totals with the supplied outer ledger;
- `canonical <= compatible_minfixed <= compatible_nonextendible` per position;
- exact pair-count arithmetic;
- exactly one accepted current-cover occurrence for each tested concrete cap triple;
- cap sizes, disjointness, singleton rows/columns, all 628 maximal-line bounds, residual complement, and canonical key for generated records.

The full exact count and resulting factor are inserted in the final report and status file after the nine-shard audit.

## 10. Completed full count

The nine production count shards covered every representative position exactly once. The independent ledger audit returned:

- original compatible nonextendible occurrences: `1,633,664,146`;
- canonical triple records: `544,481,464`;
- exact reduction factor: `3.000403602352935`;
- valid nonextendible first-cap positions: `125,690`;
- skipped extendible positions: `1,801`, all with zero generated counts.

For every position the audit checked

`0 <= canonical <= compatible_minfixed <= compatible_nonextendible`

and checked `pair_tests_gt = C(candidates_gt,2)`. The original occurrence sum agrees exactly with the frozen nine-shard outer ledger.

## 11. Solver exactness after the reduction

The retained hybrid solver changes only the branch-variable score. Its state, line bounds, cardinality propagation, leaf definition, binary P4/P5 solvers and witness fields are inherited unchanged from the rebuilt audited solver. Both branches are explored at every branch. Therefore it cannot remove a completion or create one.

Two complete 57,755-case comparisons were run:

- the frozen `fixed57755` family;
- a deterministic systematic sample of 57,755 unique residuals from all 248,664 unique residuals generated by the eight complete canonical representative positions.

In both comparisons, residual sets and every P4/P5 terminal status matched the rebuilt baseline exactly. All 115,510 cases were UNSAT.

## 12. Streaming production and reconstruction

`hybrid30_stream.cpp` processes one generator record at a time and emits `cap1`, `cap2`, `cap3`, `rep_position`, the residual, terminal status, counters and any residual witnesses. Thus no all-residual in-memory set is required. A SAT result retains all six colour masks needed by the existing independent full-colouring verifier. A FIFO end-to-end smoke on representative position 89741 processed all 11 canonical records with generator and solver exit status zero and preserved provenance in every record.

## 13. Build and implementation checks

- GCC 14 and Clang 17 produced identical canonical count fields on 120 stratified positions.
- GCC 14 and Clang 17 produced identical residuals, terminal statuses, SAT flags and deterministic counters for hybrid30 on `varied1200`.
- AddressSanitizer and UndefinedBehaviorSanitizer found no issue on hybrid solver, canonical counter and provenance generator smoke sets.
- The slow reference counter and production counter agreed on all 120 stratified positions.

These checks supplement, but do not replace, the mathematical exactly-one theorem.
