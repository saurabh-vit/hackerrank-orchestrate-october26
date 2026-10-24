"""Audit evaluation/usage reports against executable artifacts; scratch-only."""
from __future__ import annotations
import csv, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
from evaluation.main import evaluate

def main():
    report = (ROOT / "code/evaluation/evaluation_report.md").read_text(encoding="utf-8")
    usage = (ROOT / "code/evaluation/usage_report.md").read_text(encoding="utf-8")
    m = evaluate()
    expected = {r["case_id"]: r["deletion_status"] for r in csv.DictReader((ROOT/"dataset/sample_output.csv").open(encoding="utf-8"))}
    actual = {k: v["deletion_status"] for k, v in m["actual"].items()}
    matrix = Counter((expected[k], actual[k]) for k in expected)
    print("RECOMPUTED_METRICS", json.dumps({"cases":m["cases"],"status":m["case_status_accuracy"],"row":m["row_exact_match"],"step_f1":m["step_f1"],"sequence":m["sequence_accuracy"],"fields":m["field_accuracy"]}, sort_keys=True))
    print("CONFUSION", json.dumps({f"{a}->{b}": n for (a,b),n in sorted(matrix.items())}, sort_keys=True))
    print("REPORT_HAS_CONFUSION_MATRIX", bool(re.search(r"confusion", report, re.I)))
    print("REPORT_HAS_FAILURES_SECTION", bool(re.search(r"^##? .*failures|failures found", report, re.I|re.M)))
    print("CUSTOM", subprocess.run([sys.executable, str(ROOT/"code/evaluation/custom_cases/custom_eval.py")], capture_output=True, text=True).stdout.strip())
    print("USAGE_ZERO_FIELDS", all(re.search(rf"\| {re.escape(x)} \| 0", usage) for x in ("LLM calls", "Vision LLM calls", "Input tokens", "Output tokens", "Total tokens")))
    print("CACHE_DIRS", [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_dir() and ("cache" in p.name.casefold() or p.name==".vision_cache")])

if __name__ == "__main__": main()
