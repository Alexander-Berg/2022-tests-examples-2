# pylint: disable=C5521
import dataclasses
import datetime as dt
import itertools
from typing import Optional

from .base import BaseObject

ORDERS_COUNT = 10
LAST_DATE_IN_MSC = '2021-01-01'


@dataclasses.dataclass
class PlaceCreatedOrdersStats(BaseObject):
    place_id: int
    orders_count: int = ORDERS_COUNT
    last_date_in_msc: str = LAST_DATE_IN_MSC
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceCreatedOrdersStats'):
        return self.place_id < other.place_id


@dataclasses.dataclass
class PlaceCreatedOrdersStatsHistory(BaseObject):
    place_id: int
    orders_count: int = ORDERS_COUNT
    last_date_in_msc: str = LAST_DATE_IN_MSC
    record_id: int = dataclasses.field(
        default_factory=itertools.count().__next__,
    )
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceCreatedOrdersStatsHistory'):
        return self.record_id < other.record_id
