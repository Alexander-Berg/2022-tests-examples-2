import dataclasses
import datetime as dt
from typing import List


@dataclasses.dataclass
class GeoHierarchyDb:
    park_id: str
    driver_id: str
    geo_hierarchy_hash: int
    updated_at: dt.datetime


@dataclasses.dataclass
class GeoHierarchyOutboxDb:
    park_id: str
    driver_id: str
    geo_hierarchy: List[str]
    updated_at: dt.datetime
