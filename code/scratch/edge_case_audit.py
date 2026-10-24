"""Scratch-only audit of requested edge behaviors; never used by production."""
from __future__ import annotations
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
from identity import IdentityResolver
from evidence.pipeline import _rows, collect_case, _parse_file
from evaluation.main import _predict
from rules import load_rules

DATA = ROOT / "dataset"
resolver = IdentityResolver.from_dataset(DATA)
rules = load_rules(DATA / "deletion_rules.csv")
requests = _rows(DATA / "deletion_requests.csv")
activities = _rows(DATA / "system_activity.csv")
out = {r["case_id"]: r for r in _rows(ROOT / "output.csv")}

def case_for_user(uid):
    return [r["case_id"] for r in requests if resolver.resolve_email(r["email"]).user_id == uid]

def users_in(text):
    return re.findall(r"user_\d+", text or "", flags=re.I)

def output_for(cid):
    row = out[cid]
    return row["deletion_status"], json.loads(row["steps_json"])

def compact(cid):
    status, steps = output_for(cid)
    return {"case_id": cid, "status": status, "steps": [
        {k: s[k] for k in ("phase", "operation", "system_id", "resource_id", "state", "evidence_id")}
        for s in steps
    ]}

def main():
    print("HISTORICAL_CASES")
    shown = 0
    for row in requests:
        res = resolver.resolve_email(row["email"])
        if any("audit:" in item for item in res.matched_on):
            print(row["case_id"], res.user_id, ",".join(res.matched_on), row["audit_at"])
            shown += 1
            if shown == 10: break
    print("RESOURCE_EVIDENCE_CASES")
    resource_users = {}
    manifests = _rows(DATA / "evidence_files.csv")
    for manifest in manifests:
        try:
            parsed = _parse_file(DATA / manifest["file_path"], tuple(sorted(manifest.items())), DATA / "evidence" / ".vision_cache")
        except Exception as exc:
            print("PARSE_ERROR", manifest.get("file_id"), type(exc).__name__)
            continue
        for obs in parsed:
            ids = list(obs.identifiers_seen)
            us = {x.split(":", 1)[1] for x in ids if x.startswith("user_id:")}
            for em in [x.split(":", 1)[1] for x in ids if x.startswith("email:")]:
                try:
                    uid = resolver.resolve_email(em).user_id
                    if uid: us.add(uid)
                except Exception:
                    pass
            for uid in us:
                resource_users.setdefault(obs.resource_id, set()).add(uid)
    for resource, users in sorted(resource_users.items()):
        if resource:
            cases = sorted({cid for u in users for cid in case_for_user(u)})
            if cases:
                print(resource, ",".join(sorted(users)), ",".join(cases))
    print("ACTIVITY_RESOURCE_CASES")
    seen = set()
    for a in activities:
        if a.get("event_type") not in {"RESTORE_BACKUP", "CHECK_DATA_FLOW", "CHECK_RESTORE_ACCESS", "DISABLE_DATA_FLOW", "BLOCK_RESTORE", "DELETE_RECORD", "LINK_RESOURCE_IDENTITY"}:
            continue
        us = set(users_in(" ".join(a.values())))
        for u in us:
            for cid in case_for_user(u):
                key = (a.get("activity_id"), cid)
                if key not in seen and (a.get("event_type") in {"RESTORE_BACKUP", "LINK_RESOURCE_IDENTITY"} or a.get("resource_id", "").startswith(("data_flow_", "backup_"))):
                    seen.add(key)
                    print(a.get("activity_id"), a.get("event_type"), a.get("resource_id"), u, cid, a.get("reported_result"), a.get("details", ""))
    print("SELECTED_OUTPUTS")
    # Concrete cases selected from the participant-facing records.
    selected = ["case_33", "case_34", "case_35", "case_39", "case_45", "case_46", "case_50", "case_53", "case_55", "case_61", "case_63"]
    for cid in selected:
        print(json.dumps(compact(cid), separators=(",", ":")))
    print("SELECTED_OBSERVATIONS")
    for cid in selected:
        case = next(r for r in requests if r["case_id"] == cid)
        ce = collect_case(case, DATA, resolver)
        print(cid, ce.user_id, "excluded", ce.excluded_after_audit)
        for o in ce.observations:
            print(" ", o.evidence_id, o.system_id, o.resource_id, o.record_type, o.state, o.observed_at, "|", o.source_detail[:120])
    print("RESTORE_AND_REVERSE_SEARCH")
    for a in activities:
        if a.get("event_type") == "RESTORE_BACKUP" or "re-enabled" in (a.get("details", "").casefold()):
            print(a)

if __name__ == "__main__":
    main()
