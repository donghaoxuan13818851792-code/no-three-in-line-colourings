# R artifact inventory

This file records the large R-branch artifacts currently staged for archival. The filenames below are archival/reconstructed names used by this repository; the original upload UI added parenthesised copy indices to some split-part filenames.

## Certificate package 0.1.0

Reconstructed archive:

- archival filename: `grid11_six_colour_two_size22_certificate_0.1.0.zip`
- bytes: `856451184`
- SHA-256: `f257f471ce104a80cc130682fdbe4cca2858d321bccf2e76573d44a9cd6d2198`
- archive integrity test: PASS (`unzip -t`)

Staging parts received:

| part | bytes | SHA-256 |
|---|---:|---|
| part 00 | 500000000 | `66a1411cb710969a3ce90e2c83fb9de6d5c38f8add844d259db185748a48aecd` |
| part 01 | 356451184 | `7bad5c9da55b91cd7710c1a3fe88fe88bdddff472ad00e2c942c1d1cf38a3506` |

The package identifies itself internally as `grid11_six_colour_two_size22_certificate_0.1.0`.

## Packaging refresh 0.1.1

Reconstructed archive:

- archival filename: `grid11_six_colour_two_size22_certificate_0.1.1.tar.zst`
- bytes: `594591562`
- SHA-256: `e5bc7cb32befb06fedb64803aeead269f232665069721e872ca6ec8e20adab0e`
- zstd integrity test: PASS

Staging parts received:

| part | bytes | SHA-256 |
|---|---:|---|
| part 00 | 104857600 | `f1c712248e40cdee9ebbec6b209eaee1e6fcd400c5312c7060e5a80295486eea` |
| part 01 | 104857600 | `8050a7e1c686731b11f3cc9c801b4a1c4930c0ce2487a0a6927784628fc53dcc` |
| part 02 | 104857600 | `392d1850b73e09df82fa7f83e35196cde076427e6e27a50cc6146412f75c7d09` |
| part 03 | 104857600 | `8fc0c3640f3df2b7295382fc82701da6b6828d184e2408c426f58e23b3951316` |
| part 04 | 104857600 | `a2df6bbfea8c6a8760e1c4e921222a81db1ab39b2c14e02b48c1af900949acdc` |
| part 05 | 70079162 | `c3720fa28dde46fc8a4ba4f58c6d19fbea87ae5e48816bcbd30dea443739ee0c` |

The 0.1.1 documentation states that this refresh changes packaging documentation and read-only wrapper scripts only; no research source, CNF, solver report, proof-verification report, certificate log, or mathematical data file was modified.

## Full proof-body archive

The certificate package cross-references the complete proof-body archive:

- filename: `grid11_six_colour_two_size22_proofs_0.1.0.tar.zst`
- bytes: `45687997349`
- SHA-256: `0087af20d68402c18728e56bc209e508b5565e9522c0b4185afaf2faf43f994f`
- content: 1,309 compressed DRAT proof bodies

This 45.7 GB archive has not yet been imported to a stable public archival location from this repository. Until that happens, the R branch remains conservatively `AWAITING_ARTIFACT_IMPORT` in `STATUS.md`.
