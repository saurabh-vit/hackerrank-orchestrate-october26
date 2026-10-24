"""Generate the required output.csv from participant-facing dataset files."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from evaluation.main import _predict  # noqa: E402
from evidence.pipeline import _rows  # noqa: E402
from identity import IdentityResolver  # noqa: E402
from rules import load_rules  # noqa: E402


def main() -> None:
    dataset = ROOT / "dataset"
    requests = _rows(dataset / "deletion_requests.csv")
    activities = _rows(dataset / "system_activity.csv")
    resolver = IdentityResolver.from_dataset(dataset)
    rules = load_rules(dataset / "deletion_rules.csv")
    predictions = [_predict(row, resolver, rules, activities) for row in requests]
    predictions.sort(key=lambda row: row["case_id"])
    with (ROOT / "output.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", "deletion_status", "steps_json"])
        writer.writeheader()
        for row in predictions:
            writer.writerow({"case_id": row["case_id"], "deletion_status": row["deletion_status"], "steps_json": json.dumps(row["steps_json"], ensure_ascii=False, separators=(",", ":"))})
    print(f"wrote {len(predictions)} rows to output.csv")


if __name__ == "__main__":
    main()
