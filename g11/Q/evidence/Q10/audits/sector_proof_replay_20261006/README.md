# Existing Q10 sector: fresh native proof receipts

`report.json` is the actual final replay output, not a rewritten coordinator
state. All 88 ordinary native logs and the strict rep1 IDRUP log are retained
byte-for-byte. `rep1_binding.json` checks source/transcript correspondence for
all 2,200 UNSAT interactions. `ordinary_drat_ledger.json` is the original input
ledger; `input_archive_bindings.json` matches every checked input and checker
source to the complete immutable public Q10 file index.

This result is limited to the at-least-two-extendible-size-20 sector. It does
not independently prove arbitrary-cap global Q10 UNSAT.

The outer time wrapper was interrupted by disk protection. Its exit status is
not recorded; native checker completion and its exact exit/verification log
are reviewed separately. `verification/local_campaign/20261006/` preserves
the original stop state and final reconciliation. The final receipt archive
also contains the freshly compiled native binaries and unchanged source files.

The raw report's `updated_epoch` marks entry to its rep1 phase; final completion
is identified by the retained native log and original report write timestamp
in the final review. The frozen build header and Darwin RSS-unit issue are
explained in `../../AUDIT.md` and the final campaign report.
