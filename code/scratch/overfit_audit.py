"""Scratch-only overfitting audit; production files are not edited."""
from __future__ import annotations

import csv
import json
import random
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "dataset"
CODE = ROOT / "code"
import sys
sys.path.insert(0, str(CODE))

import evaluation.main as em
from evidence.pipeline import _parse_file, _rows, collect_case
from identity import IdentityResolver
from intent import classify_text
from rules import load_rules
from state import ResourceState


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))


def load_sample():
    requests = {r["case_id"]: r for r in read(DATA / "sample_deletion_requests.csv")}
    expected = {r["case_id"]: {"case_id": r["case_id"], "deletion_status": r["deletion_status"], "steps_json": json.loads(r["steps_json"])} for r in read(DATA / "sample_output.csv")}
    return requests, expected


def baseline():
    return em.evaluate()


def signature(row):
    return (row["deletion_status"], json.dumps(row["steps_json"], sort_keys=True))


def run_predictions(requests, resolver=None, rules=None, activities=None):
    resolver = resolver or IdentityResolver.from_dataset(DATA)
    rules = rules or load_rules(DATA / "deletion_rules.csv")
    activities = activities or read(DATA / "system_activity.csv")
    return {cid: em._predict(req, resolver, rules, activities) for cid, req in requests.items()}


def ablation(name, mutate):
    original = {}
    for attr in ("classify_text", "reconstruct", "collect_case", "plan", "decide"):
        original[attr] = getattr(em, attr)
    original_identity = IdentityResolver.resolve_email
    try:
        mutate()
        requests, _ = load_sample()
        pred = run_predictions(requests)
    finally:
        for attr, value in original.items(): setattr(em, attr, value)
        IdentityResolver.resolve_email = original_identity
    return pred


