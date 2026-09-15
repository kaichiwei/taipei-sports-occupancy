import csv

from typing import Iterator
from pathlib import Path
from collections import defaultdict

from .models import OccupancyRecord, FacilityReading

FIELDNAMES = ["timestamp", "city", "name_zh", "name_en", "facility", "current", "capacity"]

def to_rows(record: OccupancyRecord) -> Iterator[dict]:
    base = {
        "timestamp": record.timestamp,
        "city": record.city,
        "name_zh": record.name_zh,
        "name_en": record.name_en
    }
    for facility, reading in record.facilities.items():
        yield {
            **base, 
            "facility": facility, 
            "current": reading.current, 
            "capacity": reading.capacity
        }


def save_to_csv(records: list[OccupancyRecord]) -> None:
    rows_by_path = defaultdict(list)
    for record in records:
        csv_path = Path("data") / f"log_{record.timestamp[:7]}.csv"
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