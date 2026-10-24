from __future__ import annotations
import re
import sqlite3
from pathlib import Path
from .common import identifiers, parse_time, resource_ids, state_from
from . import make_observation

def parse_sql(path: Path, evidence_id: str, manifest_origin: str = ""):
    text = path.read_text(encoding="utf-8", errors="replace")
    captured = (re.search(r"Captured at:\s*([0-9TZ:.\-+]+)", text, re.I) or [None, ""])[1]
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(text)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        scope = {}
        if "snapshot_scope" in tables:
            for row in conn.execute("SELECT * FROM snapshot_scope"):
                scope[str(row[0])] = str(row[1])
        for table in tables:
            if table == "snapshot_scope" or table.startswith("sqlite_"):
                continue
            columns = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]
            for row in conn.execute(f'SELECT * FROM "{table}"'):
                data = dict(zip(columns, row))
                rid = str(data.get("resource_id") or "")
                if not rid:
                    continue
                system = str(data.get("origin_system") or data.get("system") or scope.get(table, "") or "")
                if not system:
                    table_systems = (
                        ("account_service", ("profile", "account")),
                        ("search_service", ("search",)),
                        ("analytics_platform", ("analytic", "telemetry")),
                        ("support_platform", ("support",)),
                        ("export_service", ("export",)),
                        ("integration_service", ("connector", "subscription", "flow")),
                        ("backup_service", ("backup",)),
                        ("security_service", ("security", "audit")),
                    )
                    system = next((name for name, needles in table_systems if any(n in table.casefold() for n in needles)), manifest_origin or table.split("_")[0])
                observed = next((parse_time(data.get(k)) for k in ("observed_at", "updated_at", "captured_at") if data.get(k)), captured)
                raw_state = next((data.get(k) for k in ("state", "result", "status", "account_status", "restore_allowed", "enabled") if k in data), None)
                state = state_from(raw_state)
                if raw_state in (1, "1", True) and "restore" in table: state = "ACTIVE"
                if raw_state in (0, "0", False) and ("restore" in table or "connector" in table): state = "BLOCKED" if "restore" in table else "DISABLED"
                yield make_observation(system_id=system, resource_id=rid, record_type=str(data.get("record_type") or data.get("collection_name") or table), state=state, identifiers_seen=identifiers(data), evidence_id=evidence_id, observed_at=observed, source_detail=f"{path.name}:table={table}")
    finally:
        conn.close()
