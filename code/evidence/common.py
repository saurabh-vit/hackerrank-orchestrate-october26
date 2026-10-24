from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Any

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b")
HASH_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
RESOURCE_RE = re.compile(r"\b(?:account|search|support|export|analytics|data_flow|backup|audit_record|tombstone|object|marketing|customer_export)_\d+\b")
USER_RE = re.compile(r"\buser_\d+\b")

def norm(value: Any) -> str:
    return str(value).strip().casefold()

def values_from_any(value: Any) -> list[str]:
    if isinstance(value, dict):
        out = []
        for k, v in value.items():
            if isinstance(v, (str, int, float, bool)) and v not in ("", None):
                out.append(f"{k}={v}")
            out.extend(values_from_any(v))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(values_from_any(item))
        return out
    return [str(value)] if value not in ("", None) else []

def identifiers(value: Any) -> tuple[str, ...]:
    text = " ".join(values_from_any(value))
    found = {f"email:{norm(x)}" for x in EMAIL_RE.findall(text)}
    found |= {f"hash:{norm(x)}" for x in HASH_RE.findall(text)}
    found |= {f"user_id:{norm(x)}" for x in USER_RE.findall(text)}
    for key in ("customer_reference", "subject_reference", "user_id"):
        for match in re.findall(rf"(?i)\b{key}\s*[:=]\s*[\"']?([A-Za-z0-9_.@+\-]+)", text):
            found.add(f"{key.casefold()}:{norm(match)}")
    return tuple(sorted(found))

def resource_ids(value: Any) -> tuple[str, ...]:
    return tuple(sorted(set(RESOURCE_RE.findall(" ".join(values_from_any(value))))))

def parse_time(value: Any) -> str:
    if not value:
        return ""
    text = str(value).strip()
    return text.replace(" ", "T", 1) if "T" not in text and len(text) >= 19 else text

def at_or_before(value: str, cutoff: str) -> bool:
    if not value or not cutoff:
        return True
    try:
        a = datetime.fromisoformat(value.replace("Z", "+00:00"))
        b = datetime.fromisoformat(cutoff.replace("Z", "+00:00"))
        if a.tzinfo is None: a = a.replace(tzinfo=timezone.utc)
        if b.tzinfo is None: b = b.replace(tzinfo=timezone.utc)
        return a <= b
    except ValueError:
        return True

def state_from(value: Any, default: str = "PRESENT") -> str:
    text = norm(value)
    if text in {"not_found", "absent", "missing", "deleted", "gone"}: return "ABSENT"
    if text in {"redacted", "redact"}: return "REDACTED"
    if text in {"anonymized", "anonymised"}: return "ANONYMIZED"
    if text in {"active", "enabled", "true", "found", "present", "identifiable", "success", "hit"}: return "ACTIVE" if text in {"active", "enabled", "true"} else "PRESENT"
    if text in {"disabled", "stopped", "false"}: return "DISABLED"
    if text in {"blocked", "block"}: return "BLOCKED"
    return default
