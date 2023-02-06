# pylint: disable=C5521
import dataclasses
import datetime as dt
import itertools
from typing import Optional

from tests_eats_retail_business_alerts.models.base import BaseObject
from tests_eats_retail_business_alerts.models.base import StrGenerator


@dataclasses.dataclass
class Brand(BaseObject):
    brand_id: int = dataclasses.field(
        default_factory=itertools.count().__next__,
    )
    slug: str = dataclasses.field(
        default_factory=StrGenerator('slug_').__next__,
    )
    name: str = dataclasses.field(
        default_factory=StrGenerator('Name ').__next__,
    )
    is_enabled: bool = True
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'Brand'):
        return self.brand_id < other.brand_id
