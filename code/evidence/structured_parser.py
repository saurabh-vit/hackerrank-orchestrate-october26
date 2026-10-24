from __future__ import annotations
import json
from pathlib import Path
from .common import identifiers, parse_time, resource_ids, state_from
from . import make_observation

def parse_structured(path: Path, evidence_id: str, origin: str = ""):
    value = json.loads(path.read_text(encoding="utf-8"))
    def walk(node, location="$", inherited_time="", inherited_system="", inherited_collection=""):
        if isinstance(node, dict):
            observed = next((parse_time(node.get(k)) for k in ("observed_at", "recorded_at", "captured_at", "updated_at", "created_at", "exported_at") if node.get(k)), inherited_time)
            system_in_scope = str(node.get("data_store") or node.get("system") or node.get("origin_system") or inherited_system or origin)
            collection_in_scope = str(node.get("collection") or inherited_collection)
            rid = str(node.get("resource_id") or "")
            if rid:
                system = str(node.get("system_id") or node.get("system") or node.get("data_store") or node.get("origin_system") or node.get("source_system") or inherited_system or origin)
                raw_state = next((node.get(k) for k in ("state", "result", "status", "record_type", "account_status", "restore_allowed", "enabled") if k in node), None)
                state = state_from(raw_state)
                if collection_in_scope == "deleted_customer_references" and not any(node.get(k) for k in ("name", "email", "phone", "email_hash")):
                    state = "REDACTED"
                if raw_state in (1, "1", True) and ("restore" in str(node).casefold()): state = "ACTIVE"
                if raw_state in (0, "0", False) and ("restore" in str(node).casefold()): state = "BLOCKED"
                yield make_observation(system_id=system, resource_id=rid, record_type=str(node.get("record_type") or node.get("data_category") or collection_in_scope or "JSON_RECORD"), state=state, identifiers_seen=identifiers(node), evidence_id=evidence_id, observed_at=observed, source_detail=f"{path.name}:{location}")
            for key, child in node.items():
                yield from walk(child, f"{location}.{key}", observed, system_in_scope, collection_in_scope)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                yield from walk(child, f"{location}[{index}]", inherited_time, inherited_system, inherited_collection)
    yield from walk(value)
