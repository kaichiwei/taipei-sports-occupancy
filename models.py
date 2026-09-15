from dataclasses import dataclass


@dataclass
class FacilityReading:
    current: int | None
    capacity: int | None

@dataclass
class OccupancyRecord:
    timestamp: str
    city: str
    name_zh: str
    name_en: str
    facilities: dict[str, FacilityReading]
    website: str