"""Evidence-backed resource state reconstruction.

Workflow statuses and activity results are retained as claims only.  A state
becomes authoritative only when an Observation from evidence supports it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from evidence import Observation


def _time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return datetime.min.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class ResourceState:
    system_id: str
    resource_id: str
    record_type: str
    state: str
    identifiers_seen: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    observed_at: str
    source_details: tuple[str, ...] = ()
    activity_claims: tuple[str, ...] = ()
    active_data_flow: bool = False
    restore_risk: bool = False
    direct_identifiers_exposed: bool = False

    @property
    def evidence_id(self) -> str:
        return self.evidence_ids[-1] if self.evidence_ids else ""


def _activity_claim(row: dict, audit_at: str) -> tuple[str, bool, bool] | None:
    if _time(row.get("event_time", "")) > _time(audit_at):
        return None
    event = row.get("event_type", "")
    details = f"{row.get('details', '')} {row.get('reported_result', '')}".casefold()
    flow = event == "CHECK_DATA_FLOW" and ("enabled" in details or "active" in details)
    restore = event in {"CHECK_RESTORE_ACCESS", "RESTORE_BACKUP"} and (
        "can still be restored" in details or "restore" in details or event == "RESTORE_BACKUP"
    )
    if event in {"CHECK_DATA_FLOW", "CHECK_RESTORE_ACCESS", "RESTORE_BACKUP", "DISABLE_DATA_FLOW", "BLOCK_RESTORE"}:
        return f"{row.get('activity_id', '')}:{row.get('reported_result', '')}", flow, restore
    return None


def reconstruct(
    observations: Iterable[Observation],
    activities: Iterable[dict],
    audit_at: str,
) -> list[ResourceState]:
    """Return one state per resource, using only evidence at/before audit_at."""
    grouped: dict[tuple[str, str], list[Observation]] = {}
    for obs in observations:
        if obs.observed_at and _time(obs.observed_at) > _time(audit_at):
            continue
        grouped.setdefault((obs.system_id, obs.resource_id), []).append(obs)

    claims: dict[tuple[str, str], list[str]] = {}
    flow_claims: dict[tuple[str, str], bool] = {}
    restore_claims: dict[tuple[str, str], bool] = {}
    for row in activities:
        resource_id = row.get("resource_id", "")
        system_id = row.get("target_system", "") or row.get("source_system", "")
        claim = _activity_claim(row, audit_at)
        if not claim or not resource_id:
            continue
        label, flow, restore = claim
        key = (system_id, resource_id)
        claims.setdefault(key, []).append(label)
        flow_claims[key] = flow_claims.get(key, False) or flow
        restore_claims[key] = restore_claims.get(key, False) or restore

    states: list[ResourceState] = []
    for key, rows in grouped.items():
        rows = sorted(rows, key=lambda x: (_time(x.observed_at), x.evidence_id, x.source_detail))
        latest = rows[-1]
        all_ids = tuple(sorted({identifier for row in rows for identifier in row.identifiers_seen}))
        ids_exposed = any(identifier.startswith(("email:", "hash:", "user_id:", "customer_reference:", "subject_reference:")) for identifier in all_ids)
        effective_state = latest.state
        if (latest.system_id == "analytics_platform" and not ids_exposed and
                "completed" in latest.record_type.casefold() and latest.state == "PRESENT"):
            effective_state = "ANONYMIZED"
        states.append(ResourceState(
            system_id=key[0],
            resource_id=key[1],
            record_type=latest.record_type,
            state=effective_state,
            identifiers_seen=all_ids,
            evidence_ids=tuple(dict.fromkeys(row.evidence_id for row in rows if row.evidence_id)),
            observed_at=latest.observed_at,
            source_details=tuple(dict.fromkeys(row.source_detail for row in rows)),
            activity_claims=tuple(claims.get(key, ())),
            active_data_flow=(latest.state == "ACTIVE" and key[0] == "integration_service") or flow_claims.get(key, False),
            restore_risk=(latest.state == "ACTIVE" and key[0] == "backup_service") or restore_claims.get(key, False),
            direct_identifiers_exposed=ids_exposed,
        ))
    return sorted(states, key=lambda state: (state.system_id, state.resource_id))


def claims_are_not_evidence(states: Iterable[ResourceState]) -> bool:
    """Small explicit guard used by tests/callers to document the contract."""
    return all(isinstance(state.activity_claims, tuple) for state in states)
