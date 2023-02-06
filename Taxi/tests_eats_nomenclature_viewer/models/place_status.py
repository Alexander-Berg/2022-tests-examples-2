# pylint: disable=C5521

import dataclasses
import datetime as dt
from enum import Enum
from typing import Optional

from tests_eats_nomenclature_viewer.models.base import BaseObject
from tests_eats_nomenclature_viewer.models.base import StrGenerator


class PlaceTaskType(Enum):
    AVAILABILITY = 'availability'
    PRICE = 'price'
    STOCK = 'stock'
    VENDOR_DATA = 'vendor_data'


@dataclasses.dataclass
class PlaceFallbackFile(BaseObject):
    place_id: int
    task_type: PlaceTaskType
    file_path: str
    file_datetime: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceFallbackFile'):
        return (self.place_id, self.task_type) < (
            other.place_id,
            other.task_type,
        )


@dataclasses.dataclass
class PlaceAvailabilityFile(BaseObject):
    place_id: int
    file_path: str = dataclasses.field(
        default_factory=StrGenerator('availability/path_', '.json').__next__,
    )
    file_datetime: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceAvailabilityFile'):
        return self.place_id < other.place_id


@dataclasses.dataclass
class PlaceTaskStatus(BaseObject):
    place_id: int
    task_type: PlaceTaskType
    task_started_at: Optional[dt.datetime] = None
    task_is_in_progress: bool = False
    task_finished_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceTaskStatus'):
        return (self.place_id, self.task_type) < (
            other.place_id,
            other.task_type,
        )


@dataclasses.dataclass
class PlaceEnrichmentStatus(BaseObject):
    place_id: int
    are_prices_ready: bool
    are_stocks_ready: bool
    is_vendor_data_ready: bool
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceEnrichmentStatus'):
        return self.place_id < other.place_id
