import sqlite3
from pathlib import Path
from .models import OccupancyRecord, FacilityReading

DB_PATH = Path("data/occupancy.db")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS occupancy_records (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                city TEXT NOT NULL,
                name_zh TEXT NOT NULL,
                name_en TEXT NOT NULL,
                facility TEXT NOT NULL,
                current INTEGER,
                capacity INTEGER
            )
        """)


def save_to_db(records: list[OccupancyRecord]) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.executemany("""
            INSERT INTO occupancy_records (
                timestamp,
                city,
                name_zh,
                name_en,
                facility,
                current,
                capacity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
                (
                    record.timestamp,
                    record.city,
                    record.name_zh,
                    record.name_en,
                    facility,
                    readings.current,
                    readings.capacity,
                )
            for record in records
            for facility, readings in record.facilities.items()
            ]
        )