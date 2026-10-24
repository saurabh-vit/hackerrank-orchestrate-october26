from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from .common import identifiers, parse_time, resource_ids
from . import make_observation

def pdf_text(path: Path) -> str:
    if shutil.which("pdftotext"):
        result = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=False)
        if result.returncode == 0: return result.stdout
    try:
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    except Exception:
        return ""

def parse_pdf(path: Path, evidence_id: str, origin: str = "", captured_at: str = ""):
    text = pdf_text(path)
    ids = identifiers(text)
    resources = resource_ids(text)
    record_type = "SUPPORT_ATTACHMENT" if "attachment" in f"{path.name} {text}".casefold() else "PDF_DOCUMENT"
    for rid in resources or ("",):
        yield make_observation(system_id=origin or "document", resource_id=rid, record_type=record_type, state="PRESENT", identifiers_seen=ids, evidence_id=evidence_id, observed_at=captured_at, source_detail=f"{path.name}:pdftotext")
