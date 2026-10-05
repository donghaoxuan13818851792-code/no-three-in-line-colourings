# Archive upload status

The original Q10 ZIP is split into 13 ordered parts, each at most 250,000,000
bytes. All local part hashes and the reconstructed complete SHA-256 match.
The parts are currently being uploaded serially; archive upload must not be
considered complete until every server digest matches `archive.json`.
The original supplied-list audits and native join checks are complete.
