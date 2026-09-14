from dataclasses import dataclass

@dataclass
class OccupancyRecord:
    timestamp: str
    city: str
    name_zh: str
    name_en: str
    facilities: dict
    website: str