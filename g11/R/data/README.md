# R frozen data inventory

The exact audit source imported under `../source/` was taken from the frozen 0.1.1 package. The corresponding small data files have been independently hashed and reconstructed from that package, but their bytes are not yet all committed in this directory.

| Original package path | Lines | Bytes | SHA-256 | Repository state |
|---|---:|---:|---|---|
| `caps/size22_caps/caps22_diag_independent.hex` | 676 | 21632 | `2aed51282c1fb96e623e7c47c7e182ff2d914f80a414808898f526ac832f83bc` | pending byte import |
| `caps/size22_caps/caps22_d4.hex` | 89 | 2848 | `234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40` | pending byte import |
| `caps/capacity_filter/cap_pairs22_capacity_d4_swap.hex` | 119 | 7616 | `5f6b9033e3eef7b0505be70b6e2eb98cc879984f2456ab0836567014a87f9c3c` | pending byte import |
| `symmetry/orbit_data/pairs22_filtered_ordered_d4.hex` | 119 | 7616 | `0aa91ddff6dc2fa6bf860919b0f779cec86674a88099fc1f44c32a2e4685b2ae` | pending byte import |

The two 119-line tables are independently required by the coverage auditor and were checked to represent the same canonical orbit universe. During the 2026-08-26 reconstruction, regeneration of the capacity-filtered table from the 676-cap input produced a byte-identical file with SHA-256 `5f6b9033e3eef7b0505be70b6e2eb98cc879984f2456ab0836567014a87f9c3c`.

Until these files have either been committed here or exposed through a stable immutable archive URI, reproduction commands in `../REPRODUCE.md` should be run against the frozen 0.1.1 package.
