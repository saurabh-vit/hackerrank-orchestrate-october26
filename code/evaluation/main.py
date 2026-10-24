"""Evaluate the deterministic deletion-audit pipeline on public samples."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "code"
DATA = ROOT / "dataset"
sys.path.insert(0, str(CODE))

from evidence.pipeline import _rows, collect_case  # noqa: E402
from identity import IdentityResolver  # noqa: E402
from intent import classify_text  # noqa: E402
from planner import plan  # noqa: E402
from rules import decide, load_rules  # noqa: E402
from state import reconstruct  # noqa: E402


STEP_FIELDS = ("phase", "operation", "system_id", "resource_id", "state")
ALL_FIELDS = STEP_FIELDS + ("evidence_id",)


def _predict(case, resolver, rules, activities):
    intent = classify_text(case.get("request_text", ""))
    if intent.intent == "NOT_APPLICABLE":
        return {"case_id": case["case_id"], "deletion_status": "NOT_APPLICABLE", "steps_json": []}
    evidence = collect_case(case, ROOT / "dataset", resolver)
    states = reconstruct(evidence.observations, activities, case["audit_at"])
    decisions = { (s.system_id, s.resource_id): decide(rules, s, now=case["audit_at"]) for s in states }
    incomplete = False
    for state in states:
        action = decisions[(state.system_id, state.resource_id)].required_action
        compliant = ((action == "DELETE" and state.state == "ABSENT") or
                     (action == "REDACT" and state.state == "REDACTED" and not state.direct_identifiers_exposed) or
                     (action == "ANONYMIZE" and state.state == "ANONYMIZED" and not state.direct_identifiers_exposed) or
                     (action == "RETAIN" and state.state in {"PRESENT", "REDACTED", "ANONYMIZED"}) or
                     (action == "DISABLE" and not state.active_data_flow) or
                     (action == "BLOCK" and not state.restore_risk))
        incomplete |= not compliant or state.active_data_flow or state.restore_risk
    steps = [s.to_dict() for s in plan(states, decisions, complete=not incomplete)]
    return {"case_id": case["case_id"], "deletion_status": "INCOMPLETE" if incomplete else "COMPLETE", "steps_json": steps}


def _step_key(step, fields=STEP_FIELDS):
    return tuple(step.get(field, "") for field in fields)


def compare(expected, actual):
    result = {
        "status_ok": expected["deletion_status"] == actual["deletion_status"],
        "row_exact": expected["deletion_status"] == actual["deletion_status"] and expected["steps_json"] == actual["steps_json"],
    }
    exp, got = expected["steps_json"], actual["steps_json"]
    expected_keys, actual_keys = [_step_key(s) for s in exp], [_step_key(s) for s in got]
    ec, ac = Counter(expected_keys), Counter(actual_keys)
    tp = sum((ec & ac).values())
    precision = tp / len(actual_keys) if actual_keys else (1.0 if not expected_keys else 0.0)
    recall = tp / len(expected_keys) if expected_keys else (1.0 if not actual_keys else 0.0)
    result["step_f1"] = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    result["sequence_ok"] = expected_keys == actual_keys
    n = max(len(exp), len(got))
    result["field_accuracy"] = {field: (sum(i < len(exp) and i < len(got) and exp[i].get(field, "") == got[i].get(field, "") for i in range(n)) / n if n else 1.0) for field in ALL_FIELDS}
    if not result["row_exact"]:
        result["diff"] = {"expected_status": expected["deletion_status"], "actual_status": actual["deletion_status"], "expected_steps": exp, "actual_steps": got}
    return result


def evaluate(request_name="sample_deletion_requests.csv", expected_name="sample_output.csv"):
    requests = {r["case_id"]: r for r in _rows(DATA / request_name)}
    expected = {r["case_id"]: {"case_id": r["case_id"], "deletion_status": r["deletion_status"], "steps_json": json.loads(r["steps_json"])} for r in _rows(DATA / expected_name)}
    resolver, rules = IdentityResolver.from_dataset(DATA), load_rules(DATA / "deletion_rules.csv")
    activities = _rows(DATA / "system_activity.csv")
    actual = {case_id: _predict(request, resolver, rules, activities) for case_id, request in requests.items()}
    comparisons = {case_id: compare(expected[case_id], actual[case_id]) for case_id in expected if case_id in actual}
    if not comparisons:
        return {"cases": len(actual), "actual": actual, "comparisons": {}, "failing_cases": []}
    fields = {field: sum(c["field_accuracy"][field] for c in comparisons.values()) / len(comparisons) for field in ALL_FIELDS}
    metrics = {
        "cases": len(comparisons),
        "case_status_accuracy": sum(c["status_ok"] for c in comparisons.values()) / len(comparisons),
        "row_exact_match": sum(c["row_exact"] for c in comparisons.values()) / len(comparisons),
        "step_f1": sum(c["step_f1"] for c in comparisons.values()) / len(comparisons),
        "sequence_accuracy": sum(c["sequence_ok"] for c in comparisons.values()) / len(comparisons),
        "field_accuracy": fields,
        "failing_cases": [case_id for case_id, c in comparisons.items() if not c["row_exact"]],
        "actual": actual,
        "comparisons": comparisons,
    }
    return metrics


def _append_changelog(label, metrics):
    path = Path(__file__).with_name("CHANGELOG.md")
    if not path.exists():
        path.write_text("# Evaluation changelog\n\n| Iteration | Status | Row exact | Step F1 | Sequence | Evidence field | Failing cases |\n|---|---:|---:|---:|---:|---:|---:|\n", encoding="utf-8")
    line = f"| {label} | {metrics['case_status_accuracy']:.3f} | {metrics['row_exact_match']:.3f} | {metrics['step_f1']:.3f} | {metrics['sequence_accuracy']:.3f} | {metrics['field_accuracy']['evidence_id']:.3f} | {len(metrics['failing_cases'])} |\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def _print_report(metrics):
    print(json.dumps({k: v for k, v in metrics.items() if k not in {"actual", "comparisons"}}, indent=2, sort_keys=True))
    for case_id in metrics["failing_cases"]:
        print(f"\nDIFF {case_id}")
        print(json.dumps(metrics["comparisons"][case_id]["diff"], indent=2))


def main():
    metrics = evaluate()
    _append_changelog("final sample run", metrics)
    _print_report(metrics)
    full = evaluate("deletion_requests.csv", "sample_output.csv")
    print("\nFULL DATASET DISTRIBUTION")
    print(dict(Counter(row["deletion_status"] for row in full["actual"].values())))
    print("SAMPLE EXPECTED DISTRIBUTION")
    sample = {r["case_id"]: r for r in _rows(DATA / "sample_output.csv")}
    print(dict(Counter(r["deletion_status"] for r in sample.values())))
    print("FULL NON-APPLICABLE CASES", sum(row["deletion_status"] == "NOT_APPLICABLE" for row in full["actual"].values()))
    sample_steps = {status: [len(json.loads(row["steps_json"])) for row in sample.values() if row["deletion_status"] == status] for status in {r["deletion_status"] for r in sample.values()}}
    full_steps = {status: [len(row["steps_json"]) for row in full["actual"].values() if row["deletion_status"] == status] for status in {r["deletion_status"] for r in sample.values()}}
    print("SAMPLE STEP COUNTS", {k: {"min": min(v), "max": max(v), "avg": round(sum(v) / len(v), 2)} for k, v in sample_steps.items()})
    print("FULL STEP COUNTS", {k: {"min": min(v), "max": max(v), "avg": round(sum(v) / len(v), 2)} for k, v in full_steps.items() if v})
    outliers = []
    limits = {status: max(values) for status, values in sample_steps.items()}
    for case_id, row in full["actual"].items():
        count = len(row["steps_json"])
        if row["deletion_status"] in limits and count > limits[row["deletion_status"]] * 2:
            outliers.append((case_id, row["deletion_status"], count, "more than twice sample maximum"))
        if row["deletion_status"] == "INCOMPLETE" and count == 0:
            outliers.append((case_id, row["deletion_status"], count, "incomplete with no steps"))
    print("FULL OUTLIERS", outliers[:50], "count=", len(outliers))


if __name__ == "__main__":
    main()
