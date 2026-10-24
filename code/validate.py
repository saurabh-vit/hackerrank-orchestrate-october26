"""Contract validator for output.csv."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from planner import OPERATION_ORDER, PHASE_ORDER  # noqa: E402

DATA = ROOT / "dataset"
EXPECTED_HEADER = ["case_id", "deletion_status", "steps_json"]
LEGAL = {
    "FINDING": {"REPORT_REMAINING_RECORD": "PRESENT", "REPORT_EXPOSED_PII": "PRESENT", "REPORT_ACTIVE_DATA_FLOW": "ACTIVE", "REPORT_RESTORE_RISK": "ACTIVE"},
    "REMEDIATION": {"DISABLE_DATA_FLOW": "DISABLED", "BLOCK_RESTORE": "BLOCKED", "DELETE_RECORD": "ABSENT", "REDACT_RECORD": "REDACTED", "ANONYMIZE_RECORD": "ANONYMIZED"},
    "VERIFICATION": {"VERIFY_RECORD_ABSENT": "ABSENT", "VERIFY_RECORD_PRESENT": "PRESENT", "VERIFY_RECORD_REDACTED": "REDACTED", "VERIFY_RECORD_ANONYMIZED": "ANONYMIZED", "VERIFY_DATA_FLOW_DISABLED": "DISABLED", "VERIFY_RESTORE_BLOCKED": "BLOCKED"},
}


def _ids(path: Path, key: str) -> set[str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {row.get(key, "") for row in csv.DictReader(handle) if row.get(key, "")}


def validate(path: Path = ROOT / "output.csv") -> list[str]:
    errors: list[str] = []
    request_ids = [row["case_id"] for row in _rows(DATA / "deletion_requests.csv")]
    evidence_ids = _ids(DATA / "evidence_files.csv", "file_id") | _ids(DATA / "system_activity.csv", "activity_id") | _ids(DATA / "user_audit_log.csv", "audit_id")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_HEADER:
            errors.append(f"header: expected {EXPECTED_HEADER}, got {reader.fieldnames}")
        rows = list(reader)
    if len(rows) != 518:
        errors.append(f"row count: expected 518, got {len(rows)}")
    ids = [row.get("case_id", "") for row in rows]
    if ids != sorted(ids): errors.append("case_id order is not sorted")
    if set(ids) != set(request_ids): errors.append("case_id set does not match deletion_requests.csv")
    for row in rows:
        case = row.get("case_id", "?")
        status = row.get("deletion_status", "")
        if status not in {"COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"}:
            errors.append(f"{case}: invalid status {status}")
        try:
            steps = json.loads(row.get("steps_json", ""))
        except json.JSONDecodeError as exc:
            errors.append(f"{case}: invalid steps_json: {exc}")
            continue
        if not isinstance(steps, list):
            errors.append(f"{case}: steps_json is not an array")
            continue
        if status == "NOT_APPLICABLE" and steps != []: errors.append(f"{case}: NOT_APPLICABLE must have []")
        numbers = [step.get("step_no") for step in steps]
        if numbers != list(range(1, len(steps) + 1)): errors.append(f"{case}: step_no is not consecutive")
        previous = None
        for step in steps:
            phase, operation, state = step.get("phase"), step.get("operation"), step.get("state")
            if phase not in LEGAL or LEGAL[phase].get(operation) != state: errors.append(f"{case}: illegal phase/operation/state {phase}/{operation}/{state}")
            key = (PHASE_ORDER.get(phase, 99), OPERATION_ORDER.get(phase, {}).get(operation, 99), step.get("system_id", ""), step.get("resource_id", ""))
            if previous is not None and key < previous: errors.append(f"{case}: ordering violation at step {step.get('step_no')}")
            previous = key
            evidence_id = step.get("evidence_id", "")
            if status == "COMPLETE" and evidence_id not in evidence_ids: errors.append(f"{case}: unknown COMPLETE evidence_id {evidence_id}")
            if status == "INCOMPLETE" and phase in {"REMEDIATION", "VERIFICATION"} and evidence_id != "": errors.append(f"{case}: INCOMPLETE {phase} evidence_id must be empty")
    return errors


def _rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle: return list(csv.DictReader(handle))


if __name__ == "__main__":
    failures = validate(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output.csv")
    if failures:
        print("INVALID")
        print("\n".join(failures))
        raise SystemExit(1)
    print("VALID: output.csv satisfies the submission contract")
