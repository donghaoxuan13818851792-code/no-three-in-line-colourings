#!/usr/bin/env python3
"""Auditable, resumable orchestration for all 55x55 cap20 shards.

Production mode always dispatches exactly the 3,025 singleton-row/column-pair
keys.  A completed shard is reusable only when its atomic JSON record belongs
to the immutable run identity, says COMPLETE/exit 0, and its mask file still
matches the recorded hash, line count, syntax, and unique shard key.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

SIDE = 11
POINTS = SIDE * SIDE
PAIRS = [(a, b) for a in range(SIDE) for b in range(a + 1, SIDE)]
HEX_RE = re.compile(r"[0-9a-f]{31}")
ENUM_RE = re.compile(
    r"^COMPLETE count (\d+) least_eligible (\d+) "
    r"extendible (\d+) nonextendible (\d+) nodes (\d+) leaves (\d+) "
    r"tight_lines (\d+) column_rejects (\d+) line_rejects (\d+) "
    r"self_secant_rejects (\d+) seconds ([0-9.eE+-]+)$"
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def parse_anchor(text: str) -> int:
    if not HEX_RE.fullmatch(text.lower()):
        raise ValueError("anchor must be exactly 31 hexadecimal digits")
    anchor = int(text, 16)
    if anchor.bit_count() != 22:
        raise ValueError("anchor must contain exactly 22 points")
    return anchor


def key_pair(key_id: int) -> tuple[int, int]:
    if not 0 <= key_id < 3025:
        raise ValueError(f"key outside 0..3024: {key_id}")
    return divmod(key_id, 55)


def mask_pair_ids(mask: int) -> tuple[int, int]:
    row_degree = [sum((mask >> (SIDE*r+c)) & 1 for c in range(SIDE))
                  for r in range(SIDE)]
    col_degree = [sum((mask >> (SIDE*r+c)) & 1 for r in range(SIDE))
                  for c in range(SIDE)]
    if sorted(row_degree) != [1, 1] + [2] * 9:
        raise ValueError("bad singleton-row degree pattern")
    if sorted(col_degree) != [1, 1] + [2] * 9:
        raise ValueError("bad singleton-column degree pattern")
    rows = tuple(i for i, degree in enumerate(row_degree) if degree == 1)
    cols = tuple(i for i, degree in enumerate(col_degree) if degree == 1)
    return PAIRS.index(rows), PAIRS.index(cols)


def parse_enum_stdout(stdout: str) -> dict[str, int | float]:
    lines = stdout.strip().splitlines()
    if len(lines) != 1:
        raise ValueError("enumerator stdout is not exactly one nonempty line")
    match = ENUM_RE.match(lines[0])
    if not match:
        raise ValueError("enumerator did not report the required COMPLETE v4 schema")
    names = (
        "count", "least_eligible", "extendible", "nonextendible", "nodes",
        "leaves", "tight_lines", "column_rejects", "line_rejects",
        "self_secant_rejects",
    )
    parsed: dict[str, int | float] = {
        name: int(value) for name, value in zip(names, match.groups()[:-1])
    }
    parsed["seconds"] = float(match.group(11))
    if parsed["count"] != parsed["leaves"]:
        raise ValueError("COMPLETE count/leaves mismatch")
    if parsed["count"] != parsed["extendible"] + parsed["nonextendible"]:
        raise ValueError("COMPLETE classification mismatch")
    return parsed


def validate_mask_file(path: Path, expected_count: int,
                       key: tuple[int, int]) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("mask file is missing")
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise ValueError("mask file is not ASCII") from error
    words = text.splitlines()
    if len(words) != expected_count:
        raise ValueError(f"mask line count {len(words)} != {expected_count}")
    for line_number, word in enumerate(words, 1):
        if not HEX_RE.fullmatch(word):
            raise ValueError(f"malformed mask at line {line_number}")
        mask = int(word, 16)
        if mask.bit_count() != 20:
            raise ValueError(f"non-size-20 mask at line {line_number}")
        if mask_pair_ids(mask) != key:
            raise ValueError(f"mask belongs to wrong shard at line {line_number}")
    return {
        "bytes": len(raw),
        "lines": len(words),
        "sha256": sha256_bytes(raw),
    }


def record_path(run_dir: Path, key: tuple[int, int]) -> Path:
    return run_dir / "records" / f"{key[0]:02d}_{key[1]:02d}.json"


def mask_path(run_dir: Path, key: tuple[int, int]) -> Path:
    return run_dir / "shards" / f"{key[0]:02d}_{key[1]:02d}.hex"


def reusable_record(run_dir: Path, key: tuple[int, int],
                    identity_sha256: str) -> tuple[bool, str, dict[str, Any] | None]:
    path = record_path(run_dir, key)
    if not path.is_file():
        return False, "record missing", None
    try:
        record = json.loads(path.read_text())
        if record.get("run_identity_sha256") != identity_sha256:
            raise ValueError("identity hash mismatch")
        if record.get("row_pair") != key[0] or record.get("col_pair") != key[1]:
            raise ValueError("record key mismatch")
        if record.get("status") != "COMPLETE" or record.get("exit_code") != 0:
            raise ValueError("record is not COMPLETE/exit0")
        parsed = parse_enum_stdout(record["stdout"])
        if parsed != record.get("parsed"):
            raise ValueError("record parse mismatch")
        file_info = validate_mask_file(mask_path(run_dir, key), int(parsed["count"]), key)
        if file_info != record.get("mask_file"):
            raise ValueError("mask file hash/metadata mismatch")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        return False, str(error), None
    return True, "validated", record


def preserve_failed_attempt(run_dir: Path, key: tuple[int, int], command: list[str],
                            result: subprocess.CompletedProcess[str],
                            temporary_mask: Path, reason: str,
                            identity_sha256: str, elapsed: float) -> None:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    stem = f"{key[0]:02d}_{key[1]:02d}.{stamp}.{uuid.uuid4().hex}"
    attempt_dir = run_dir / "attempts"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    partial_name = None
    if temporary_mask.exists():
        partial = attempt_dir / f"{stem}.partial.hex"
        os.replace(temporary_mask, partial)
        partial_name = partial.name
    atomic_json(attempt_dir / f"{stem}.json", {
        "col_pair": key[1],
        "command": command,
        "elapsed_wall_seconds": elapsed,
        "exit_code": result.returncode,
        "partial_mask_file": partial_name,
        "reason": reason,
        "row_pair": key[0],
        "run_identity_sha256": identity_sha256,
        "stderr": result.stderr,
        "stdout": result.stdout,
        "timestamp_utc": utc_now(),
    })


def run_one(run_dir: Path, key: tuple[int, int], identity_sha256: str,
            generator: Path, anchor_text: str, caps: Path,
            time_limit: float) -> tuple[tuple[int, int], bool, str]:
    destination = mask_path(run_dir, key)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    command = [
        str(generator), "--anchor", anchor_text,
        "--row-pair", str(key[0]), "--col-pair", str(key[1]),
        "--time", str(time_limit), "--caps", str(caps),
        "--output-masks", str(temporary),
    ]
    started = utc_now()
    begin = time.monotonic()
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    elapsed = time.monotonic() - begin
    try:
        if result.returncode != 0:
            raise ValueError(f"enumerator exit {result.returncode}")
        parsed = parse_enum_stdout(result.stdout)
        file_info = validate_mask_file(temporary, int(parsed["count"]), key)
    except (OSError, ValueError) as error:
        preserve_failed_attempt(run_dir, key, command, result, temporary,
                                str(error), identity_sha256, elapsed)
        return key, False, str(error)

    os.replace(temporary, destination)
    record = {
        "col_pair": key[1],
        "command": command,
        "elapsed_wall_seconds": elapsed,
        "exit_code": 0,
        "finished_utc": utc_now(),
        "mask_file": file_info,
        "parsed": parsed,
        "row_pair": key[0],
        "run_identity_sha256": identity_sha256,
        "started_utc": started,
        "status": "COMPLETE",
        "stderr": result.stderr,
        "stdout": result.stdout.strip(),
    }
    atomic_json(record_path(run_dir, key), record)
    return key, True, "COMPLETE"


def deterministic_finalize(args: argparse.Namespace, run_dir: Path,
                           keys: list[tuple[int, int]], identity_sha256: str,
                           fixture_mode: bool) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for key in keys:
        valid, reason, record = reusable_record(run_dir, key, identity_sha256)
        if not valid or record is None:
            raise RuntimeError(f"final validation failed for {key}: {reason}")
        records.append(record)

    log_lines = [
        f"{record['row_pair']},{record['col_pair']},{record['stdout']},exit=0\n"
        for record in records
    ]
    log_path = run_dir / "shards.log"
    atomic_bytes(log_path, "".join(log_lines).encode())

    unsorted_path = run_dir / f".all_masks.{uuid.uuid4().hex}.unsorted"
    with unsorted_path.open("wb") as output:
        for key in keys:
            with mask_path(run_dir, key).open("rb") as source:
                while chunk := source.read(1 << 20):
                    output.write(chunk)
    sorted_temporary = run_dir / f".all_masks.{uuid.uuid4().hex}.sorted"
    environment = dict(os.environ)
    environment["LC_ALL"] = "C"
    sort_result = subprocess.run(
        ["sort", "-o", str(sorted_temporary), str(unsorted_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env=environment, check=False,
    )
    unsorted_path.unlink()
    if sort_result.returncode != 0:
        raise RuntimeError(f"sort failed: {sort_result.stderr}")
    catalogue_path = run_dir / "all_masks.hex"
    os.replace(sorted_temporary, catalogue_path)

    total = 0
    previous = ""
    with catalogue_path.open() as catalogue:
        for line_number, line in enumerate(catalogue, 1):
            word = line.rstrip("\n")
            if not HEX_RE.fullmatch(word):
                raise RuntimeError(f"malformed combined mask at line {line_number}")
            if previous and word <= previous:
                raise RuntimeError(f"combined catalogue duplicate/order failure at {line_number}")
            previous = word
            total += 1
    expected_total = sum(int(record["parsed"]["count"]) for record in records)
    if total != expected_total:
        raise RuntimeError(f"combined count {total} != record total {expected_total}")

    audit_result = subprocess.run(
        [str(args.auditor), "--anchor", args.anchor.lower(),
         "--catalogue", str(catalogue_path), "--caps", str(args.caps)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    audit_log = audit_result.stdout + audit_result.stderr
    atomic_bytes(run_dir / "catalogue.audit.log", audit_log.encode())
    if audit_result.returncode != 0 or not audit_result.stdout.startswith("AUDIT_OK "):
        raise RuntimeError("independent catalogue audit did not return AUDIT_OK")

    external: dict[str, Any] = {}
    if not fixture_mode:
        summary_temporary = run_dir / f".summary.{uuid.uuid4().hex}.json"
        summary_result = subprocess.run(
            [sys.executable, str(args.summarizer), str(log_path),
             "--json", str(summary_temporary)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if summary_result.returncode != 0:
            raise RuntimeError(f"summary failed: {summary_result.stderr}")
        os.replace(summary_temporary, run_dir / "summary.json")
        shard_audit_temporary = run_dir / f".shard_audit.{uuid.uuid4().hex}.json"
        shard_result = subprocess.run(
            [sys.executable, str(args.shard_auditor),
             "--shards", str(run_dir / "shards"), "--log", str(log_path),
             "--catalogue", str(catalogue_path), "--json", str(shard_audit_temporary)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if shard_result.returncode != 0:
            raise RuntimeError(f"shard audit failed: {shard_result.stderr}")
        os.replace(shard_audit_temporary, run_dir / "shard_audit.json")
        external = {
            "shard_audit_stdout": shard_result.stdout.strip(),
            "summary_stdout": summary_result.stdout.strip(),
        }

    result = {
        "audit": audit_result.stdout.strip(),
        "catalogue_masks": total,
        "catalogue_sha256": sha256_file(catalogue_path),
        "completed_utc": utc_now(),
        "fixture_mode": fixture_mode,
        "log_sha256": sha256_file(log_path),
        "records": len(records),
        "run_identity_sha256": identity_sha256,
        "schema": "q10-cap20-catalogue-run-result-v1",
        "status": "COMPLETE_AUDITED",
        "sum_enumerator_wall_seconds": sum(float(record["elapsed_wall_seconds"])
                                               for record in records),
        **external,
    }
    for stale_name in ("incomplete.json", "audit_failure.json"):
        stale = run_dir / stale_name
        if stale.exists():
            stale.unlink()
    atomic_json(run_dir / "result.json", result)
    return result


def resolve_file(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise ValueError(f"{label} is not a file: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--anchor", required=True)
    parser.add_argument("--generator", type=Path, required=True)
    parser.add_argument("--generator-source", type=Path)
    parser.add_argument("--caps", type=Path, required=True)
    parser.add_argument("--auditor", type=Path, required=True)
    parser.add_argument("--summarizer", type=Path)
    parser.add_argument("--shard-auditor", type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--time-per-shard", type=float, default=300.0)
    parser.add_argument("--fixture-keys", type=Path,
                        help="test-only key-id list; production omits this")
    args = parser.parse_args()

    try:
        parse_anchor(args.anchor)
        if args.jobs <= 0 or args.time_per_shard <= 0:
            raise ValueError("jobs and time-per-shard must be positive")
        generator = resolve_file(args.generator, "generator")
        caps = resolve_file(args.caps, "caps")
        auditor = resolve_file(args.auditor, "auditor")
        generator_source = (resolve_file(args.generator_source, "generator source")
                            if args.generator_source else None)
        fixture_mode = args.fixture_keys is not None
        if fixture_mode:
            fixture_path = resolve_file(args.fixture_keys, "fixture keys")
            ids = [int(line) for line in fixture_path.read_text().splitlines()]
            if not ids or len(ids) != len(set(ids)):
                raise ValueError("fixture keys must be nonempty and unique")
        else:
            ids = list(range(3025))
            if args.summarizer is None or args.shard_auditor is None:
                raise ValueError("production mode requires --summarizer and --shard-auditor")
            args.summarizer = resolve_file(args.summarizer, "summarizer")
            args.shard_auditor = resolve_file(args.shard_auditor, "shard auditor")
        keys = [key_pair(key_id) for key_id in sorted(ids)]
    except (OSError, ValueError) as error:
        parser.error(str(error))

    args.generator = generator
    args.caps = caps
    args.auditor = auditor
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "records").mkdir(exist_ok=True)
    (run_dir / "shards").mkdir(exist_ok=True)

    key_payload = "".join(f"{55*r+c}\n" for r, c in keys).encode()
    identity: dict[str, Any] = {
        "anchor_hex": args.anchor.lower(),
        "auditor": {"path": str(auditor), "sha256": sha256_file(auditor)},
        "caps": {"path": str(caps), "sha256": sha256_file(caps)},
        "expected_key_count": len(keys),
        "fixture_mode": fixture_mode,
        "generator": {"path": str(generator), "sha256": sha256_file(generator)},
        "generator_source": ({"path": str(generator_source),
                              "sha256": sha256_file(generator_source)}
                             if generator_source else None),
        "key_ids_sha256": sha256_bytes(key_payload),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "schema": "q10-cap20-catalogue-run-identity-v1",
        "time_per_shard": args.time_per_shard,
    }
    if not fixture_mode:
        identity["summarizer"] = {
            "path": str(args.summarizer), "sha256": sha256_file(args.summarizer)
        }
        identity["shard_auditor"] = {
            "path": str(args.shard_auditor), "sha256": sha256_file(args.shard_auditor)
        }
    identity_sha256 = sha256_bytes(canonical_bytes(identity))
    meta_path = run_dir / "run.meta.json"
    if meta_path.exists():
        try:
            old = json.loads(meta_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            print(f"ERROR unreadable run identity: {error}", file=sys.stderr)
            return 3
        if old.get("identity") != identity or old.get("identity_sha256") != identity_sha256:
            print("ERROR immutable run identity mismatch", file=sys.stderr)
            return 3
    else:
        atomic_json(meta_path, {
            "created_utc": utc_now(),
            "identity": identity,
            "identity_sha256": identity_sha256,
        })

    missing: list[tuple[int, int]] = []
    invalid: list[tuple[tuple[int, int], str]] = []
    for key in keys:
        valid, reason, _ = reusable_record(run_dir, key, identity_sha256)
        if not valid:
            missing.append(key)
            invalid.append((key, reason))
    print(json.dumps({
        "identity_sha256": identity_sha256,
        "invalid_or_missing": len(missing),
        "jobs": args.jobs,
        "reusable": len(keys) - len(missing),
        "total_keys": len(keys),
    }, sort_keys=True), flush=True)

    failures: list[tuple[tuple[int, int], str]] = []
    if missing:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [executor.submit(
                run_one, run_dir, key, identity_sha256, generator,
                args.anchor.lower(), caps, args.time_per_shard,
            ) for key in missing]
            for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
                key, ok, reason = future.result()
                if not ok:
                    failures.append((key, reason))
                if completed % 25 == 0 or completed == len(futures):
                    print(json.dumps({
                        "attempted": completed,
                        "failed": len(failures),
                        "remaining": len(futures) - completed,
                    }, sort_keys=True), flush=True)
    if failures:
        atomic_json(run_dir / "incomplete.json", {
            "failures": [{"row_pair": key[0], "col_pair": key[1], "reason": reason}
                         for key, reason in failures],
            "identity_sha256": identity_sha256,
            "status": "INCOMPLETE",
            "timestamp_utc": utc_now(),
        })
        print(f"INCOMPLETE {len(failures)} shard attempts failed", file=sys.stderr)
        return 2

    try:
        result = deterministic_finalize(args, run_dir, keys, identity_sha256, fixture_mode)
    except (OSError, RuntimeError, ValueError) as error:
        atomic_json(run_dir / "audit_failure.json", {
            "error": str(error),
            "identity_sha256": identity_sha256,
            "status": "AUDIT_FAILED",
            "timestamp_utc": utc_now(),
        })
        print(f"AUDIT_FAILED {error}", file=sys.stderr)
        return 4
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
