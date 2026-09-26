# Direct exact Q1--Q4 cap packing

Source:

```text
q1234_cap_packing.cpp
SHA-256 2227dba3f45b344abd38e445b9636ecaa6f30258ae68f9c7e992029c990e2fa7
```

The program fixes each of the 89 \(D_4\)-representative size-22 caps,
chooses three pairwise-compatible size-21 caps in increasing numeric-mask
order, and splits the forced 36-point complement into two caps of size at
most 21.  Their only unordered size pairs are

```text
21+15  20+16  19+17  18+18
```

so this is one exact search for Q1, Q2, Q3, and Q4.  Q1 contains four
size-21 caps; choosing any three duplicates it but does not omit it.
The residual Boolean search fixes its least point to the first colour,
removing the two-colour interchange.

Syntax-only validation (performed without launching the search):

```sh
c++ -std=c++20 -O2 -Wall -Wextra -pedantic -fsyntax-only \
  work/sat_agent/q1234_cap_packing.cpp
```

It succeeds with only an inherited unused-parameter warning from the
frozen P1 source.  A later build and six-way run can use:

```sh
c++ -std=c++20 -O3 -DNDEBUG \
  work/sat_agent/q1234_cap_packing.cpp \
  -o work/sat_agent/q1234_cap_packing

work/sat_agent/q1234_cap_packing --shard 0 6
# repeat shard indices 1,...,5
```

The six shards cover fixed-cap indices congruent to their shard index
modulo six, hence respectively 15, 15, 15, 15, 15, and 14 of the 89
representatives.  Exit 10 prints and fully checks a colouring.  Exit 20
prints `UNSAT_Q1234_SHARD` with exact prefix/residual node totals.  A
complete impossibility certificate requires all six exit-20 records,
their executable/source/input hashes, and an independent rebuild/replay;
a timeout or partial log is not a proof.

Frozen transitive inputs:

```text
p1_cap_packing.cpp      5c43c81a5b4a830c9a18c4eaf7197d9b8a4d8eefc7881f8960fbf4057a6127e0
caps22_d4.hex           234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40
caps21_r0_diag.hex      c4ba6b9aa11f4b9b7d1f7c2cd74eada8b727c40851c57e25a553142c4e12df3e
caps21_r1_diag.hex      62d025e2de26afe788057cc1a4525302d8a56c1be8ae4baf3d6d129f115b3895
caps21_r2_diag.hex      14f89035771e3428d0d6465d02ebea8430fb101cd0d6e3c972a8e98062d180e5
caps21_r3_diag.hex      92f7ea6aec073e2b335e089a56634f08ba34d1dab18e6b3c3935b70c2a157b42
caps21_r4_diag.hex      b1df4d6c48aeaad56d674b688e9398d05ef529409a9f4502fac212a7f4f78060
caps21_r5_diag.hex      47d59957a0f5f3d83298041cf4d8a3f99c5f5dc5211524c42e74235ea2561f9e
```

Independent read-only audit:

```text
work/independent_agent/q1234_cap_packing_audit.md
SHA-256 a34698d0e11ca2fcbc5aa40e4ff8c1d239dc380804649fb92caa39a984d7f3fd
```

That audit found no coverage, D4, equal-colour, compatibility-cache,
line-capacity, propagation, branching, or cardinality defect.  Runtime is
not yet measured; first run one fixed-cap smoke branch after the occupied
CPU batch finishes.
