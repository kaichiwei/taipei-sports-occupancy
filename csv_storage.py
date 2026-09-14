import csv

from typing import Iterator
from pathlib import Path
from collections import defaultdict


FIELDNAMES = ["timestamp", "city", "name_zh", "name_en", "facility", "current", "capacity"]

def to_rows(record: dict) -> Iterator[dict]:
    base = {k: record[k] for k in ("timestamp", "city", "name_zh", "name_en")}
    for facility, (cur, cap) in record["facilities"].items():
        yield {**base, "facility": facility, "current": cur, "capacity": cap}


def save_to_csv(records: list[dict]) -> None:
    rows_by_path = defaultdict(list)
    for record in records:
        csv_path = Path("data") / f"log_{record["timestamp"][:7]}.csv"
        for row in to_rows(record):
            if row["current"] is not None:
                rows_by_path[csv_path].append(row)

    Path("data").mkdir(parents=True, exist_ok=True)
    for csv_path, rows in rows_by_path.items():
        new_csv = not csv_path.exists() or csv_path.stat().st_size == 0
        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            if new_csv:
                writer.writeheader()
            writer.writerows(rows)