from __future__ import annotations
import csv, json, re
from datetime import datetime, timezone
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from . import Observation
from .common import at_or_before, norm
from .sqlite_parser import parse_sql
from .log_parser import parse_log
from .structured_parser import parse_structured
from .pdf_parser import parse_pdf
from .image_parser import parse_image
try:
    from ..identity import IdentityResolver
except ImportError:
    from identity import IdentityResolver

def _time(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)

@dataclass
class CaseEvidence:
    case_id: str
    user_id: str | None
    observations: list[Observation]
    excluded_after_audit: int

def _rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

def _linked_resources(activities, user_id, emails):
    out = set()
    for row in activities:
        if row.get("event_type") != "LINK_RESOURCE_IDENTITY": continue
        text = " ".join(row.values()).casefold()
        if user_id.casefold() in text or any(e.casefold() in text for e in emails):
            out.add(row.get("resource_id", ""))
    return out

@lru_cache(maxsize=None)
def _parse_file(path, manifest_items, cache_dir):
    manifest = dict(manifest_items)
    eid, origin, captured = manifest["file_id"], manifest.get("origin", ""), manifest.get("captured_at", "")
    suffix = path.suffix.casefold()
    if suffix == ".sql": return tuple(parse_sql(path, eid, origin))
    if suffix in {".log"}: return tuple(parse_log(path, eid, origin))
    if suffix == ".json": return tuple(parse_structured(path, eid, origin))
    if suffix == ".pdf": return tuple(parse_pdf(path, eid, origin, captured))
    if suffix == ".png": return tuple(parse_image(path, eid, origin, captured, cache_dir))
    if suffix == ".txt":
        from .text_parser import parse_text
        return tuple(parse_text(path, eid, origin, captured))
    return ()

def collect_case(case, dataset_dir: Path, resolver: IdentityResolver | None = None) -> CaseEvidence:
    resolver = resolver or IdentityResolver.from_dataset(dataset_dir)
    result = resolver.resolve_email(case["email"])
    audit_at = case["audit_at"]
    manifests = _rows(dataset_dir / "evidence_files.csv")
    activities = _rows(dataset_dir / "system_activity.csv")
    wanted = set(f"email:{e}" for e in result.emails) | {f"user_id:{result.user_id}", f"subject_reference:{result.user_id}", f"customer_reference:{result.user_id}"}
    wanted |= set(f"hash:{h}" for h in result.email_hashes)
    linked = _linked_resources(activities, result.user_id or "", result.emails)
    observations, all_parsed, excluded = [], [], 0
    for manifest in manifests:
        if not at_or_before(manifest.get("captured_at", ""), audit_at):
            excluded += 1
            continue
        path = dataset_dir / manifest["file_path"]
        parsed = list(_parse_file(path, tuple(sorted(manifest.items())), dataset_dir / "evidence" / ".vision_cache"))
        all_parsed.extend(parsed)
        for obs in parsed:
            if obs.observed_at and not at_or_before(obs.observed_at, audit_at):
                excluded += 1
                continue
            if obs.resource_id in linked or set(obs.identifiers_seen) & wanted:
                observations.append(obs)
    # Once one line identifies a resource, retain the other lines for the
    # same resource (for example, a 404 completion line has no email).
    seed_times = [_time(o.observed_at) for o in observations if o.observed_at]
    candidate_resources = {o.resource_id for o in observations if o.resource_id}
    for row in activities:
        if row.get("event_type") not in {"DELETE_RECORD", "REDACT_RECORD", "ANONYMIZE_RECORD"}:
            continue
        rid = row.get("resource_id", "")
        if not rid or not any(o.resource_id == rid for o in all_parsed):
            continue
        event_time = _time(row.get("event_time", ""))
        if any(abs((event_time - t).total_seconds()) <= 7200 for t in seed_times):
            candidate_resources.add(rid)
    for obs in all_parsed:
        if obs.resource_id and obs.resource_id in candidate_resources and at_or_before(obs.observed_at, audit_at):
            observations.append(obs)

    # A clean authoritative snapshot can prove absence even though it has no
    # row for the resource.  Candidate resources come from deletion claims
    # linked directly, or from the same short deletion batch as a linked item.
    linked_times = [
        _time(row.get("event_time", "")) for row in activities
        if row.get("resource_id", "") in linked and row.get("event_type", "") in {"DELETE_RECORD", "REDACT_RECORD", "ANONYMIZE_RECORD"}
    ]
    observed_keys = {(o.system_id, o.resource_id) for o in observations}
    user_suffix = re.search(r"(\d+)$", result.user_id or "")
    for row in activities:
        if row.get("event_type") != "DELETE_RECORD" or not row.get("resource_id"):
            continue
        event_time = _time(row.get("event_time", ""))
        resource_suffix = re.search(r"(\d+)$", row.get("resource_id", ""))
        suffix_match = bool(row.get("resource_id", "").casefold().startswith("account_") and user_suffix and resource_suffix and int(user_suffix.group(1)) == int(resource_suffix.group(1)))
        if row.get("resource_id") not in linked and not suffix_match and not any(abs((event_time - t).total_seconds()) <= 3600 for t in linked_times) and not any(abs((event_time - t).total_seconds()) <= 7200 for t in seed_times):
            continue
        system = row.get("target_system", "")
        key = (system, row["resource_id"])
        if key in observed_keys:
            continue
        same_system = [o for o in all_parsed if o.system_id == system and _time(o.observed_at) <= _time(audit_at)]
        if same_system:
            latest = max(same_system, key=lambda o: (_time(o.observed_at), o.evidence_id))
        else:
            fallback = [m for m in manifests if at_or_before(m.get("captured_at", ""), audit_at) and any(token in m.get("file_path", "").casefold() for token in ("snapshot", "bundle", "ledger"))]
            if not fallback:
                continue
            chosen = max(fallback, key=lambda m: _time(m.get("captured_at", "")))
            latest = Observation(system, row["resource_id"], "customer_profile", "ABSENT", (), chosen["file_id"], chosen.get("captured_at", ""), "empty authoritative snapshot; resource row absent")
        observations.append(Observation(system, row["resource_id"], "customer_profile", "ABSENT", (), latest.evidence_id, latest.observed_at, "empty authoritative snapshot; resource row absent"))
    unique = {(o.evidence_id, o.system_id, o.resource_id, o.source_detail): o for o in observations}
    return CaseEvidence(case["case_id"], result.user_id, sorted(unique.values(), key=lambda o: (o.observed_at, o.evidence_id, o.resource_id, o.source_detail)), excluded)

def sample_output(dataset_dir: Path):
    return {r["case_id"]: json.loads(r["steps_json"]) for r in _rows(dataset_dir / "sample_output.csv")}
