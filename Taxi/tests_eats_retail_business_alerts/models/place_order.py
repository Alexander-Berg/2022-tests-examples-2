# pylint: disable=C5521
import dataclasses
import datetime as dt
from typing import Optional

from .base import BaseObject
from .base import StrGenerator


@dataclasses.dataclass
class PlaceOrder(BaseObject):
    place_id: int
    order_nr: str = dataclasses.field(
        default_factory=StrGenerator('order_').__next__,
    )
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceOrder'):
        return self.order_nr < other.order_nr
