# Local verification campaign — 6 October 2026

## Scope and resource policy

The authorized campaign runs on the existing Apple M4 Mac (10 physical CPU
cores, 24 GiB RAM), using at most ten workers within a computational phase.
Phases run sequentially. It retains at least 5 GiB free disk and limits the
campaign's resident memory to 14 GiB. Original research packages are read-only.
The initial attempt was stopped by the disk reserve before any P123 part
completed. Its records are preserved separately and do not count as UNSAT.
The restarted campaign began at 10:25 UTC.

The full P6 and P7 production searches and the unavailable 45.7 GB R proof
archive are outside this campaign. No new SAT solver searches are scheduled.

## Queued work and preliminary costs

| Phase | Work | CPU hours, preliminary | Mac wall time, preliminary |
|---|---|---:|---:|
| P123 | unchanged independent verifier; all 127,491 anchors and all resulting residuals | 2.5–4 | 25–40 minutes |
| Old packages and small certificates | Q7/Q8/Q9 terminal, prefix and Boolean audits; available P45 scope/record audits; G9/G10/G12 matrices; small G11 graph/profile checks; seed/prime arithmetic; G10 existing formal proof; G9 existing 598-class validity/canonicalisation | 0.05–0.3 | 5–25 minutes |
| Q10 catalogue membership | all 89 existing catalogues, 75,666,410 masks, fresh build of the separately authored geometric auditor | 0.05–0.15 | 3–15 minutes, excluding download |
| Existing Q10 sector certificates | 88 DRAT checks, followed by one stateful rep1 IDRUP check | 0.8–1.5 | 35–80 minutes |

Budget: approximately **4–7 CPU hours and 1.5–3 hours on this Mac**, including
allowance for setup and ordinary transfer delays. These are estimates, not
termination bounds. Transfer time is not CPU time. Parallel phases cannot be
estimated by simply dividing a single-core time by ten: the M4 has cores of
different performance, and the IDRUP check is stateful.

P123 calibration at 577.63 seconds: at least 53,000 of 127,491 anchors
completed (41.57%), about 1.226 CPU hours consumed; projected 2.948 CPU hours
and 23.16 minutes total elapsed, before uncertainty allowance. Active progress
is rounded down to 100-anchor reporting intervals.

Q10 calibration used the **entire** existing rep53 catalogue, 289,590 masks:
geometry/capacity/classification checks passed, with 0.53 user seconds,
0.01 system seconds and 0.86 elapsed seconds. Scaling this membership audit
does not estimate the cost of regenerating catalogues or searching joins.

Completed P123 measurement: **2.70674 CPU hours and 20.92 minutes elapsed**,
all 60 parts and all 708,638 residual instances checked. Q7/Q8/Q9 terminal,
prefix and Boolean/profile checks, the small-certificate checks, G9 observed
598-class audit and G10 route2 formal proof/CNF audit also pass. Q10 download
and its subsequent membership/proof replays remain in progress.

## Evidence produced

- P123 uses sixty disjoint residue classes of representative index modulo 60.
  Grouping them modulo six permits comparison with each historical primary
  shard. Actual exit 20, expected anchor counts, zero SAT, residual shapes,
  residual counts, and all corresponding prefix counters must agree.
  Every part retains its original output, progress log, exit code, command,
  stream and hashes. No six-shard output or missing historical status is forged.
- Q7/Q8/Q9 historical command strings are compared against their original
  paths. `run_relocated_audit.py` changes filesystem resolution only, preserves
  the unchanged audit source hash, and maps reads to the deposited package.
- P45 audits are explicitly restricted to their documented fixed branch and
  compression experiments. Their own status files say the global P4/P5 result
  is unresolved; a successful artifact audit does not close the global proof.
- The upper-bound matrices are checked by determinant triples and normalized
  line equations. Both methods must produce the same collinear triples, no
  monochromatic collinear triple, and the manuscript's canonical text hashes.
- Small G11 checks independently confirm catalogue membership, D4 orbit
  closure, triangle-freeness, capacity-feasible pair counts, pair orbits and
  all 44 deficit profiles. They do not establish catalogue-generation
  completeness or check the missing R proof bodies.
- The seed audit checks 2,240 nonzero determinants, 1,024 reflection
  memberships and the eight positions without a same-class reflection choice.
  It reconstructs the 29-prime list and checks exact primality/admissibility
  of the displayed prime. It does not establish that the prime is smallest
  or replace mathematical review of the infinite construction. The C6 check
  sums the four displayed subtotals only; its complete 33-profile ledger has
  not yet been mapped to an artifact.
- The G10 route2 audit rechecks the existing proof with freshly built DRAT,
  regenerates and audits the five-colour CNF, and compares it byte-for-byte
  against the certified input. It does not invoke a SAT solver.
- The G9 audit checks the existing 598 observed inequivalent classes, all
  monochromatic-class triples, D4/colour canonicalisation, stabilizers, orbit
  sizes and hashes. It does not claim exhaustive C(9)=743.
- Q10 reads the exact archived ZIP without unpacking its 10 GB contents.
  Only one catalogue per worker is temporarily extracted and hash-bound, then
  deleted. Membership audits do not establish catalogue completeness or the
  global UNSAT decision.
- Q10 proof replay checks existing proofs with freshly built checkers, without
  invoking CaDiCaL. Its claim remains the at-least-two-extendible-size-20
  sector; it does not certify arbitrary-cap global Q10.

## Running and reviewing

The detached coordinator is `scripts/run_local_verification.py`. It writes
`state.json`, per-part records, `p123_audit.json`, and follow-up outputs to the
chosen run directory. `followups.json` supplies explicit local package paths
and commands, executed sequentially after P123 passes. Bytecode writes are
disabled to avoid modifying received packages.

`COMPUTATION_FINISHED` means the queued programs have returned. It is not a
mathematical completion claim: each result, failure, scope and dependency
still needs review before updating `STATUS.md` and the artifact manifests.
