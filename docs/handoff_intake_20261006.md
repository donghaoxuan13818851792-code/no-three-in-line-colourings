# Research handoff intake — 6 October 2026

Matthew Lewis supplied P6 and Q10 ZIP links in the Gmail thread
“Remaining P6 files for the repository”, dated 5 October 2026 at 15:30:45
and 15:39:11 UTC. These are newly received archives, not the older same-name
local packages. Original downloads are archived byte-for-byte in the
[g11-handoff-20261006 release](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/tag/g11-handoff-20261006).
Their exact digests, sizes and validation limits are in the branch audit files.
Private login material and share-link tokens are excluded from this intake.

## P6 requested materials

| Requested evidence | Received and checked | Remaining gap |
|---|---|---|
| Final run ledger | 10,787 terminal fixed-A decisions and pair records | Global final ledger |
| Work-item/shard completion | Exact input IDs and 169 completed chunks | Global canonical-pair scheduler/coverage mapping |
| Final UNSAT evidence | Saved logs exit 20; fresh backend replay 10,787/10,787 | Complete candidate enumeration and independent global correctness |
| Exact source/input hashes | Sources, Linux binaries, input, pairgrids, candidates and outputs bind | Source revision and original compiler environment |
| Slurm commands/scripts | Full-run and 64-case Slurm scripts and executed driver arguments | Exact original submission commands |
| Job logs | Successful full-run stdout/empty stderr; failed launch/rerun logs | Comprehensive global job history |
| Crashes/timeouts/reruns/UNKNOWN | Failed launch 24427405 and successful rerun 24427919 retained | Explicit run-wide accounting beyond this branch |
| Final validation | New evidence auditor and fresh backend replay pass | Supplied verifier rejects stale manifest; independent completeness pending |
| Archive and SHA-256 | Original ZIP public release asset; server digest matches local bytes | No archive gap for this received P6 package |

P6 therefore remains **INCOMPLETE globally**. Read
[the P6 audit](../g11/P/evidence/P6/AUDIT.md) before citing the branch result.

## Q10

The new primary chains cover all 89 representatives, with 257,125 catalogue
shards and 4,675 new terminal join shards checked. The exact original ZIP is
archived as 63 ordered byte-preserving chunks with complete and per-part SHA-256.
The supplied manifest stage rejects 533,182 unmanifested additions; all
23,594 old entries match. Failed catalogue launches and the rep1 resource
wrapper error are preserved alongside the complete final records.

Q10 is **INDEPENDENT_VERIFICATION_PENDING**, with remaining independent
correctness, refreshed manifest/status and provenance gaps explained in
[the Q10 audit](../g11/Q/evidence/Q10/AUDIT.md). This closes the missing-primary
execution gap, not the final theorem gate.

## Storage and evidence handling

The original archives are release assets rather than ordinary Git blobs.
P6 was extracted once for its integrity audit and full supplied-list backend
replay. Q10 is read directly from its ZIP to avoid a large expanded copy.
Temporary files created for this intake can be removed after the archive and
repository records are confirmed. Earlier user-owned material is preserved.

All 67 release assets now match their expected byte sizes and server SHA-256
digests, including all 63 Q10 chunks. The source ZIP and local ordered chunk
reassembly had already matched the complete Q10 archive hash. The task-created
Q10 raw download and uploaded chunks were removed after their corresponding
checks. See the [completed upload record](../g11/Q/evidence/Q10/UPLOAD_STATUS.md)
and [remote asset verification](../g11/Q/evidence/Q10/audits/remote_asset_verification.json).
