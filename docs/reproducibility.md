# Reproducibility policy

## Frozen artifacts

Every production artifact referenced by a theorem should be immutable and identified by:

- filename;
- byte size;
- SHA-256 hash;
- producing program/version;
- command line;
- input hashes;
- platform/compiler details where relevant.

## Large data

Large catalogues and production bundles should normally be stored outside ordinary Git history.

Preferred pattern:

1. archive the artifact in a GitHub Release, Zenodo record, or other immutable store;
2. record the URL/DOI and SHA-256 in `manifests/artifact_manifest.tsv`;
3. keep small validators and reconstruction scripts in Git.

## Independent checking

Whenever practical, a final branch should have a checker that is structurally simpler than the producing solver and does not merely trust recorded terminal status fields.
