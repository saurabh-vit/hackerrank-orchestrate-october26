"""Deterministic current-and-historical identity resolution.

The resolver intentionally uses only participant-facing CSV files.  Email
matching is case-insensitive and trims surrounding whitespace.  Historical
audit rows are treated as bidirectional identity evidence: both old_value and
new_value belong to the row's user_id.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset"


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def normalize_phone(value: str) -> str:
    return value.strip().casefold()


def normalize_hash(value: str) -> str:
    return value.strip().casefold()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(frozen=True)
class Resolution:
    query_email: str
    normalized_email: str
    status: str
    user_id: str | None
    candidate_user_ids: tuple[str, ...] = ()
    matched_on: tuple[str, ...] = ()
    emails: tuple[str, ...] = ()
    phones: tuple[str, ...] = ()
    email_hashes: tuple[str, ...] = ()
    audit_ids: tuple[str, ...] = ()
    reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class IdentityResolver:
    """Indexes current identity snapshots and the complete audit history."""

    def __init__(
        self,
        identities: Iterable[dict[str, str]],
        audit_rows: Iterable[dict[str, str]],
    ) -> None:
        self.identities = list(identities)
        self.audit_rows = list(audit_rows)
        self._email_to_users: dict[str, set[str]] = {}
        self._identity_by_user: dict[str, dict[str, str]] = {}
        self._audits_by_user: dict[str, list[dict[str, str]]] = {}
        self._index_data()

    @classmethod
    def from_dataset(cls, dataset_dir: Path = DATASET) -> "IdentityResolver":
        return cls(
            read_csv(dataset_dir / "user_identities.csv"),
            read_csv(dataset_dir / "user_audit_log.csv"),
        )

    def _add_email(self, value: str, user_id: str) -> None:
        if value:
            self._email_to_users.setdefault(normalize_email(value), set()).add(user_id)

    def _index_data(self) -> None:
        for row in self.identities:
            user_id = row["user_id"]
            self._identity_by_user[user_id] = row
            self._add_email(row.get("email", ""), user_id)
        for row in self.audit_rows:
            user_id = row["user_id"]
            self._audits_by_user.setdefault(user_id, []).append(row)
            if row.get("field_name", "").casefold() == "email":
                self._add_email(row.get("old_value", ""), user_id)
                self._add_email(row.get("new_value", ""), user_id)
        for rows in self._audits_by_user.values():
            rows.sort(key=lambda row: (row.get("event_time", ""), row["audit_id"]))

    def _history(self, user_id: str) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
        emails: set[str] = set()
        phones: set[str] = set()
        hashes: set[str] = set()
        audit_ids: list[str] = []
        current = self._identity_by_user.get(user_id)
        if current:
            if current.get("email"):
                emails.add(normalize_email(current["email"]))
            if current.get("phone"):
                phones.add(normalize_phone(current["phone"]))
            if current.get("email_hash"):
                hashes.add(normalize_hash(current["email_hash"]))
        for row in self._audits_by_user.get(user_id, []):
            audit_ids.append(row["audit_id"])
            field_name = row.get("field_name", "").casefold()
            old_value = row.get("old_value", "")
            new_value = row.get("new_value", "")
            if field_name == "email":
                emails.update(x for x in (normalize_email(old_value), normalize_email(new_value)) if x)
            elif field_name == "phone":
                phones.update(x for x in (normalize_phone(old_value), normalize_phone(new_value)) if x)
            elif field_name == "email_hash":
                hashes.update(x for x in (normalize_hash(old_value), normalize_hash(new_value)) if x)
        return tuple(sorted(emails)), tuple(sorted(phones)), tuple(sorted(hashes)), tuple(audit_ids)

    def resolve_email(self, email: str) -> Resolution:
        normalized = normalize_email(email)
        candidates = tuple(sorted(self._email_to_users.get(normalized, set())))
        if not normalized:
            return Resolution(email, normalized, "unresolved", None, reason="empty email after trimming")
        if not candidates:
            return Resolution(email, normalized, "unresolved", None, reason="email absent from current and audited email values")
        if len(candidates) > 1:
            return Resolution(
                email,
                normalized,
                "ambiguous",
                None,
                candidates,
                reason="normalized email maps to multiple user_ids",
            )
        user_id = candidates[0]
        current = self._identity_by_user.get(user_id, {})
        matched_on: list[str] = []
        if normalize_email(current.get("email", "")) == normalized:
            matched_on.append("current.email")
        for row in self._audits_by_user.get(user_id, []):
            if row.get("field_name", "").casefold() == "email" and normalized in {
                normalize_email(row.get("old_value", "")),
                normalize_email(row.get("new_value", "")),
            }:
                matched_on.append(f"audit:{row['audit_id']}")
        emails, phones, hashes, audit_ids = self._history(user_id)
        return Resolution(
            email,
            normalized,
            "resolved",
            user_id,
            candidates,
            tuple(matched_on),
            emails,
            phones,
            hashes,
            audit_ids,
            reason="unique current or historical email match",
        )

    def resolve_requests(self, requests: Iterable[dict[str, str]]) -> list[Resolution]:
        return [self.resolve_email(row.get("email", "")) for row in requests]

    def duplicate_email_values(self) -> dict[str, tuple[tuple[str, ...], ...]]:
        """Return normalized email values repeated within one user's history.

        Repeated current/new values are legitimate audit-chain duplicates and
        are reported separately from cross-user ambiguity.
        """
        values: dict[str, list[tuple[str, str]]] = {}
        for user_id, row in self._identity_by_user.items():
            values.setdefault(normalize_email(row.get("email", "")), []).append((user_id, "current"))
        for row in self.audit_rows:
            if row.get("field_name", "").casefold() == "email":
                for kind in ("old_value", "new_value"):
                    value = normalize_email(row.get(kind, ""))
                    if value:
                        values.setdefault(value, []).append((row["user_id"], f"{row['audit_id']}:{kind}"))
        return {
            value: tuple(tuple(item) for item in occurrences)
            for value, occurrences in sorted(values.items())
            if len(occurrences) > 1
        }


def audit_requests(dataset_dir: Path = DATASET) -> dict:
    resolver = IdentityResolver.from_dataset(dataset_dir)
    requests = read_csv(dataset_dir / "deletion_requests.csv")
    results = []
    for row in requests:
        result = resolver.resolve_email(row.get("email", ""))
        results.append({"case_id": row["case_id"], **result.to_dict()})
    counts = {
        "total": len(results),
        "resolved": sum(r["status"] == "resolved" for r in results),
        "unresolved": sum(r["status"] == "unresolved" for r in results),
        "ambiguous": sum(r["status"] == "ambiguous" for r in results),
    }
    request_email_groups: dict[str, list[str]] = {}
    for row in requests:
        request_email_groups.setdefault(normalize_email(row.get("email", "")), []).append(row["case_id"])
    duplicate_request_emails = {
        email: tuple(case_ids)
        for email, case_ids in sorted(request_email_groups.items())
        if len(case_ids) > 1
    }
    duplicate_history = resolver.duplicate_email_values()
    cross_user_duplicates = {
        email: occurrences
        for email, occurrences in duplicate_history.items()
        if len({item[0] for item in occurrences}) > 1
    }
    return {
        "counts": counts,
        "duplicate_request_emails": duplicate_request_emails,
        "duplicate_history_email_values": duplicate_history,
        "cross_user_duplicate_history_email_values": cross_user_duplicates,
        "non_resolved": [r for r in results if r["status"] != "resolved"],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true", help="audit all deletion requests")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--email", help="resolve one email and print JSON")
    args = parser.parse_args()
    resolver = IdentityResolver.from_dataset(args.dataset)
    if args.email is not None:
        print(json.dumps(resolver.resolve_email(args.email).to_dict(), ensure_ascii=False, indent=2))
        return
    if args.audit:
        print(json.dumps(audit_requests(args.dataset), ensure_ascii=False, indent=2))
        return
    parser.error("use --audit or --email")


if __name__ == "__main__":
    main()