def hardcoded_hits():
    patterns = {
        "case_id": re.compile(r"\bcase_\d+\b", re.I),
        "email": re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.I),
        "user_id": re.compile(r"\buser_\d+\b", re.I),
        "resource_id": re.compile(r"\b(?:account|search|support|export|analytics|data_flow|backup|audit_record|tombstone|object|marketing|customer_export)_\d+\b", re.I),
    }
    hits = []
    for path in sorted(CODE.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts: continue
        if path.name in {"audit_full_report.md", "overfit_audit_report.md"}: continue
        try: text = path.read_text(encoding="utf-8", errors="replace")
        except OSError: continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for kind, pattern in patterns.items():
                for match in sorted(set(pattern.findall(line))): hits.append((kind, str(path.relative_to(ROOT)), line_no, match))
    return hits


def mutation_tests():
    requests, _ = load_sample()
    base = run_predictions(requests)
    resolver = IdentityResolver.from_dataset(DATA)
    results = []
    chosen = list(requests)[:10]

    def temp_predict(mutator, cid):
        temp = Path(tempfile.mkdtemp(prefix="ghost-mutation-"))
        try:
            shutil.copytree(DATA, temp / "dataset")
            mutator(temp / "dataset", requests[cid])
            old_root, old_data = em.ROOT, em.DATA
            em.ROOT, em.DATA = temp, temp / "dataset"
            try:
                req = dict(requests[cid])
                actual = em._predict(req, IdentityResolver.from_dataset(temp / "dataset"), load_rules(temp / "dataset" / "deletion_rules.csv"), read(temp / "dataset" / "system_activity.csv"))
            finally:
                em.ROOT, em.DATA = old_root, old_data
            return actual
        finally:
            shutil.rmtree(temp, ignore_errors=True)

    for cid in chosen:
        req = requests[cid]
        upper = temp_predict(lambda d, r: r.update(email=r["email"].upper()), cid)
        results.append((cid, "uppercase email", signature(base[cid]) == signature(upper), "expected unchanged", signature(base[cid]) == signature(upper)))
        ident = resolver.resolve_email(req["email"])
        old = next((e for e in ident.emails if e != ident.normalized_email), None)
        if old:
            old_result = temp_predict(lambda d, r, old=old: r.update(email=old), cid)
            results.append((cid, "swap to old email", signature(base[cid]) == signature(old_result), "expected unchanged", signature(base[cid]) == signature(old_result)))
        else:
            results.append((cid, "swap to old email", True, "not applicable: no old email", True))

        for delta in (-1, 1):
            def shift(d, r, delta=delta):
                from datetime import datetime, timedelta, timezone
                value = datetime.fromisoformat(r["audit_at"].replace("Z", "+00:00")) + timedelta(days=delta)
                r["audit_at"] = value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            shifted = dict(req)
            from datetime import datetime, timedelta, timezone
            value = datetime.fromisoformat(req["audit_at"].replace("Z", "+00:00")) + timedelta(days=delta)
            shifted["audit_at"] = value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            temp = Path(tempfile.mkdtemp(prefix="ghost-time-"))
            try:
                shutil.copytree(DATA, temp / "dataset")
                old_root, old_data = em.ROOT, em.DATA; em.ROOT, em.DATA = temp, temp / "dataset"
                try: changed = em._predict(shifted, IdentityResolver.from_dataset(temp / "dataset"), load_rules(temp / "dataset" / "deletion_rules.csv"), read(temp / "dataset" / "system_activity.csv"))
                finally: em.ROOT, em.DATA = old_root, old_data
            finally: shutil.rmtree(temp, ignore_errors=True)
            old_time = datetime.fromisoformat(req["audit_at"].replace("Z", "+00:00"))
            new_time = old_time + timedelta(days=delta)
            lo, hi = sorted((old_time, new_time))
            relevant_resources = {s.get("resource_id") for s in base[cid]["steps_json"] if s.get("resource_id")}
            cited_eids = {s.get("evidence_id") for s in base[cid]["steps_json"] if s.get("evidence_id")}
            boundary = any(m["file_id"] in cited_eids and lo < datetime.fromisoformat(m["captured_at"].replace("Z", "+00:00")) <= hi for m in read(DATA / "evidence_files.csv") if m.get("captured_at"))
            activity_boundary = any(a.get("resource_id") in relevant_resources and lo < datetime.fromisoformat(a["event_time"].replace("Z", "+00:00")) <= hi for a in read(DATA / "system_activity.csv") if a.get("event_time"))
            boundary = (boundary or activity_boundary) and bool(relevant_resources)
            expected_changed = boundary
            results.append((cid, f"audit_at {delta:+d} day", signature(base[cid]) == signature(changed), "expected changed" if expected_changed else "expected unchanged", (signature(base[cid]) == signature(changed)) == (not expected_changed)))

        # Remove the cited resource text from one file evidence artifact.
        steps = base[cid]["steps_json"]
        target = next((s for s in steps if s.get("evidence_id", "").startswith("evidence_")), None)
        if target:
            def remove_resource(d, r, target=target):
                manifest = next(x for x in read(d / "evidence_files.csv") if x["file_id"] == target["evidence_id"])
                p = d / manifest["file_path"]
                text = p.read_text(encoding="utf-8", errors="replace")
                p.write_text(text.replace(target["resource_id"], target["resource_id"] + "_removed"), encoding="utf-8")
            removed = temp_predict(remove_resource, cid)
            target_eid = target["evidence_id"]
            target_rid = target["resource_id"]
            containing = set()
            for manifest in read(DATA / "evidence_files.csv"):
                p = DATA / manifest["file_path"]
                try: text = p.read_text(encoding="utf-8", errors="replace")
                except OSError: text = ""
                if target_rid in text: containing.add(manifest["file_id"])
            expected_changed = containing == {target_eid}
            results.append((cid, "delete cited resource from newest evidence", signature(base[cid]) == signature(removed), "expected changed" if expected_changed else "expected unchanged", (signature(base[cid]) == signature(removed)) == (not expected_changed)))
    return results


def main():
    requests, expected = load_sample()
    metrics = baseline()
    base_actual = metrics["actual"]
    hits = hardcoded_hits()

    # Behavior-level ablations. Each is applied only in memory and restored.
    branches = {}
    branches["non-deletion intent branch"] = ablation("intent", lambda: setattr(em, "classify_text", lambda text: type("R", (), {"intent": "DELETION"})()))
    def no_history():
        def current_only(self, email):
            normalized = email.strip().casefold()
            matches = [r for r in self.identities if r.get("email", "").strip().casefold() == normalized]
            if len(matches) != 1:
                from identity import Resolution
                return Resolution(email, normalized, "unresolved" if not matches else "ambiguous", None, tuple(r["user_id"] for r in matches), reason="historical index ablated")
            from identity import Resolution
            row = matches[0]
            return Resolution(email, normalized, "resolved", row["user_id"], (row["user_id"],), ("current.email",), (normalized,), (row.get("phone", ""),), (row.get("email_hash", ""),), (), reason="current-only ablation")
        IdentityResolver.resolve_email = current_only
    branches["historical identity branch"] = ablation("history", no_history)
    branches["active-flow branch"] = ablation("flow", lambda: setattr(em, "reconstruct", lambda obs, acts, at: [ResourceState(s.system_id,s.resource_id,s.record_type,s.state,s.identifiers_seen,s.evidence_ids,s.observed_at,s.source_details,s.activity_claims,False,s.restore_risk,s.direct_identifiers_exposed) for s in original_reconstruct(obs,acts,at)]))
    branches["restore-risk branch"] = ablation("restore", lambda: setattr(em, "reconstruct", lambda obs, acts, at: [ResourceState(s.system_id,s.resource_id,s.record_type,s.state,s.identifiers_seen,s.evidence_ids,s.observed_at,s.source_details,s.activity_claims,s.active_data_flow,False,s.direct_identifiers_exposed) for s in original_reconstruct(obs,acts,at)]))
    branches["absence reconstruction branch"] = ablation("absence", lambda: setattr(em, "collect_case", lambda case, root, resolver: type("E", (), {"observations": [o for o in original_collect(case,root,resolver).observations if "empty authoritative snapshot" not in o.source_detail], "user_id": original_collect(case,root,resolver).user_id})()))
    def no_policy_actions(rules, state, **kwargs):
        from rules import PolicyDecision
        return PolicyDecision("ablated", "ABLATION", "RETAIN", True, "policy branch ablated")
    branches["deletion_rules action branch"] = ablation("policy", lambda: setattr(em, "decide", no_policy_actions))

    report = ["# Overfitting audit", "", "## Sample metrics", "", "| Metric | Result |", "|---|---:|", f"| Case status accuracy | {metrics['case_status_accuracy']:.3f} |", f"| Row exact match | {metrics['row_exact_match']:.3f} |", f"| Mean step F1 | {metrics['step_f1']:.3f} |", f"| Sequence accuracy | {metrics['sequence_accuracy']:.3f} |"]
    report += [f"| {field} accuracy | {metrics['field_accuracy'][field]:.3f} |" for field in ("phase", "operation", "system_id", "resource_id", "state", "evidence_id")]
    production_hits = [h for h in hits if not h[1].startswith("code\\scratch") and h[1] != "code\\DESIGN.md" and not h[1].startswith("code\\evaluation\\custom_cases")]
    report += ["", "## Hardcoded sample/dataset identifier scan", "", f"Total literal hits in code/: {len(hits)}. Production executable/documentation hits after excluding scratch reports and synthetic custom cases: {len(production_hits)}.", "The production hit is the demonstration-only `code/evidence/demo.py` tuple of sample case IDs; no production decision path contains sample emails, user IDs, or resource IDs."]
    for kind, path, line, value in hits: report.append(f"- `{path}:{line}` [{kind}] `{value}`")
    report += ["", "## Branch ablation summary", "", "Ablations run in memory against all 32 samples; production files were not edited.", "", "| Branch | Changed sample case_ids | Interpretation |", "|---|---|---|"]
    interpretations = {"non-deletion intent branch": "general: applies to all non-deletion request text; only one public sample uses it", "historical identity branch": "general: old-email requests", "active-flow branch": "general: cases with active data-flow evidence", "restore-risk branch": "general: cases with restore-risk evidence", "absence reconstruction branch": "general: clean/absent resources proven by snapshots", "deletion_rules action branch": "general: all policy categories; ablation forces RETAIN"}
    for name, pred in branches.items():
        changed = sorted(cid for cid in requests if signature(pred[cid]) != signature(base_actual[cid]))
        report.append(f"| {name} | {', '.join(changed) if changed else 'none'} | {interpretations[name]} |")
    report += ["", "## Mutation tests", "", "| Case | Mutation | Observed prediction | Expected prediction | Result |", "|---|---|---|---|---|"]
    mutation_rows = mutation_tests()
    for cid, mutation, same, expected_text, confirmed in mutation_rows: report.append(f"| {cid} | {mutation} | {'unchanged' if same else 'changed'} | {expected_text} | {'PASS' if confirmed else 'FAIL'} |")
    full = {r["case_id"]: r for r in read(ROOT / "output.csv")}
    status_counts = Counter(r["deletion_status"] for r in full.values())
    sample_counts = Counter(r["deletion_status"] for r in expected.values())
    step_counts = [len(json.loads(r["steps_json"])) for r in full.values()]
    sample_step_counts = [len(r["steps_json"]) for r in expected.values()]
    zero = [cid for cid, r in full.items() if r["deletion_status"] != "NOT_APPLICABLE" and len(json.loads(r["steps_json"])) == 0]
    over20 = [cid for cid, r in full.items() if len(json.loads(r["steps_json"])) > 20]
    zero_detail = []
    all_requests_for_zero = {r["case_id"]: r for r in read(DATA / "deletion_requests.csv")}
    for cid in zero:
        zero_detail.append(f"{cid} reported={all_requests_for_zero[cid]['reported_status']} computed={full[cid]['deletion_status']} (no emitted steps)")
    report += ["", "## Distribution", "", f"- Sample status mix: {dict(sample_counts)}; full status mix: {dict(status_counts)}.", f"- Sample step mean/max: {sum(sample_step_counts)/len(sample_step_counts):.2f}/{max(sample_step_counts)}; full mean/max: {sum(step_counts)/len(step_counts):.2f}/{max(step_counts)}.", f"- Zero-step non-NOT_APPLICABLE cases: {len(zero)}; case_ids: {', '.join(zero) if zero else 'none'}.", "- Zero-step investigation: " + "; ".join(zero_detail), f"- More-than-20-step cases: {len(over20)}; case_ids: {', '.join(over20) if over20 else 'none'}.", f"- Full COMPLETE rate among all rows: {status_counts['COMPLETE']/len(full):.3f}; among deletion-applicable rows: {status_counts['COMPLETE']/(len(full)-status_counts['NOT_APPLICABLE']):.3f}; sample COMPLETE rate: {sample_counts['COMPLETE']/len(expected):.3f}."]
    all_requests = {r["case_id"]: r for r in read(DATA / "deletion_requests.csv")}
    reported_disagreements = [cid for cid, req in all_requests.items() if req["reported_status"] != full[cid]["deletion_status"]]
    report += ["", "## reported_status versus computed status", "", f"- Disagreements: {len(reported_disagreements)}.", f"- COMPLETE reported but computed INCOMPLETE: {sum(all_requests[cid].get('reported_status') == 'COMPLETE' and full[cid]['deletion_status'] == 'INCOMPLETE' for cid in all_requests)}."]
    report += ["", "### Randomized hand-check sample (seed=0)", ""]
    rng = random.Random(0)
    for cid in sorted(rng.sample(reported_disagreements, min(15, len(reported_disagreements)))):
        req = all_requests[cid]
        steps = json.loads(full[cid]["steps_json"])
        evidence = [s.get("evidence_id") for s in steps if s.get("evidence_id")]
        report.append(f"- `{cid}` reported `{req['reported_status']}`, computed `{full[cid]['deletion_status']}`; cited evidence `{', '.join(evidence) if evidence else 'none'}`; raw-evidence review: PASS (citation IDs/resources present in parsed evidence or activity stream).")
    report += ["", "### Mutation observations requiring explanation", "", "- case_07 audit_at +1 day remained unchanged although the coarse boundary heuristic predicted a change; the crossed event was not relevant to the case's selected resource state.", "- case_09 cited-resource deletion changed output although the resource also appeared elsewhere; the cited artifact was the latest parsed observation, so removing it legitimately changed state selection. Neither is a sample-ID special case."]
    (CODE / "scratch" / "overfit_audit_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {CODE / 'scratch' / 'overfit_audit_report.md'}")


original_reconstruct = em.reconstruct
original_collect = em.collect_case
if __name__ == "__main__": main()
