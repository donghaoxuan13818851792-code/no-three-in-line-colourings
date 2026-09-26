# P1–P3 independent verification — 26 September 2026

The independent verifier completed all six representative-index shards. Every shard exited with code 20, produced its full terminal record and residual stream, and reported `residual_sat=0`. The existing auditor cross-checked the independent counts against the primary outputs and validated each residual mask's width and 37-bit size.

The run covered 127,491 first caps and 708,638 residual instances. There are 707,115 distinct 121-bit mask encodings and 1,523 repeat occurrences across streams; repeated encodings remain separate residual instances.

The repository import audit verifies every recorded output, log, status, residual stream, and command digest, then runs the existing independent-results auditor using a temporary mirror for its historical relative paths. It passes. The run manifest and imported bytes are preserved under [`P123Independent/run_20260926T032326Z/`](../P123Independent/run_20260926T032326Z/).
