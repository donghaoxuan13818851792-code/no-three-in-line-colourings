#!/usr/bin/env python3
"""Audit the imported Q10 source selection and 89 representative results."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re


Q_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Q_ROOT / "evidence/Q10"
PACKAGE = EVIDENCE / "source_records/Q10_HPC_HANDOFF_PACKAGE"
EXPECTED_SOURCE_BYTES = 10_399_498_240
EXPECTED_SOURCE_SHA256 = "7e20e19f7428ca8a084c1a561b5ed97e69bbb9647e8098d1024a8114b4028eaa"
UNEXHAUSTED_OLD_SNAPSHOT = {17, 53, 76, 88}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        value = json.load(source)
    assert isinstance(value, dict), path
    return value


def catalogue_record(rep: int) -> tuple[int, str, dict]:
    if rep in (17, 76):
        metadata = read_json(PACKAGE / f"work/math_agent/nonextendible_structure/rep{rep}_result_meta.json")
        catalogue = metadata["catalogue"]
        count, digest = int(catalogue["masks"]), catalogue["sha256"]
    elif rep == 53:
        metadata = read_json(PACKAGE / "work/math_agent/nonextendible_structure/rep53_result_audit.json")
        enumeration = metadata["enumeration"]
        count, digest = int(enumeration["candidate_count"]), enumeration["catalogue_sha256"]
    elif rep == 1:
        metadata = read_json(PACKAGE / "work/solver_agent/cap20_rep1_runner_v1/result.json")
        count, digest = int(metadata["catalogue_masks"]), metadata["catalogue_sha256"]
    elif rep == 88:
        metadata = read_json(PACKAGE / "work/solver_agent/cap20_rep88_runner_v1/result.json")
        count, digest = int(metadata["catalogue_masks"]), metadata["catalogue_sha256"]
    else:
        metadata = read_json(PACKAGE / f"runs/rep{rep}_catalogue/result.json")
        count, digest = int(metadata["catalogue_masks"]), metadata["catalogue_sha256"]
    return count, digest, metadata


def audit_terminal_json(rep: int, path: Path) -> tuple[int, str]:
    result = read_json(path)
    assert result["status"] == "PASS", (rep, path)
    assert result["mathematical_status"] == "UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE", (rep, path)
    assert result["exit_code_histogram"] == {"20": 55}, (rep, path)
    assert result["aggregate"]["final_pool_candidates"] == 0, (rep, path)
    ledger = result["shard_ledger"]
    assert len(ledger) == 55, (rep, path)
    assert all(row["status"] == "COMPLETE_NO_WITNESS" and row["exit_code"] == 20 for row in ledger)
    assert all(row["witness_sha256"] is None for row in ledger)
    return int(result["candidate_count"]), result["catalogue_sha256"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    source_rows = list(csv.DictReader((EVIDENCE / "source_members.tsv").open(), delimiter="\t"))
    assert len(source_rows) == 814
    for row in source_rows:
        path = EVIDENCE / "source_records" / row["member"]
        assert path.is_file(), path
        assert path.stat().st_size == int(row["bytes"]), path
        assert sha256(path) == row["sha256"], path
    archive = list(csv.DictReader((EVIDENCE / "source_archive.tsv").open(), delimiter="\t"))[0]
    assert int(archive["bytes"]) == EXPECTED_SOURCE_BYTES
    assert archive["sha256"] == EXPECTED_SOURCE_SHA256
    assert int(archive["selected_package_members"]) == len(source_rows)
    assert archive["selection_manifest_sha256"] == sha256(EVIDENCE / "source_members.tsv")

    summary_rows = []
    for line in (PACKAGE / "runs/join-summary.tsv").read_text(encoding="utf-8").splitlines():
        rep, status, mathematical_status, count, seconds = line.split("\t")
        summary_rows.append((int(rep), status, mathematical_status, int(count), seconds))
    assert len(summary_rows) == 85
    summary_by_rep = {row[0]: row for row in summary_rows}
    expected_new = set(range(89)) - UNEXHAUSTED_OLD_SNAPSHOT
    assert set(summary_by_rep) == expected_new
    assert all(row[1] == "PASS" and row[2] == "UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE" for row in summary_rows)
    assert sum(row[3] for row in summary_rows) == 74_011_954

    new_reports = {
        int(re.fullmatch(r"rep(\d{2})\.audit\.json", path.name).group(1)): path
        for path in (EVIDENCE / "audits/raw_new_85/reports").glob("rep*.audit.json")
    }
    old_reports = {
        int(re.fullmatch(r"rep(\d{2})\.audit\.json", path.name).group(1)): path
        for path in (EVIDENCE / "audits/raw_prior_17_76_88/reports").glob("rep*.audit.json")
    }
    assert set(new_reports) == expected_new
    assert set(old_reports) == {17, 76, 88}

    final_rows: list[tuple[int, int, str, str]] = []
    for rep in sorted(expected_new | {17, 76, 88}):
        report_path = new_reports[rep] if rep in new_reports else old_reports[rep]
        count, digest = audit_terminal_json(rep, report_path)
        archived_count, archived_digest, catalog_meta = catalogue_record(rep)
        assert (count, digest) == (archived_count, archived_digest), rep
        if rep in summary_by_rep:
            _, status, mathematical_status, summary_count, _ = summary_by_rep[rep]
            assert status == "PASS" and mathematical_status == "UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE"
            assert summary_count == count
            origin = "fresh raw 55-shard audit; join-summary.tsv"
        else:
            origin = "prior raw 55-shard audit; exact catalogue/result metadata"
        if rep in (17, 76):
            assert catalog_meta["catalogue"]["enumeration"]["status"] == "COMPLETE"
            assert catalog_meta["catalogue"]["enumeration"]["complete_shards"] == 3025
            assert catalog_meta["catalogue"]["enumeration"]["missing_keys"] == 0
        else:
            assert catalog_meta["status"] == "COMPLETE_AUDITED"
            assert catalog_meta["records"] == 3025
        final_rows.append((rep, count, digest, origin))

    # Rep 53 uses its complete native 3,025-shard catalogue audit and one
    # complete terminal join log, rather than the later 55-shard join format.
    rep53_source = EVIDENCE / "audits/rep53/rep53_result_audit.source.json"
    rep53_rerun = EVIDENCE / "audits/rep53/rep53-chain-audit-rerun.json"
    rep53_original = read_json(rep53_source)
    rep53_current = read_json(rep53_rerun)
    assert rep53_source.read_bytes() == rep53_rerun.read_bytes()
    assert rep53_original == rep53_current
    assert rep53_current["status"] == "PASS"
    assert rep53_current["representative_index"] == 53
    assert rep53_current["enumeration"]["shards"] == 3025
    assert rep53_current["enumeration"]["all_complete_exit_zero"] is True
    assert rep53_current["join"]["status"] == "COMPLETE_NO_WITNESS"
    assert rep53_current["join"]["final_pool_candidates"] == 0
    assert (int(rep53_current["enumeration"]["candidate_count"]),
            rep53_current["enumeration"]["catalogue_sha256"]) == catalogue_record(53)[:2]
    assert (EVIDENCE / "audits/raw_prior_17_76_88/rep53-shard-audit.json").is_file()
    assert (EVIDENCE / "audits/raw_prior_17_76_88/rep53-geometry-audit.json").is_file()

    supplemental = list(csv.DictReader((EVIDENCE / "rep53_supplement/supplement_manifest.tsv").open(), delimiter="\t"))
    assert len(supplemental) == 2
    for row in supplemental:
        path = EVIDENCE / "rep53_supplement" / row["package_member"]
        assert path.stat().st_size == int(row["bytes"])
        assert sha256(path) == row["sha256"]
    expected_supplement = {
        "work/root/rep53_capset_join.log": "19c4b2392ccbd7631a31a8f23504fc19e0444e4d9d0a8da6c96c2aed934d2111",
        "work/solver_agent/cap20_rep53_all_masks_v4.audit.log": "29d4e230f0b0ae7c8fb27c8997ff33c004dff13b3fffb556cdbb07be6d4ea457",
    }
    assert {row["package_member"]: row["sha256"] for row in supplemental} == expected_supplement

    old_status = [line.split("\t") for line in (PACKAGE / "runs/join-status.tsv").read_text().splitlines()]
    assert len(old_status) == 85 and all(row[1] == "MISSING" for row in old_status)

    assert len(final_rows) == 88
    assert {row[0] for row in final_rows} == set(range(89)) - {53}
    final_rows.append((53, int(rep53_current["enumeration"]["candidate_count"]),
                       rep53_current["enumeration"]["catalogue_sha256"],
                       "fresh exact-source-chain audit; source JSON independently rerun"))
    final_rows.sort()
    assert len(final_rows) == 89 and {row[0] for row in final_rows} == set(range(89))
    assert sum(row[1] for row in final_rows) == 75_666_410

    table = EVIDENCE / "audits/final_audit.tsv"
    table.parent.mkdir(parents=True, exist_ok=True)
    with table.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(["representative", "catalogue_masks", "catalogue_sha256", "terminal_evidence"])
        writer.writerows(final_rows)
    result = {
        "status": "PASS",
        "representatives_audited": 89,
        "catalogue_masks_across_89_representatives": sum(row[1] for row in final_rows),
        "fresh_85_join_summary_candidate_masks": sum(row[3] for row in summary_rows),
        "new_raw_55_shard_join_audits": len(new_reports),
        "prior_raw_55_shard_join_audits": len(old_reports),
        "rep53_native_chain_audit": "PASS",
        "each_55_shard_join": "55/55 exit 20 COMPLETE_NO_WITNESS, no witness, zero final pool candidates",
        "rep53_join": "complete native terminal log, COMPLETE_NO_WITNESS, zero final pool candidates",
        "source_archive_sha256": EXPECTED_SOURCE_SHA256,
        "source_archive_bytes": EXPECTED_SOURCE_BYTES,
        "historical_join_status": "85 MISSING rows preserved; later 2026-09-10 summary and raw audits supersede this earlier snapshot",
        "supplemental_rep53_records": "PASS",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n")
    print("Q10_FINAL_AUDIT PASS audited=89/89 fresh_85_join_candidates=74011954 catalogue_masks=75666410 fail_cases=0")
    print(rendered)


if __name__ == "__main__":
    main()
