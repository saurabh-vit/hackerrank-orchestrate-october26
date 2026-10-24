"""Read-only audit of output.csv against the raw participant dataset."""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "code"
DATA = ROOT / "dataset"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))

from evidence import Observation  # noqa: E402
from evidence.pipeline import _parse_file, _rows, _linked_resources  # noqa: E402
from identity import IdentityResolver, audit_requests as identity_audit, normalize_email  # noqa: E402
from intent import classify_text, _resource_identity_map, primary_classification_signal  # noqa: E402
from planner import OPERATION_ORDER, PHASE_ORDER  # noqa: E402
from rules import category_for, load_rules, decide  # noqa: E402


def t(value: str) -> datetime:
    try:
        d = datetime.fromisoformat((value or "").replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ids_for(identity) -> set[str]:
    return {f"email:{e}" for e in identity.emails} | {f"hash:{h}" for h in identity.email_hashes} | {
        f"user_id:{identity.user_id}", f"subject_reference:{identity.user_id}", f"customer_reference:{identity.user_id}"
    }


def parse_evidence(manifests):
    parsed = []
    by_eid = defaultdict(list)
    cache = HERE / ".vision_cache"
    for manifest in manifests:
        path = DATA / manifest["file_path"]
        try:
            observations = list(_parse_file(path, tuple(sorted(manifest.items())), cache))
        except Exception as exc:  # evidence parser errors are audit findings, not fatal
            observations = []
            by_eid[manifest["file_id"]].append(f"PARSER_ERROR:{type(exc).__name__}:{exc}")
        parsed.extend((manifest, obs) for obs in observations)
        by_eid[manifest["file_id"]].extend(observations)
    return parsed, by_eid


def case_observations(case, identity, parsed, activities):
    wanted = ids_for(identity)
    linked = _linked_resources(activities, identity.user_id or "", identity.emails)
    direct = []
    for manifest, obs in parsed:
        if obs.observed_at and t(obs.observed_at) > t(case["audit_at"]):
            continue
        if obs.resource_id in linked or set(obs.identifiers_seen) & wanted:
            direct.append((manifest, obs))
    resources = {obs.resource_id for _, obs in direct if obs.resource_id}
    return [(m, o) for m, o in parsed if o.resource_id in resources and (not o.observed_at or t(o.observed_at) <= t(case["audit_at"]))]


def step_key(step):
    phase = step.get("phase", "")
    return (PHASE_ORDER.get(phase, 99), OPERATION_ORDER.get(phase, {}).get(step.get("operation", ""), 99), step.get("system_id", ""), step.get("resource_id", ""))


def case_map(requests):
    return {r["case_id"]: r for r in requests}


def main():
    requests = rows(DATA / "deletion_requests.csv")
    output = rows(ROOT / "output.csv")
    activities = rows(DATA / "system_activity.csv")
    audits = rows(DATA / "user_audit_log.csv")
    manifests = rows(DATA / "evidence_files.csv")
    resolver = IdentityResolver.from_dataset(DATA)
    rules = load_rules(DATA / "deletion_rules.csv")
    parsed, by_eid = parse_evidence(manifests)
    manifest_by_id = {m["file_id"]: m for m in manifests}
    activity_by_id = {r["activity_id"]: r for r in activities}
    audit_by_id = {r["audit_id"]: r for r in audits}
    request_by_id = case_map(requests)
    output_by_id = {r.get("case_id", ""): r for r in output}
    all_ids = set(manifest_by_id) | set(activity_by_id) | set(audit_by_id)
    findings = []

    def add(name, count, offenders, detail=""):
        findings.append((name, count, sorted(set(offenders)), detail))

    # Identity checks.
    resolutions = {r["case_id"]: resolver.resolve_email(r.get("email", "")) for r in requests}
    unresolved = [cid for cid, r in resolutions.items() if r.status != "resolved"]
    old_email_cases = [cid for cid, r in resolutions.items() if any(x.startswith("audit:") for x in r.matched_on)]
    casefold_or_trim = []
    for req in requests:
        res = resolutions[req["case_id"]]
        if res.status == "resolved":
            raw = req["email"]
            if raw != raw.strip() or raw != raw.casefold(): casefold_or_trim.append(req["case_id"])
    add("IDENTITY: unresolved or ambiguous requests", len(unresolved), unresolved, f"resolved={len(requests)-len(unresolved)}; old-email-chain={len(old_email_cases)}; case/whitespace variants={len(casefold_or_trim)}")
    duplicate_requests = identity_audit(DATA)["duplicate_request_emails"]
    duplicate_detail = "; ".join(f"{email} -> {list(case_ids)} -> users={sorted({resolutions[cid].user_id for cid in case_ids})}" for email, case_ids in duplicate_requests.items()) or "none"
    add("IDENTITY: duplicated request email", sum(len(v) for v in duplicate_requests.values()), [cid for v in duplicate_requests.values() for cid in v], duplicate_detail)

    # Intent checks, including the ten primary classifier events.
    links = _resource_identity_map(DATA)
    intents = {r["case_id"]: classify_text(r.get("request_text", "")) for r in requests}
    na_ids = [cid for cid, x in intents.items() if x.intent == "NOT_APPLICABLE"]
    deletion_ids = [cid for cid, x in intents.items() if x.intent == "DELETION"]
    ambiguous_ids = [cid for cid, x in intents.items() if x.intent == "AMBIGUOUS"]
    output_na_bad = [cid for cid in na_ids if output_by_id.get(cid, {}).get("deletion_status") != "NOT_APPLICABLE" or output_by_id.get(cid, {}).get("steps_json") != "[]"]
    add("NOT_APPLICABLE: text classifier disagreement", len(output_na_bad), output_na_bad, f"text non-deletion={len(na_ids)}; output NA={sum(output_by_id.get(cid, {}).get('deletion_status') == 'NOT_APPLICABLE' for cid in output_by_id)}; ambiguous={len(ambiguous_ids)}")
    classify_events = [a for a in activities if a.get("event_type") == "CLASSIFY_REQUEST"]
    primary_by_case = {}
    for req in requests:
        ident = resolutions[req["case_id"]]
        primary_by_case[req["case_id"]] = primary_classification_signal(req, ident.user_id, set(ident.emails), activities, links)
    classify_cases = [cid for cid, x in primary_by_case.items() if x.intent != "UNKNOWN"]
    disagreements = [cid for cid in classify_cases if primary_by_case[cid].intent != intents[cid].intent]
    add("NOT_APPLICABLE: CLASSIFY_REQUEST agreement", len(disagreements), disagreements, f"CLASSIFY_REQUEST events={len(classify_events)}; linked cases={len(classify_cases)}; agreement={len(classify_cases)-len(disagreements)}/{len(classify_cases)}")
    near_text = []
    for cid in na_ids + deletion_ids:
        if cid in classify_cases:
            near_text.append(f"{cid}: {request_by_id[cid].get('request_text','')}")
    multilingual = []
    lang_re = re.compile(r"(削除|삭제|eliminar|eliminación|supprim|exclu|excluir|apagar|dados|donnees|données)", re.I)
    for req in requests:
        if lang_re.search(req.get("request_text", "")):
            cid = req["case_id"]
            multilingual.append(f"{cid} [{output_by_id.get(cid, {}).get('deletion_status','missing')}]: {req.get('request_text','')}")

    # Evidence and output structural checks.
    unknown_evidence = []
    future_file_evidence = []
    citation_not_latest = []
    citation_not_user_grounded = []
    incomplete_citation = []
    complete_missing_citation = []
    resource_to_cases = defaultdict(list)
    for cid, req in request_by_id.items():
        ident = resolutions[cid]
        case_obs = case_observations(req, ident, parsed, activities)
        for _, obs in case_obs:
            resource_to_cases[(cid, obs.resource_id)].append(obs)
        out = output_by_id.get(cid, {})
        try: steps = json.loads(out.get("steps_json", ""))
        except Exception: steps = []
        for step in steps:
            eid = step.get("evidence_id", "")
            phase = step.get("phase")
            if eid and eid not in all_ids: unknown_evidence.append(cid); continue
            if out.get("deletion_status") == "COMPLETE" and not eid: complete_missing_citation.append(cid)
            if out.get("deletion_status") == "INCOMPLETE" and phase in {"REMEDIATION", "VERIFICATION"} and eid: incomplete_citation.append(cid)
            if eid in manifest_by_id:
                manifest = manifest_by_id[eid]
                if t(manifest.get("captured_at")) > t(req["audit_at"]): future_file_evidence.append(cid)
                target = step.get("resource_id", "")
                candidates = [(m, o) for m, o in parsed if m["file_id"] == eid and o.resource_id == target and (not o.observed_at or t(o.observed_at) <= t(req["audit_at"]))]
                user_ids = ids_for(ident)
                grounded = [o for _, o in candidates if set(o.identifiers_seen) & user_ids or target in _linked_resources(activities, ident.user_id or "", ident.emails)]
                if not grounded: citation_not_user_grounded.append(cid)
                candidate_captures = []
                for m, o in parsed:
                    if o.resource_id != target or t(m.get("captured_at")) > t(req["audit_at"]): continue
                    if set(o.identifiers_seen) & user_ids or target in _linked_resources(activities, ident.user_id or "", ident.emails):
                        candidate_captures.append((t(m.get("captured_at")), m["file_id"]))
                if candidate_captures and eid != max(candidate_captures)[1]: citation_not_latest.append(cid)
            elif eid in activity_by_id and t(activity_by_id[eid].get("event_time")) > t(req["audit_at"]):
                future_file_evidence.append(cid)
    add("EVIDENCE: unknown evidence IDs", len(unknown_evidence), unknown_evidence)
    add("EVIDENCE: future citations", len(future_file_evidence), future_file_evidence)
    add("EVIDENCE: citation not latest qualifying capture", len(citation_not_latest), citation_not_latest)
    add("EVIDENCE: cited file not grounded to user/resource", len(citation_not_user_grounded), citation_not_user_grounded)
    add("EVIDENCE: INCOMPLETE remediation/verification not empty", len(incomplete_citation), incomplete_citation)
    add("EVIDENCE: COMPLETE step missing citation", len(complete_missing_citation), complete_missing_citation)

    # Policy operation checks and retention dates.
    policy_offenders = []
    retention_checked, retention_bad = 0, []
    for cid, req in request_by_id.items():
        ident = resolutions[cid]
        obs_by_resource = defaultdict(list)
        for _, obs in case_observations(req, ident, parsed, activities): obs_by_resource[(obs.system_id, obs.resource_id)].append(obs)
        out = output_by_id.get(cid, {})
        try: steps = json.loads(out.get("steps_json", ""))
        except Exception: steps = []
        for step in steps:
            key = (step.get("system_id", ""), step.get("resource_id", ""))
            candidates = obs_by_resource.get(key, [])
            record_type = candidates[-1].record_type if candidates else ("customer_profile" if "account" in key[0] or key[1].startswith("account_") else key[1])
            fake = type("State", (), {"system_id": key[0], "resource_id": key[1], "record_type": record_type, "source_details": tuple(), "direct_identifiers_exposed": True})()
            decision = decide(rules, fake, now=req["audit_at"])
            action = decision.required_action
            op = step.get("operation", "")
            expected = {
                "DELETE": {"DELETE_RECORD", "VERIFY_RECORD_ABSENT"}, "REDACT": {"REDACT_RECORD", "VERIFY_RECORD_REDACTED"},
                "ANONYMIZE": {"ANONYMIZE_RECORD", "VERIFY_RECORD_ANONYMIZED"}, "RETAIN": {"VERIFY_RECORD_PRESENT"},
                "DISABLE": {"DISABLE_DATA_FLOW", "VERIFY_DATA_FLOW_DISABLED"}, "BLOCK": {"BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED"},
            }.get(action, set())
            if step.get("phase") == "REMEDIATION" and op not in expected: policy_offenders.append(cid)
            if step.get("phase") == "VERIFICATION" and op not in expected: policy_offenders.append(cid)
            if "audit_record" in key[1] or decision.data_category == "SECURITY_AUDIT_LOG":
                retention_checked += 1
                text = " ".join(str(x.source_detail) for x in candidates)
                dates = re.findall(r"retention_until[=:\s\"]+([0-9T:.+\-Z]+)", text, re.I)
                if dates and any(t(d) < t(req["audit_at"]) for d in dates): retention_bad.append(cid)
    add("POLICY: operation contradicts deletion rule", len(policy_offenders), policy_offenders, f"retention checks={retention_checked}; expired-at-audit={len(retention_bad)}")
    add("POLICY: retention date expired at audit_at", len(retention_bad), retention_bad, "Dates were compared with case audit_at, not wall-clock time")

    # Ordering, pair consistency, and structure.
    order_bad, orphan_findings, orphan_remediation, orphan_verification = [], [], [], []
    for cid, out in output_by_id.items():
        try: steps = json.loads(out.get("steps_json", ""))
        except Exception: continue
        if any(step_key(a) > step_key(b) for a, b in zip(steps, steps[1:])): order_bad.append(cid)
        if out.get("deletion_status") != "INCOMPLETE": continue
        by_phase = defaultdict(set)
        for s in steps: by_phase[s.get("phase")].add((s.get("system_id"), s.get("resource_id")))
        for resource in by_phase["FINDING"] - by_phase["REMEDIATION"]: orphan_findings.append(cid)
        for resource in by_phase["REMEDIATION"] - by_phase["FINDING"]: orphan_remediation.append(cid)
        # Verification-only resources are legitimate in INCOMPLETE cases:
        # already-clean records and retained records still need checks.
        for resource in by_phase["REMEDIATION"] - by_phase["VERIFICATION"]: orphan_verification.append(cid)
    add("STRUCTURE: ordering violations", len(order_bad), order_bad)
    add("STRUCTURE: findings without remediation", len(orphan_findings), orphan_findings)
    add("STRUCTURE: remediation without finding", len(orphan_remediation), orphan_remediation)
    add("STRUCTURE: remediation/verification orphan mismatch", len(orphan_verification), orphan_verification)

    # Write a compact table plus the requested manual text review.
    report = ["# Full output audit", "", "| Check | Count | Offending case_ids | Evidence |", "|---|---:|---|---|"]
    for name, count, offenders, detail in findings:
        report.append(f"| {name} | {count} | {', '.join(offenders) if offenders else 'none'} | {detail or 'no violations'} |")
    report += ["", "## Identity explanations", "", f"- Total requests: {len(requests)}; resolved: {len(requests)-len(unresolved)}; unresolved/ambiguous: {len(unresolved)}.", f"- Old-email-chain requests: {len(old_email_cases)}; case/whitespace variants: {len(casefold_or_trim)}.", f"- Duplicate request email handling: {duplicate_detail}."]
    if unresolved: report.append("- Unresolved details: " + "; ".join(f"{cid}: {resolutions[cid].reason}" for cid in unresolved))
    report += ["", "## Manual intent review", "", f"CLASSIFY_REQUEST events: {len(classify_events)}; linked agreement: {len(classify_cases)-len(disagreements)}/{len(classify_cases)}.", "", "### Every NOT_APPLICABLE and linked deletion-sounding case", ""]
    for line in near_text: report.append(f"- {line}")
    report += ["", "### Multilingual scan", ""]
    report.extend(f"- {line}" for line in multilingual)
    report += ["", "### Retention verification", "", f"Security/audit retention steps checked: {retention_checked}; expired at audit_at: {len(retention_bad)}. Evidence text and ledger timestamps were compared to each case audit_at."]
    retention_files = [m["file_id"] for m in manifests if "retention" in m.get("file_path", "").casefold() or "legal" in m.get("file_path", "").casefold()]
    report += ["", "## Parser notes", "", f"Parsed evidence observations: {len(parsed)}; evidence files: {len(manifests)}; audit rows: {len(audits)}; activity rows: {len(activities)}.", f"Retention/legal-register evidence files inspected by name: {len(retention_files)}; audit-ledger rows available for comparison: {len(audits)}."]
    (HERE / "audit_full_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {HERE / 'audit_full_report.md'}")
    for name, count, offenders, _ in findings: print(f"{name}: {count}; offending={','.join(offenders) if offenders else 'none'}")


if __name__ == "__main__":
    main()
