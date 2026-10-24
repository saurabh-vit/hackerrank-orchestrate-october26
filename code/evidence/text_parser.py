from __future__ import annotations
import re
from pathlib import Path
from .common import identifiers, parse_time, state_from
from . import make_observation

LINE = re.compile(r"^\s*-\s*(?P<time>\S+)\s*\|\s*(?P<system>[^|]+)\|\s*(?P<resource>[^|]+)\|\s*(?P<type>[^|]+)\|\s*(?P<state>[^|]+)\|\s*(?P<subject>.+?)\s*$")

def parse_text(path: Path, evidence_id: str, origin: str = "", captured_at: str = ""):
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = LINE.match(line)
        if not match:
            continue
        data = match.groupdict()
        subject = data["subject"].strip()
        yield make_observation(system_id=data["system"].strip() or origin, resource_id=data["resource"].strip(), record_type=data["type"].strip(), state=state_from(data["state"]), identifiers_seen=identifiers(subject), evidence_id=evidence_id, observed_at=parse_time(data["time"]) or captured_at, source_detail=f"{path.name}:line={line_no}")
