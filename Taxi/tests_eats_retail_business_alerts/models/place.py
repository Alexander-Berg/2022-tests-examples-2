# pylint: disable=C5521
import dataclasses
import datetime as dt
import itertools
from typing import Optional

from tests_eats_retail_business_alerts.models.base import BaseObject
from tests_eats_retail_business_alerts.models.base import StrGenerator


@dataclasses.dataclass
class Place(BaseObject):
    brand_id: int
    region_id: int
    place_id: int = dataclasses.field(
        default_factory=itertools.count().__next__,
    )
    slug: str = dataclasses.field(
        default_factory=StrGenerator('slug_').__next__,
    )
    name: str = dataclasses.field(
        default_factory=StrGenerator('Name ').__next__,
    )
    is_enabled: bool = True
    is_enabled_changed_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'Place'):
        return self.place_id < other.place_id
