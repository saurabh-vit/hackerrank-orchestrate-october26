from __future__ import annotations
import json
import re
from pathlib import Path
from .common import identifiers, parse_time, resource_ids, state_from
from . import make_observation

KV = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=(?:"([^"]*)"|([^ ]+))')
TIME = re.compile(r"^\s*(\d{4}-\d\d-\d\dT[^ ]+)")

def _record(fields, raw, path, evidence_id, line_no, fallback_time, origin=""):
    rid = fields.get("resource_id") or (resource_ids(raw)[0] if resource_ids(raw) else "")
    if not rid:
        return None
    system = fields.get("service") or fields.get("system") or fields.get("source_system") or fields.get("target_system") or origin
    if system == "support_replica" and origin == "support_platform":
        system = origin
    record_type = fields.get("record_type") or fields.get("event") or "LOG_EVENT"
    raw_state = fields.get("result") or fields.get("state") or fields.get("status") or fields.get("enabled") or fields.get("restore_allowed")
    state = state_from(raw_state)
    if (fields.get("rows") == "0" or fields.get("http_status") in {"404", "410"}) and "completed" in fields.get("event", "").casefold():
        state = "ABSENT"
    if fields.get("event", "").casefold() in {"connector_heartbeat", "restore_candidate_evaluated"}: state = "ACTIVE"
    return make_observation(system_id=system, resource_id=rid, record_type=record_type, state=state, identifiers_seen=identifiers(fields), evidence_id=evidence_id, observed_at=parse_time(fields.get("event_time") or fallback_time), source_detail=f"{path.name}:line={line_no}")

def parse_log(path: Path, evidence_id: str, origin: str = ""):
    trace_context = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip(): continue
        timestamp = TIME.search(line)
        fallback = timestamp.group(1) if timestamp else ""
        fields = {}
        stripped = line.strip()
        if "{" in stripped:
            try:
                obj = json.loads(stripped[stripped.index("{"):])
                if isinstance(obj, dict): fields.update({k: str(v) for k, v in obj.items()})
            except json.JSONDecodeError:
                pass
        for match in KV.finditer(line):
            fields[match.group(1)] = match.group(2) or match.group(3)
        trace_id = fields.get("trace_id") or fields.get("requestId")
        if trace_id:
            previous = trace_context.get(trace_id, {})
            if fields.get("resource_id"):
                for key in ("email", "customer_email", "lookup_key", "subject_key", "correlation_key", "subject_reference", "customer_reference"):
                    if key not in fields and key in previous:
                        fields[key] = previous[key]
            else:
                trace_context[trace_id] = {**previous, **fields}
        obs = _record(fields, line, path, evidence_id, line_no, fallback, origin)
        if obs: yield obs
