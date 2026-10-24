"""Deletion-request intent classification and signal-agreement audit."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"
PROMPT = ROOT / "code" / "prompts" / "intent.md"

DELETION_RE = re.compile(
    r"(?i)(delete|delet|erase|erasure|remove (my|the) (account|profile|personal|data)|"
    r"close (my|the) account|exclus|elimin|suppression|supprim|削除|삭제|exclusão|"
    r"eliminación|suppression définitive)"
)
NON_DELETION_RE = re.compile(
    r"(?i)(don't delete|do not delete|not asking for deletion|not a request to erase|"
    r"keep (the )?(account|profile|records|data)|leave (the )?(account|profile|history)|"
    r"change (the )?(email|address|phone|number|name|surname)|correct (my|the |it)|"
    r"update (my|the )?(profile|email|phone|address|name)|replace (it|my|the )|reset (the )?"
    r"(login|password|profile)|download|copy|portable|invoice|marketing|"
    r"promotional|information request|continue using|still use|still need|do not close|don't close|without removing)"
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_email(value: str) -> str:
    return value.strip().casefold()


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: str
    signal: str
    reason: str
    llm_used: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class CachedIntentLLM:
    """Optional JSON-only LLM hook; no network call is made without a callback."""

    def __init__(self, callback: Callable[[str, str, float], str] | None = None, cache_dir: Path | None = None):
        self.callback = callback
        self.cache_dir = cache_dir or ROOT / "code" / "scratch" / "intent_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def classify(self, text: str) -> IntentResult:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cache_file = self.cache_dir / f"{digest}.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return IntentResult(data["intent"], data["confidence"], "llm", data["reason"], True)
        if self.callback is None:
            return IntentResult("AMBIGUOUS", "LOW", "llm-unavailable", "ambiguous text and no configured LLM callback", False)
        raw = self.callback(PROMPT.read_text(encoding="utf-8"), text, 0.0)
        data = json.loads(raw)
        if set(data) != {"intent", "confidence", "reason"}:
            raise ValueError("intent LLM response must contain exactly intent, confidence, reason")
        if data["intent"] not in {"DELETION", "NOT_APPLICABLE", "AMBIGUOUS"}:
            raise ValueError("invalid intent")
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return IntentResult(data["intent"], data["confidence"], "llm", data["reason"], True)


def classify_text(text: str, llm: CachedIntentLLM | None = None) -> IntentResult:
    deletion = bool(DELETION_RE.search(text or ""))
    non_deletion = bool(NON_DELETION_RE.search(text or ""))
    if non_deletion and not deletion:
        return IntentResult("NOT_APPLICABLE", "HIGH", "text", "explicit non-deletion/update/access/copy language")
    if deletion and not non_deletion:
        return IntentResult("DELETION", "HIGH", "text", "explicit deletion/erasure request")
    if deletion and non_deletion:
        # Explicit negation wins for common English forms.
        if re.search(r"(?i)(don't delete|do not delete|not asking for deletion|not a request to erase|do not close|don't close|without removing)", text):
            return IntentResult("NOT_APPLICABLE", "HIGH", "text", "explicitly negates deletion")
        if llm:
            return llm.classify(text)
        return IntentResult("AMBIGUOUS", "LOW", "text", "both deletion and non-deletion signals present")
    if llm:
        return llm.classify(text)
    return IntentResult("AMBIGUOUS", "LOW", "text", "no deletion intent signal recognized")


def _resource_identity_map(dataset_dir: Path) -> dict[str, set[str]]:
    """Recover evidence-backed resource -> user/email links for classifiers."""
    mapping: dict[str, set[str]] = {}
    for path in (dataset_dir / "evidence").rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in {".json", ".txt", ".log", ".sql"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        resources = set(re.findall(r"\baccount_\d+\b", text, re.I))
        for resource in resources:
            window = text[max(0, text.find(resource) - 250): text.find(resource) + 500]
            links = set(re.findall(r"\buser_\d+\b", window, re.I))
            links |= {normalize_email(x) for x in re.findall(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", window)}
            if links:
                mapping.setdefault(resource.casefold(), set()).update(links)
    return mapping


def primary_classification_signal(
    request: dict[str, str],
    resolved_user_id: str | None,
    resolved_emails: set[str],
    activities: list[dict[str, str]],
    resource_links: dict[str, set[str]],
) -> IntentResult:
    for activity in activities:
        if activity.get("event_type") != "CLASSIFY_REQUEST":
            continue
        resource = activity.get("resource_id", "").casefold()
        links = resource_links.get(resource, set())
        if resolved_user_id and resolved_user_id.casefold() in links:
            return IntentResult("NOT_APPLICABLE", "HIGH", "classify_activity", "CLASSIFY_REQUEST says non-deletion for linked resource")
        if resolved_emails & links:
            return IntentResult("NOT_APPLICABLE", "HIGH", "classify_activity", "CLASSIFY_REQUEST says non-deletion for linked resource")
    return IntentResult("UNKNOWN", "NONE", "classify_activity", "no linked CLASSIFY_REQUEST activity")


def audit_requests(dataset_dir: Path = DATASET, llm: CachedIntentLLM | None = None) -> dict:
    from identity import IdentityResolver
    resolver = IdentityResolver.from_dataset(dataset_dir)
    requests = rows(dataset_dir / "deletion_requests.csv")
    activities = rows(dataset_dir / "system_activity.csv")
    links = _resource_identity_map(dataset_dir)
    results = []
    for request in requests:
        identity = resolver.resolve_email(request["email"])
        primary = primary_classification_signal(request, identity.user_id, set(identity.emails), activities, links)
        secondary = classify_text(request["request_text"], llm)
        agreement = primary.intent == secondary.intent if primary.intent != "UNKNOWN" else None
        final = secondary.intent if secondary.intent != "AMBIGUOUS" else "NOT_APPLICABLE"
        results.append({
            "case_id": request["case_id"],
            "primary": primary.to_dict(),
            "secondary": secondary.to_dict(),
            "agreement": agreement,
            "final_intent": final,
            "output": {"case_id": request["case_id"], "deletion_status": final, "steps_json": [] if final == "NOT_APPLICABLE" else None},
        })
    both = [r for r in results if r["agreement"] is not None]
    return {
        "counts": {
            "total": len(results),
            "primary_non_deletion": sum(r["primary"]["intent"] == "NOT_APPLICABLE" for r in results),
            "primary_unknown": sum(r["primary"]["intent"] == "UNKNOWN" for r in results),
            "secondary_non_deletion": sum(r["secondary"]["intent"] == "NOT_APPLICABLE" for r in results),
            "secondary_deletion": sum(r["secondary"]["intent"] == "DELETION" for r in results),
            "secondary_ambiguous": sum(r["secondary"]["intent"] == "AMBIGUOUS" for r in results),
            "agreement_when_both_available": sum(r["agreement"] is True for r in both),
            "disagreement_when_both_available": sum(r["agreement"] is False for r in both),
        },
        "disagreements": [r for r in results if r["agreement"] is False],
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--email")
    args = parser.parse_args()
    if args.email:
        print(json.dumps(classify_text(args.email).to_dict(), indent=2))
    elif args.audit:
        print(json.dumps(audit_requests(), ensure_ascii=False, indent=2))
    else:
        parser.error("use --audit or --email")


if __name__ == "__main__":
    main()
