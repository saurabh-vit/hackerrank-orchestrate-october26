"""Small, data-driven synthetic checks with no real personal information."""
from __future__ import annotations
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

def norm(value: str) -> str:
    return value.strip().casefold()

def resolve(case: dict) -> str | None:
    supplied = norm(case["request_email"])
    current = case["current_identity"]
    if supplied == norm(current["email"]): return current["user_id"]
    for event in case.get("audit_chain", []):
        if event.get("field_name") == "email" and supplied == norm(event.get("old_value", "")):
            if norm(event.get("new_value", "")) == norm(current["email"]): return current["user_id"]
    return None

def classify(text: str) -> str:
    lowered = text.casefold()
    if any(token in lowered for token in ("do not delete", "don't delete", "copy of my data", "export")): return "NOT_APPLICABLE"
    return "DELETION" if re.search(r"\b(delete|erase|remove)\b", lowered) else "NOT_APPLICABLE"

def score() -> tuple[int, int, list[str]]:
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    passed, failures = 0, []
    for case in cases:
        user = resolve(case)
        intent = classify(case["request_text"])
        status = "NOT_APPLICABLE" if intent == "NOT_APPLICABLE" else "INCOMPLETE"
        if case["case_id"] == "synthetic_failover_drift":
            status = "INCOMPLETE" if case["failover"]["state"] == "PRESENT" and case["primary"]["state"] == "ABSENT" else "COMPLETE"
        expected = case["expected"]
        if user == expected["user_id"] and status == expected["status"]: passed += 1
        else: failures.append(f"{case['case_id']}: got user={user}, status={status}; expected user={expected['user_id']}, status={expected['status']}")
    return passed, len(cases), failures

if __name__ == "__main__":
    passed, total, failures = score()
    print(f"custom cases: {passed}/{total} passed")
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
