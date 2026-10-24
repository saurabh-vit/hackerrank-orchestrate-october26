"""Deletion policy loading and category/condition evaluation."""
from __future__ import annotations
import csv
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    rule_id: str
    data_category: str
    condition: str
    required_action: str


@dataclass(frozen=True)
class PolicyDecision:
    rule_id: str
    data_category: str
    required_action: str
    condition_met: bool
    rationale: str


def load_rules(path: Path) -> list[Rule]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [Rule(**row) for row in csv.DictReader(handle)]


def category_for(system_id: str, record_type: str, resource_id: str = "") -> str:
    text = f"{system_id} {record_type} {resource_id}".casefold()
    if any(token in text for token in ("contact_query", "deletion_marker", "profile_lookup")):
        return "SECONDARY_IDENTIFIER"
    if "tombstone" in text or "account_tombstone" in text: return "ACCOUNT_TOMBSTONE"
    if "security" in text or "audit_record" in text: return "SECURITY_AUDIT_LOG"
    if "legal" in text or "hold" in text: return "LEGAL_HOLD_RECORD"
    if "backup" in text: return "BACKUP_ARCHIVE"
    if "data_flow" in text or "connector" in text: return "DATA_FLOW"
    if "cache" in text: return "CACHE_ENTRY"
    if "search" in text or "index" in text: return "SEARCH_INDEX_ENTRY"
    if "export" in text: return "USER_EXPORT"
    if "marketing" in text: return "MARKETING_PROFILE"
    if "support_attachment" in text or "attachment" in text: return "SUPPORT_ATTACHMENT"
    if "support" in text or "support_message" in text: return "SUPPORT_MESSAGE"
    if "email_delivery" in text or "delivery_log" in text: return "EMAIL_DELIVERY_LOG"
    if "telemetry" in text or "event" in text: return "PRODUCT_TELEMETRY"
    if "analytic" in text: return "ANALYTICS_PROFILE"
    if "profile" in text or "account" in text: return "USER_PROFILE"
    return "SECONDARY_IDENTIFIER"


def _within_retention(state, now: str | None) -> bool:
    matches = re.search(r"retention_until[=:]([0-9TZ:.\-+]+)", " ".join(state.source_details), re.I)
    if not matches or not now:
        return True
    try:
        expiry = datetime.fromisoformat(matches.group(1).replace("Z", "+00:00"))
        current = datetime.fromisoformat(now.replace("Z", "+00:00"))
        return current <= expiry
    except ValueError:
        return True


def decide(rule_rows: Iterable[Rule], state, *, legal_hold_active: bool = False, now: str | None = None) -> PolicyDecision:
    category = category_for(state.system_id, state.record_type, state.resource_id)
    matching = [rule for rule in rule_rows if rule.data_category == category]
    if category == "DATA_FLOW":
        return PolicyDecision("contract_flow", category, "DISABLE", True, "active data flows must be disabled before dependent changes")
    if not matching:
        return PolicyDecision("unmapped", category, "REVIEW", False, "no deletion_rules.csv row matched this resource")
    rule = matching[0]
    condition = rule.condition.casefold()
    if category == "LEGAL_HOLD_RECORD":
        met = legal_hold_active
    elif category == "SECURITY_AUDIT_LOG":
        met = _within_retention(state, now)
    elif category == "BACKUP_ARCHIVE":
        met = True
    elif category == "SUPPORT_MESSAGE":
        met = True
    elif category == "SUPPORT_ATTACHMENT":
        met = "belongs only" in condition or "attachment" in state.record_type.casefold()
    elif category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY"}:
        met = state.direct_identifiers_exposed
    elif "always" in condition:
        met = True
    else:
        met = True
    return PolicyDecision(rule.rule_id, category, rule.required_action if met else "RETAIN", met, rule.condition)
