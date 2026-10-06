# Local verification results — 6 October 2026

All locally available checks scheduled for this campaign have completed and
been reviewed. P1–P3 passes full fresh independent replay; the other results
below have their stated finite or certificate scope. This does not complete
the G11 lower bound or every claim in the manuscript.

## Results and scope

| Evidence | Reviewed result | Scope retained |
|---|---|---|
| P1–P3 | PASS: 60 actual parts, 127,491 anchors, 708,638 residuals, all exits 20, zero SAT, matching primary counters | full frozen P1–P3 independent replay |
| Q7, Q8/Q9 | PASS: exact original package manifests, unchanged strict terminal audits, fresh prefix/Boolean/profile checks | existing full execution records audited; terminal searches not rerun |
| Q10 catalogues | PASS: all 89 catalogues and 75,666,410 masks | geometric membership, stored counters and exact archive/anchor bindings; not enumeration completeness |
| Q10 existing proof sector | PASS: 88 DRAT certificates and full strict rep1 IDRUP, plus source/transcript binding for 2,200 UNSAT queries | at least two extendible size-20 classes; not arbitrary-cap global Q10 |
| G10 route2 | PASS: both upper witnesses and fresh native DRAT; independently reconstructed CNF is byte-identical | exact route2 five-colour exclusion |
| G9 catalogue | PASS: validity, canonicalisation, stabilizers, orbits and hashes of all 598 observed classes | observed classes only; not exhaustive C(9)=743 |
| Small paper certificates | PASS: G9/G10/G12 matrices, small G11 graph/profile arithmetic, seed/reflection, finite prime conditions, displayed C6 subtotals | finite predicates only; full classifications and human mathematical arguments remain separate |
| Available P4/P5 packages | package/scope audits PASS; global status INCOMPLETE | delivered status explicitly says unresolved; pilot/reduction records are not global terminal decisions |

The two first Q7/Q89 path-adapter failures are preserved. Corrected `retry1`
audits pass with the received source unchanged. They are resolved operational
failures, not evidence of a mathematical counterexample.

## Actual costs on this Mac

The machine is an Apple M4 with 10 physical cores and 24 GiB RAM. Independent
work within a phase used up to ten workers; major phases were sequential.
The final IDRUP proof checker is stateful and uses one core.

| Timed work | Recorded CPU hours | Elapsed time |
|---|---:|---:|
| P1–P3 fresh independent workers | 2.70674 | 20.92 minutes |
| Other timed follow-up programs, including full geometry wrapper and transfer | 0.06433 | per-program records in costs.json |
| Q10 ordinary DRAT workers | 0.15607 | included in 15.13-minute sector wrapper |
| Q10 strict rep1 IDRUP | 0.20094 | 12.31 minutes |
| **Recorded subtotal** | **3.12807** | **47.96 minutes to final proof report** |

The successful campaign restarted at **10:25:04 UTC** and produced the final
proof report at **11:13:02 UTC** (21:25 to 22:13 in Melbourne). This wall time
includes the approximately 9.53-minute Q10 transfer. Final review, packaging
and upload took additional time. CPU hours are the sum of user and system
time, not elapsed time multiplied by ten.

The subtotal does not include untimed compilation, hashing, rep1 interaction
binding, final packaging/review, or CPU consumed by the initial interrupted
P123 attempt. That attempt completed zero parts and has no reliable CPU
accounting. The full outer geometry timing already includes its workers; its
0.03551-hour native sum is not added twice. The outer Q10 proof timer was
interrupted, so only its completed native-checker timings are counted.

See `verification/local_campaign/20261006/costs.json` for exact timers and
`final_review.json` for the reviewed operational record.

## Resource interruption and final reconciliation

At 11:12:58 UTC, free disk fell to 4,708,323,328 bytes, below the 5 GiB reserve.
The coordinator recorded `STOPPED_WITH_ERROR`. Its then-running version
stopped the immediate time wrapper but did not stop the native checker child.
That child completed four seconds later, retaining `s VERIFIED`, native exit
0, all 2,200 conclusions, and zero UNKNOWN results. The wrapper also produced
its final PASS report and completion marker. All native logs, input hashes,
ledger matches and source/transcript bindings were reviewed directly.

The original coordinator state and traceback are preserved. No outer proof
exit file or clean coordinator finish was invented. Future coordinator code
terminates whole process groups on resource protection. A checker failure or
partial result would not count as UNSAT.

Only task-created temporary copies were removed: the verified Q10 ZIP
reassembly and temporary Q89/G10 extractions, totaling 3,703,107,101 bytes.
Original research materials remain read-only. After cleanup, disk free space
was **10.12 GiB**; the exact cleanup record is retained.

The frozen IDRUP checker embeds an August build string even after fresh
compilation. Its actual October compiler/source/binary hashes are retained
separately. The same unchanged source assumes Linux RSS units; on Darwin its
displayed 55,824 MB means 54.52 MiB. Raw output is preserved without correction.

## Evidence and reproduction

The [local verification release](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/tag/local-verification-20261006)
contains the original Q7, Q89 and G10 route2 packages, the complete P123 replay,
and `local_verification_final_20261006.tar.gz`. The final receipt archive
preserves genuine proof logs, input/archive bindings, original ordinary ledger,
fresh native binaries, unchanged checker sources, replay driver, cost records
and coordinator/interruption records. It contains no duplicate large proof
bodies; those remain in the exact original Q10 release archive. Every final
receipt-archive member is hash-checked before upload.

The large Q10 body is in the
[original handoff release](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/tag/g11-handoff-20261006).
All 187 checked source/input/ledger files are matched to its complete public
file index. `g11/Q/evidence/Q10/AUDIT.md` gives selective extraction/replay
instructions and the original supplied-manifest rejection. The received
manifest was not modified to manufacture a pass.

## Remaining paper work

The G11 theorem still requires full R1 proof bodies and replay, complete global
P4/P5, P6 and P7 terminal evidence, and independent global Q10 enumeration/join
correctness. Q10 stays `INDEPENDENT_VERIFICATION_PENDING`; P4/P5, P6 and P7
stay `INCOMPLETE`; R remains `AWAITING_ARTIFACT_IMPORT`.

The broader paper also needs the unmapped complete count/classification
artifacts for C5/C6/C7/C8/C9, the G12 lower bound, larger-grid packing records,
and review of the infinite construction and smallest-prime claim. Exact
claim boundaries are in `PAPER_CLAIMS.md`. This campaign did not start global
searches whose required material is absent.

The [post-campaign review](local_verification_review_20261006.md) records the
follow-up evidence checks and process cleanup correction. The
[material request checklist](supplier_materials_needed_20261006.md) identifies
what can be checked locally after receipt of further frozen artifacts.
