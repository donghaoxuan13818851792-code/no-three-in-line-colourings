# R frozen data inventory

The four small frozen data files needed for the reviewer-facing R0/R1 reconstruction are now committed directly in this directory. Their repository blobs were checked against the corresponding files extracted from the frozen 0.1.1 package; all four are byte-identical.

| Repository file | Original package path | Lines | Bytes | SHA-256 | State |
|---|---|---:|---:|---|---|
| `caps22_diag_independent.hex` | `caps/size22_caps/caps22_diag_independent.hex` | 676 | 21632 | `2aed51282c1fb96e623e7c47c7e182ff2d914f80a414808898f526ac832f83bc` | committed; byte-identical |
| `caps22_d4.hex` | `caps/size22_caps/caps22_d4.hex` | 89 | 2848 | `234108ff1e1922c5385eb7714c799a677d10913396427ec17e7aa8e411621e40` | committed; byte-identical |
| `cap_pairs22_capacity_d4_swap.hex` | `caps/capacity_filter/cap_pairs22_capacity_d4_swap.hex` | 119 | 7616 | `5f6b9033e3eef7b0505be70b6e2eb98cc879984f2456ab0836567014a87f9c3c` | committed; byte-identical |
| `pairs22_filtered_ordered_d4.hex` | `symmetry/orbit_data/pairs22_filtered_ordered_d4.hex` | 119 | 7616 | `0aa91ddff6dc2fa6bf860919b0f779cec86674a88099fc1f44c32a2e4685b2ae` | committed; byte-identical |

The two 119-line pair tables arise from different frozen routes but represent the same canonical orbit universe. The coverage auditor checks equality of their canonical orbit sets. During the 2026-08-26 fresh reconstruction, regeneration of the capacity-filtered table from the 676-cap input produced a byte-identical file with SHA-256 `5f6b9033e3eef7b0505be70b6e2eb98cc879984f2456ab0836567014a87f9c3c`.

The 676-cap catalogue itself can now be reconstructed from the committed frozen generator; see `../REPRODUCE.md` and `../source/generator/rebuild_size22_catalogue.py`.
