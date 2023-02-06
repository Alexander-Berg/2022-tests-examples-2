"""
    Structure for point object
"""

import dataclasses
from typing import List


@dataclasses.dataclass
class Point:
    lon: float
    lat: float

    def to_list(self) -> List[float]:
        return [self.lon, self.lat]

    @classmethod
    def from_list(cls, coordinates: List[float]):
        return cls(lon=coordinates[0], lat=coordinates[1])
