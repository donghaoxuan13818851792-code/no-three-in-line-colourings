# Release artifacts

Large frozen catalogues and production bundles may be attached to GitHub Releases or archived externally.

Every external artifact used by a proof claim must also appear in `manifests/artifact_manifest.tsv` with an immutable SHA-256 hash.

The [6 October 2026 P6/Q10 handoff prerelease](https://github.com/donghaoxuan13818851792-code/no-three-in-line-colourings/releases/tag/g11-handoff-20261006)
stores the exact received P6 ZIP, the Q10 ZIP as 63 ordered byte-preserving
chunks, and the compressed Q10 file index. See the
[intake report](../docs/handoff_intake_20261006.md) for verification scope
and remaining gaps. The Q10 [retrieval helper](../g11/Q/evidence/Q10/scripts/fetch_archive.py)
checks every chunk and the complete archive while writing a single ZIP.
