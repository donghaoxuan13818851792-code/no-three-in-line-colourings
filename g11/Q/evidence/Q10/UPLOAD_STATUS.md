# Archive upload status

**COMPLETE — 63/63 chunks uploaded and server-digest verified.**

The exact original Q10 ZIP is stored in 63 ordered chunks, each at most
50,000,000 bytes. Their total is 3,140,960,671 bytes. The downloaded source
and local ordered reassembly both matched SHA-256
`1ea37d8321c44a018efc37694e21e2d8dacc4870224a540ea14b5609cbc2000e`.
Every chunk now has a matching GitHub server digest and byte size.
The P6 ZIP, compressed Q10 file index and both metadata sidecars are also
uploaded and server-digest checked: 67/67 release assets match.
The check record is `audits/remote_asset_verification.json`.

Use `scripts/fetch_archive.py` with an empty destination to stream the
chunks into one ZIP. It checks each part and the complete archive while
retaining at least 5 GB free; it creates no separate chunk copies.
A small synthetic reconstruction check also passed, including overwrite
refusal and rejection of a corrupted chunk with `.partial` retained.
The complete remote ZIP was not downloaded a second time during intake.

The task-created Q10 raw download and uploaded local chunks were removed
only after source/reassembly hash checks and server-digest confirmation,
respectively. Earlier user-owned material was preserved.

Archive upload completion does not change the mathematical evidence status:
Q10 remains **INDEPENDENT_VERIFICATION_PENDING**. See `AUDIT.md`.
