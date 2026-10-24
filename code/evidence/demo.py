from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence.pipeline import collect_case, sample_output, _rows
from identity import IdentityResolver

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataset"

def main():
    requests = {r["case_id"]: r for r in _rows(DATA / "sample_deletion_requests.csv")}
    expected = sample_output(DATA)
    for case_id in ("case_05", "case_10", "case_31"):
        evidence = collect_case(requests[case_id], DATA, IdentityResolver.from_dataset(DATA))
        expected_keys = {(s["evidence_id"], s["system_id"], s["resource_id"]) for s in expected[case_id] if s["evidence_id"]}
        observed_keys = {(o.evidence_id, o.system_id, o.resource_id) for o in evidence.observations}
        print(json.dumps({"case_id": case_id, "user_id": evidence.user_id, "excluded_after_audit": evidence.excluded_after_audit, "observations": [o.to_dict() for o in evidence.observations], "expected_evidence_keys": sorted(expected_keys), "matched_expected_keys": sorted(expected_keys & observed_keys), "missing_expected_keys": sorted(expected_keys - observed_keys)}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
