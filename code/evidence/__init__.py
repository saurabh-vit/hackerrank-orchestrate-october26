"""Evidence parsing and case-scoped observation normalization."""
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Observation:
    system_id: str
    resource_id: str
    record_type: str
    state: str
    identifiers_seen: tuple[str, ...]
    evidence_id: str
    observed_at: str
    source_detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_observation(**kwargs: Any) -> Observation:
    kwargs["identifiers_seen"] = tuple(sorted(set(kwargs.get("identifiers_seen", ()))))
    return Observation(**kwargs)
