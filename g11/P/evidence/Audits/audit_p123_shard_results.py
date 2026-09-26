#!/usr/bin/env python3
"""Audit complete P123 shard outputs and compare their shared prefix to P1."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SAT = ROOT / "work/sat_agent"
EXPECTED_FIRST = (21249, 21249, 21249, 21248, 21248, 21248)

P123 = re.compile(
    r"UNSAT123_SHARD (?P<shard>\d+) 6 first_caps (?P<first>\d+)"
    r" tested2 (?P<t2>\d+) passed2 (?P<p2>\d+)"
    r" tested3 (?P<t3>\d+) passed3 (?P<p3>\d+)"
    r" tested4 (?P<t4>\d+) passed4 (?P<p4>\d+)"
    r" residual_instances (?P<instances>\d+)"
    r" residual_nodes (?P<nodes>\d+)"
    r" residual_conflicts (?P<conflicts>\d+)"
    r" residual_sat (?P<sat>\d+)\n?"
)
P1 = re.compile(
    r"UNSAT_SHARD (?P<shard>\d+) 6 first_caps (?P<first>\d+)"
    r" tested2 (?P<t2>\d+) passed2 (?P<p2>\d+)"
    r" tested3 (?P<t3>\d+) passed3 (?P<p3>\d+)"
    r" tested4 (?P<t4>\d+) passed4 (?P<p4>\d+)"
    r" tested5 \d+ passed5 \d+\n?"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path, pattern: re.Pattern[str]) -> dict[str, int]:
    text = path.read_text(encoding="ascii")
    assert "SOLUTION" not in text
    match = pattern.fullmatch(text)
    assert match, (path, text)
    return {key: int(value) for key, value in match.groupdict().items()}


def main() -> None:
    total_first = 0
    total_instances = 0
    totals = {key: 0 for key in ("t2", "p2", "t3", "p3", "t4", "p4")}
    for shard in range(6):
      status = SAT / f"p123_full_shard{shard}.status"
      output = SAT / f"p123_full_shard{shard}.out"
      log = SAT / f"p123_full_shard{shard}.log"
      assert status.read_text(encoding="ascii").strip() == "20"
      result = parse(output, P123)
      p1_result = parse(SAT / f"p1_full_shard{shard}.out", P1)
      assert result["shard"] == shard
      assert result["first"] == EXPECTED_FIRST[shard]
      assert result["instances"] == result["p4"]
      assert result["sat"] == 0
      for key in ("shard", "first", "t2", "p2", "t3", "p3", "t4", "p4"):
          assert result[key] == p1_result[key], (
              shard, key, result[key], p1_result[key])
      log_text = log.read_text(encoding="ascii")
      assert "d4_representatives 127491" in log_text
      assert "ERROR" not in log_text
      total_first += result["first"]
      total_instances += result["instances"]
      for key in totals:
          totals[key] += result[key]
      print(
          f"shard {shard}",
          *(f"{key}={result[key]}" for key in (
              "first", "t2", "p2", "t3", "p3", "t4", "p4",
              "instances", "nodes", "conflicts", "sat")),
      )
      print(
          "hashes",
          f"out={digest(output)}",
          f"log={digest(log)}",
          f"status={digest(status)}",
      )
    assert total_first == 127491
    assert total_instances == totals["p4"] == 708638
    assert totals == {
        "t2": 1331602820,
        "p2": 514209820,
        "t3": 1512534032571,
        "p3": 1505452322,
        "t4": 9327491112,
        "p4": 708638,
    }
    print(
        "P123_SHARDS_VERIFIED",
        f"first_caps={total_first}",
        f"residual_instances={total_instances}",
        *(f"{key}={value}" for key, value in totals.items()),
    )


if __name__ == "__main__":
    main()
