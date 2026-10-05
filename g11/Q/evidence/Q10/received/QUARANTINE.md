# Quarantine and historical boundary

The authoritative evidence chain is limited to the frozen inputs, pair-proof
bundle, production runners, fixed-anchor terminal records, and auditors called
by `verify_handoff.py`.

`quarantined/` contains the first rep76 partial-reuse audit that sampled only
one mask per shard and its superseding/corrected notes.  It is retained solely
to document the discovered defect.  It is not input to any proof, ledger,
certificate, completion count, or global claim.

The original cloud core archive includes additional historical pilots and
development work because it is preserved byte-for-byte for provenance.  It is
not part of the curated active tree and must not be used to strengthen a Q10
claim.  The explicit negative-result and claim-boundary notes in
`provenance/Q10_CLOUD_META_20260803/Q10_RECOVERY/FINAL_REPORT_DRAFT.md` remain
applicable.
