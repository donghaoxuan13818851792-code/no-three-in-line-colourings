#!/usr/bin/env python3
"""Audit the fixed-anchor evidence index without extending its claim boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


STANDARD_MANIFESTS = {
    17: "work/math_agent/nonextendible_structure/rep17_result_meta.json",
    76: "work/math_agent/nonextendible_structure/rep76_result_meta.json",
    88: "work/math_agent/nonextendible_structure/rep88_result_meta.json",
}

REP53_RESULT = "work/math_agent/nonextendible_structure/rep53_result_audit.json"
REP53_CATALOGUE = "work/solver_agent/cap20_rep53_all_masks_v4.hex"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object in {path}")
    return value


def catalogue_audit(path: Path, expected_count: int, expected_sha256: str) -> None:
    if sha256(path) != expected_sha256:
        raise AssertionError(f"catalogue hash mismatch: {path}")
    count = 0
    previous = -1
    with path.open() as source:
        for number, raw in enumerate(source, 1):
            token = raw.strip()
            if len(token) != 31:
                raise AssertionError(f"bad mask width at {path}:{number}")
            try:
                value = int(token, 16)
            except ValueError as error:
                raise AssertionError(f"bad mask at {path}:{number}") from error
            if value <= previous:
                raise AssertionError(f"catalogue is not strict-sorted at {path}:{number}")
            previous = value
            count += 1
    if count != expected_count:
        raise AssertionError(f"catalogue count mismatch: {path}: {count} != {expected_count}")


def audit_standard(root: Path, index: int, frozen_anchor: str) -> dict[str, object]:
    manifest_path = root / STANDARD_MANIFESTS[index]
    manifest = load_json(manifest_path)
    if manifest["representative_index_zero_based"] != index:
        raise AssertionError(f"wrong representative index in {manifest_path}")
    if manifest["anchor_hex"] != frozen_anchor:
        raise AssertionError(f"anchor does not match frozen representative {index}")
    if manifest["mathematical_status"] != f"REPRESENTATIVE_{index}_UNSAT":
        raise AssertionError(f"nonterminal fixed-anchor status in {manifest_path}")

    catalogue = manifest["catalogue"]
    catalogue_path = root / catalogue["path"]
    catalogue_audit(catalogue_path, catalogue["masks"], catalogue["sha256"])

    join = manifest["join"]
    audit_path = root / join["audit"]["path"]
    if sha256(audit_path) != join["audit"]["sha256"]:
        raise AssertionError(f"join-audit hash mismatch for representative {index}")
    audit = load_json(audit_path)
    if audit["status"] != "PASS" or audit["mathematical_status"] != "UNSAT_RELATIVE_TO_COMPLETE_CAP_CATALOGUE":
        raise AssertionError(f"join audit is not terminal UNSAT for representative {index}")
    if audit["anchor_hex"] != frozen_anchor or audit["catalogue_sha256"] != catalogue["sha256"]:
        raise AssertionError(f"join identity mismatch for representative {index}")
    if audit["candidate_count"] != catalogue["masks"]:
        raise AssertionError(f"join catalogue count mismatch for representative {index}")
    if audit["aggregate"] != join["aggregate"]:
        raise AssertionError(f"join aggregate mismatch for representative {index}")
    if audit["aggregate"]["roots_examined"] != catalogue["masks"]:
        raise AssertionError(f"join roots do not cover catalogue for representative {index}")
    if audit["aggregate"]["final_pool_candidates"] != 0:
        raise AssertionError(f"nonempty final pool for representative {index}")

    census = manifest.get("completion_matching_census")
    if census is not None and sha256(root / census["path"]) != census["sha256"]:
        raise AssertionError(f"completion-census hash mismatch for representative {index}")

    return {
        "representative_index_zero_based": index,
        "anchor_hex": frozen_anchor,
        "candidate_count": catalogue["masks"],
        "catalogue_sha256": catalogue["sha256"],
        "pair_candidates": join["aggregate"]["pair_candidates"],
        "triple_candidates": join["aggregate"]["triple_candidates"],
        "final_pool_candidates": join["aggregate"]["final_pool_candidates"],
        "fixed_anchor_status": "UNSAT",
        "manifest_path": STANDARD_MANIFESTS[index],
        "manifest_sha256": sha256(manifest_path),
        "join_audit_path": join["audit"]["path"],
        "join_audit_sha256": join["audit"]["sha256"],
    }


def audit_rep53(root: Path, frozen_anchor: str) -> dict[str, object]:
    result_path = root / REP53_RESULT
    result = load_json(result_path)
    if result["status"] != "PASS" or result["representative_index"] != 53:
        raise AssertionError("representative-53 result is not a passing terminal audit")
    if result["anchor_hex"] != frozen_anchor:
        raise AssertionError("representative-53 anchor does not match frozen table")
    enumeration = result["enumeration"]
    join = result["join"]
    catalogue_audit(
        root / REP53_CATALOGUE,
        enumeration["candidate_count"],
        enumeration["catalogue_sha256"],
    )
    if not enumeration["all_complete_exit_zero"] or enumeration["shards"] != 3025:
        raise AssertionError("representative-53 enumeration is not terminal")
    if join["status"] != "COMPLETE_NO_WITNESS":
        raise AssertionError("representative-53 join is not terminal")
    if join["roots_examined"] != enumeration["candidate_count"] or join["final_pool_candidates"] != 0:
        raise AssertionError("representative-53 join coverage mismatch")
    return {
        "representative_index_zero_based": 53,
        "anchor_hex": frozen_anchor,
        "candidate_count": enumeration["candidate_count"],
        "catalogue_sha256": enumeration["catalogue_sha256"],
        "pair_candidates": join["pair_candidates"],
        "triple_candidates": join["triple_candidates"],
        "final_pool_candidates": join["final_pool_candidates"],
        "fixed_anchor_status": "UNSAT",
        "manifest_path": REP53_RESULT,
        "manifest_sha256": sha256(result_path),
        "join_audit_path": REP53_RESULT,
        "join_audit_sha256": sha256(result_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    default_root = Path(__file__).resolve().parents[3]
    root = (args.root or default_root).resolve()
    reps_path = root / "work/package/Q10_ULTRA_RESEARCH_LEAN_20260802/data/caps22_d4.hex"
    representatives = [line.strip() for line in reps_path.read_text().splitlines() if line.strip()]
    if len(representatives) != 89 or len(set(representatives)) != 89:
        raise AssertionError("frozen representative table is not 89 unique masks")
    if any(len(mask) != 31 or int(mask, 16).bit_count() != 22 for mask in representatives):
        raise AssertionError("bad mask in frozen representative table")

    audited = [
        audit_standard(root, 17, representatives[17]),
        audit_rep53(root, representatives[53]),
        audit_standard(root, 76, representatives[76]),
        audit_standard(root, 88, representatives[88]),
    ]
    audited.sort(key=lambda row: row["representative_index_zero_based"])
    exhausted = [row["representative_index_zero_based"] for row in audited]
    result = {
        "status": "PASS",
        "mathematical_status": "INCOMPLETE",
        "claim_boundary": (
            "Only the listed frozen size-22 representatives are exhaustively UNSAT; "
            "the other representatives and hence global Q10 remain unresolved."
        ),
        "frozen_representative_table": str(reps_path.relative_to(root)),
        "frozen_representative_table_sha256": sha256(reps_path),
        "frozen_representative_count": len(representatives),
        "exhausted_representative_indices_zero_based": exhausted,
        "exhausted_representative_count": len(exhausted),
        "remaining_unexhausted_representative_count": len(representatives) - len(exhausted),
        "representatives": audited,
        "audit_scope": (
            "Binds fixed-anchor manifests to the frozen representative table; rehashes, "
            "recounts, and strict-order checks catalogues; checks terminal join identity, "
            "coverage, and zero final pools. Source semantics remain a review/reproduction obligation."
        ),
    }
    output = args.json or Path(__file__).with_name("exhausted_representatives_audit.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
