# pylint: disable=C5521
import dataclasses
import datetime as dt
import itertools
from typing import Optional

from .base import BaseObject

ORDERS_COUNT = 10
LAST_DATE_IN_MSC = '2021-01-01'


@dataclasses.dataclass
class PlaceCancelledOrdersStats(BaseObject):
    place_id: int
    cancelled_by: str
    orders_count: int = ORDERS_COUNT
    last_date_in_msc: str = LAST_DATE_IN_MSC
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceCancelledOrdersStats'):
        return (self.place_id, self.cancelled_by) < (
            other.place_id,
            other.cancelled_by,
        )


@dataclasses.dataclass
class PlaceCancelledOrdersStatsHistory(BaseObject):
    place_id: int
    cancelled_by: str
    orders_count: int = ORDERS_COUNT
    last_date_in_msc: str = LAST_DATE_IN_MSC
    record_id: int = dataclasses.field(
        default_factory=itertools.count().__next__,
    )
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceCancelledOrdersStatsHistory'):
        return self.record_id < other.record_id
