from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable
from .common import identifiers, resource_ids
from . import make_observation

VisionCall = Callable[[bytes], str]

def _cache_text(content: bytes, cache_dir: Path, call: VisionCall | None) -> tuple[str, str]:
    digest = hashlib.sha256(content).hexdigest()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{digest}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8")).get("text", ""), "vision-cache"
    if call is None:
        return "", "vision-unavailable"
    text = call(content)
    cache_file.write_text(json.dumps({"sha256": digest, "text": text}, ensure_ascii=False), encoding="utf-8")
    return text, "vision-llm"

def parse_image(path: Path, evidence_id: str, origin: str = "", captured_at: str = "", cache_dir: Path | None = None, vision_call: VisionCall | None = None):
    content = path.read_bytes()
    ocr_text, method = "", "tesseract"
    if shutil.which("tesseract"):
        result = subprocess.run(["tesseract", str(path), "stdout"], capture_output=True, text=True, check=False)
        if result.returncode == 0: ocr_text = result.stdout
    ids = identifiers(ocr_text)
    resources = resource_ids(ocr_text)
    if not ids and not resources:
        ocr_text, method = _cache_text(content, cache_dir or path.parent / ".vision_cache", vision_call)
        ids, resources = identifiers(ocr_text), resource_ids(ocr_text)
    for rid in resources or ("",):
        yield make_observation(system_id=origin or "image", resource_id=rid, record_type="IMAGE_SCREENSHOT", state="PRESENT", identifiers_seen=ids, evidence_id=evidence_id, observed_at=captured_at, source_detail=f"{path.name}:{method}")
