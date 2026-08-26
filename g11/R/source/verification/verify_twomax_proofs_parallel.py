#!/usr/bin/env python3
"""Resumably verify all 1,309 two-max DRAT proofs through LRAT.

Before checking any certificate, this program invokes the independent leaf
auditor with ``--require-all``.  That preflight reconstructs all 11 profiles,
119 pair orbits, and every leaf CNF body and unit assignment.

Each proof then passes two independent stages:

1. drat-trim validates the (possibly binary) DRAT and emits a temporary LRAT;
2. lrat-check validates that LRAT against the original CNF.

The temporary LRAT is hashed and always deleted.  Per-leaf JSON reports are
written atomically and make the run resumable.  If an uncompressed ``.drat``
named by the solver report is absent, a sibling ``.drat.zst`` is streamed
through zstd into a temporary proof and checked against the solver report's
uncompressed byte count and SHA-256.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_LEAVES = ROOT / "work/sat_agent/twomax_leaf_proofs"
DEFAULT_OUTPUT = ROOT / "work/independent_agent/twomax_leaf_proof_checks"
DEFAULT_AUDITOR = HERE / "audit_twomax_leaf_batch.py"
DRAT_SOURCE = HERE / "drat-trim-src"
DEFAULT_DRAT = DRAT_SOURCE / "drat-trim"
DEFAULT_LRAT = DRAT_SOURCE / "lrat-check"
SCHEMA = "grid11-twomax-drat-lrat-parallel-v1"
EXPECTED_LEAVES = 1309


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def resolve_root(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def tool_identity(path: Path):
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def source_commit():
    result = subprocess.run(
        ["git", "-C", str(DRAT_SOURCE), "rev-parse", "HEAD"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def logged_run(arguments, log: Path):
    temporary = log.with_suffix(log.suffix + ".tmp")
    started = time.monotonic()
    with temporary.open("wb") as sink:
        process = subprocess.run(
            [str(item) for item in arguments],
            stdout=sink,
            stderr=subprocess.STDOUT,
        )
    os.replace(temporary, log)
    return process.returncode, time.monotonic() - started


def preflight(
    leaves: Path,
    output: Path,
    auditor: Path,
):
    log = output / "preflight-leaf-audit.log"
    temporary = log.with_suffix(log.suffix + ".tmp")
    arguments = [
        sys.executable,
        str(auditor),
        "--leaves",
        str(leaves),
        "--require-all",
        "--defer-proof-content",
        "--allow-zstd",
    ]
    with temporary.open("wb") as sink:
        process = subprocess.run(
            arguments,
            cwd=ROOT,
            stdout=sink,
            stderr=subprocess.STDOUT,
        )
    os.replace(temporary, log)
    text = log.read_text(encoding="utf-8", errors="replace")
    if process.returncode != 0 or "VERIFIED" not in text:
        raise RuntimeError(
            f"exhaustive leaf preflight failed; see {log}")

    summary_path = leaves / "summary.json"
    if not summary_path.is_file():
        raise RuntimeError(f"missing solver-batch summary: {summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if not (
        summary.get("jobs") == EXPECTED_LEAVES
        and summary.get("completed") == EXPECTED_LEAVES
        and summary.get("failures") == 0
    ):
        raise RuntimeError(f"incomplete/bad solver summary: {summary}")

    source_reports = sorted(
        path for path in leaves.glob("*.json")
        if path.name != "summary.json"
    )
    if len(source_reports) != EXPECTED_LEAVES:
        raise RuntimeError(
            f"expected {EXPECTED_LEAVES} source reports, "
            f"found {len(source_reports)}")
    if len({path.stem for path in source_reports}) != EXPECTED_LEAVES:
        raise RuntimeError("duplicate source-report stems")
    return {
        "log": str(log),
        "log_sha256": sha256(log),
        "auditor": str(auditor),
        "auditor_sha256": sha256(auditor),
        "summary": str(summary_path),
        "summary_sha256": sha256(summary_path),
        "source_reports": source_reports,
    }


def materialize_proof(
    declared: Path,
    temporary: Path,
    zstd: Path | None,
):
    """Return local proof path, storage metadata, and whether it is temporary."""
    if declared.is_file():
        return declared, {
            "kind": "uncompressed",
            "path": str(declared),
            "bytes": declared.stat().st_size,
            "sha256": sha256(declared),
        }, False

    compressed = Path(str(declared) + ".zst")
    if not compressed.is_file():
        raise FileNotFoundError(
            f"missing proof and compressed sibling: {declared}")
    if zstd is None:
        raise RuntimeError(
            f"zstd executable unavailable for {compressed}")
    temporary.unlink(missing_ok=True)
    started = time.monotonic()
    with temporary.open("wb") as sink:
        process = subprocess.run(
            [str(zstd), "-dc", str(compressed)],
            stdout=sink,
            stderr=subprocess.PIPE,
        )
    if process.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"zstd failed for {compressed}: "
            f"{process.stderr.decode(errors='replace')}")
    return temporary, {
        "kind": "zstd",
        "path": str(compressed),
        "bytes": compressed.stat().st_size,
        "sha256": sha256(compressed),
        "decompression_seconds": time.monotonic() - started,
    }, True


def resumable_report_matches(
    old,
    source_report_sha,
    cnf_sha,
    proof_sha,
    drat_identity,
    lrat_identity,
):
    if not (
        old.get("schema") == SCHEMA
        and old.get("verified") is True
        and old.get("source_report_sha256") == source_report_sha
        and old.get("cnf_sha256") == cnf_sha
        and old.get("proof_sha256") == proof_sha
        and old.get("drat_trim", {}).get("sha256")
        == drat_identity["sha256"]
        and old.get("lrat_check", {}).get("sha256")
        == lrat_identity["sha256"]
        and old.get("lrat_removed_after_verification") is True
    ):
        return False
    for prefix in ("drat", "lrat"):
        log = Path(old[f"{prefix}_log"])
        if not log.is_file() or sha256(log) != old[f"{prefix}_log_sha256"]:
            return False
    return True


def check_one(
    source_report_path: Path,
    output: Path,
    temporary_directory: Path,
    drat: Path,
    lrat_checker: Path,
    drat_identity,
    lrat_identity,
    zstd: Path | None,
):
    name = source_report_path.stem
    report_path = output / "reports" / f"{name}.json"
    cnf_hash = proof_hash = source_report_hash = None
    temporary_proof = temporary_directory / f"{name}.decompressed.drat"
    lrat = temporary_directory / f"{name}.lrat"
    temporary_is_proof = False
    started = time.monotonic()
    try:
        source_report_hash = sha256(source_report_path)
        source = json.loads(
            source_report_path.read_text(encoding="utf-8"))
        if not (
            source.get("name") == name
            and source.get("exit_code") == 20
            and source.get("stdout") == "s UNSATISFIABLE\n"
        ):
            raise ValueError("source solver report is not an UNSAT result")

        cnf = resolve_root(source["cnf"])
        if not cnf.is_file():
            raise FileNotFoundError(f"missing CNF: {cnf}")
        cnf_hash = sha256(cnf)
        if not (
            cnf.stat().st_size == source["cnf_bytes"]
            and cnf_hash == source["cnf_sha256"]
        ):
            raise ValueError("CNF hash/size differs from solver report")
        header = cnf.open(encoding="ascii").readline().split()
        if header[:2] != ["p", "cnf"] or len(header) != 4:
            raise ValueError("bad DIMACS header")
        variables, clauses = map(int, header[2:])

        declared_proof = resolve_root(source["proof"])
        proof, storage, temporary_is_proof = materialize_proof(
            declared_proof, temporary_proof, zstd)
        proof_hash = sha256(proof)
        if not (
            proof.stat().st_size == source["proof_bytes"]
            and proof_hash == source["proof_sha256"]
        ):
            raise ValueError(
                "uncompressed proof hash/size differs from solver report")

        if report_path.exists():
            old = json.loads(report_path.read_text(encoding="utf-8"))
            if resumable_report_matches(
                old,
                source_report_hash,
                cnf_hash,
                proof_hash,
                drat_identity,
                lrat_identity,
            ):
                old["resumed_without_rechecking"] = True
                return old

        lrat.unlink(missing_ok=True)
        drat_log = output / "logs" / f"{name}.drat-check.log"
        lrat_log = output / "logs" / f"{name}.lrat-check.log"
        drat_code, drat_seconds = logged_run(
            [drat, cnf, proof, "-L", lrat],
            drat_log,
        )
        drat_text = drat_log.read_text(
            encoding="utf-8", errors="replace")
        if drat_code != 0 or "s VERIFIED" not in drat_text:
            raise RuntimeError(
                f"DRAT verification failed; see {drat_log}")
        if not lrat.is_file() or lrat.stat().st_size == 0:
            raise RuntimeError("drat-trim emitted no LRAT")

        lrat_bytes = lrat.stat().st_size
        lrat_hash = sha256(lrat)
        lrat_code, lrat_seconds = logged_run(
            [lrat_checker, cnf, lrat],
            lrat_log,
        )
        lrat_text = lrat_log.read_text(
            encoding="utf-8", errors="replace")
        if lrat_code != 0 or "VERIFIED" not in lrat_text.upper():
            raise RuntimeError(
                f"LRAT verification failed; see {lrat_log}")

        report = {
            "schema": SCHEMA,
            "name": name,
            "verified": True,
            "source_report": str(source_report_path),
            "source_report_sha256": source_report_hash,
            "cnf": str(cnf),
            "cnf_bytes": cnf.stat().st_size,
            "cnf_sha256": cnf_hash,
            "variables": variables,
            "clauses": clauses,
            "proof": str(declared_proof),
            "proof_bytes": proof.stat().st_size,
            "proof_sha256": proof_hash,
            "proof_storage": storage,
            "drat_trim": drat_identity,
            "drat_trim_exit": drat_code,
            "drat_trim_seconds": drat_seconds,
            "drat_log": str(drat_log),
            "drat_log_sha256": sha256(drat_log),
            "lrat_check": lrat_identity,
            "lrat_check_exit": lrat_code,
            "lrat_check_seconds": lrat_seconds,
            "lrat_log": str(lrat_log),
            "lrat_log_sha256": sha256(lrat_log),
            "lrat_bytes": lrat_bytes,
            "lrat_sha256": lrat_hash,
            "lrat_removed_after_verification": True,
            "elapsed_seconds": time.monotonic() - started,
        }
        atomic_json(report_path, report)
        return report
    except Exception as error:
        failure = {
            "schema": SCHEMA,
            "name": name,
            "verified": False,
            "source_report": str(source_report_path),
            "source_report_sha256": source_report_hash,
            "cnf_sha256": cnf_hash,
            "proof_sha256": proof_hash,
            "error": f"{type(error).__name__}: {error}",
            "elapsed_seconds": time.monotonic() - started,
        }
        atomic_json(report_path, failure)
        return failure
    finally:
        lrat.unlink(missing_ok=True)
        if temporary_is_proof:
            temporary_proof.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--leaves", type=Path, default=DEFAULT_LEAVES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--auditor", type=Path, default=DEFAULT_AUDITOR)
    parser.add_argument("--drat-trim", type=Path, default=DEFAULT_DRAT)
    parser.add_argument("--lrat-check", type=Path, default=DEFAULT_LRAT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--zstd",
        type=Path,
        default=Path(shutil.which("zstd")) if shutil.which("zstd") else None,
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")

    leaves = args.leaves.resolve()
    output = args.output.resolve()
    auditor = args.auditor.resolve()
    drat = args.drat_trim.resolve()
    lrat_checker = args.lrat_check.resolve()
    zstd = args.zstd.resolve() if args.zstd else None
    for executable in (auditor, drat, lrat_checker):
        if not executable.is_file():
            parser.error(f"missing file: {executable}")
    for executable in (drat, lrat_checker):
        if not os.access(executable, os.X_OK):
            parser.error(f"not executable: {executable}")
    if zstd is not None and not os.access(zstd, os.X_OK):
        parser.error(f"not executable: {zstd}")

    output.mkdir(parents=True, exist_ok=True)
    (output / "reports").mkdir(exist_ok=True)
    (output / "logs").mkdir(exist_ok=True)
    temporary_directory = output / "temporary"
    temporary_directory.mkdir(exist_ok=True)

    preflight_result = preflight(leaves, output, auditor)
    source_reports = preflight_result.pop("source_reports")
    drat_identity = tool_identity(drat)
    lrat_identity = tool_identity(lrat_checker)
    batch = {
        "schema": SCHEMA,
        "verified": False,
        "started_unix": time.time(),
        "workers": args.workers,
        "driver": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "preflight": preflight_result,
        "drat_trim": drat_identity,
        "lrat_check": lrat_identity,
        "drat_trim_source_commit": source_commit(),
        "zstd": tool_identity(zstd) if zstd else None,
        "expected_entries": EXPECTED_LEAVES,
        "entries": {},
    }
    aggregate = output / "batch-proof-report.json"
    atomic_json(aggregate, batch)

    completed = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                check_one,
                source_report,
                output,
                temporary_directory,
                drat,
                lrat_checker,
                drat_identity,
                lrat_identity,
                zstd,
            ): source_report
            for source_report in source_reports
        }
        for future in as_completed(futures):
            result = future.result()
            completed += 1
            if not result.get("verified"):
                failed += 1
            batch["entries"][result["name"]] = result
            batch["completed"] = completed
            batch["failures"] = failed
            atomic_json(aggregate, batch)
            if (
                completed % 10 == 0
                or not result.get("verified")
                or completed == EXPECTED_LEAVES
            ):
                print(
                    f"completed={completed}/{EXPECTED_LEAVES} "
                    f"failures={failed} last={result['name']} "
                    f"verified={result.get('verified')}",
                    flush=True,
                )

    batch["finished_unix"] = time.time()
    batch["verified"] = (
        completed == EXPECTED_LEAVES
        and failed == 0
        and len(batch["entries"]) == EXPECTED_LEAVES
        and all(
            entry.get("verified")
            for entry in batch["entries"].values()
        )
    )
    atomic_json(aggregate, batch)
    print(
        f"BATCH {'VERIFIED' if batch['verified'] else 'FAILED'} "
        f"{completed-failed}/{EXPECTED_LEAVES}; report={aggregate}")
    raise SystemExit(0 if batch["verified"] else 1)


if __name__ == "__main__":
    main()
