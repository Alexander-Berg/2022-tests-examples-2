# pylint: disable=C5521

import dataclasses
import datetime as dt
from typing import Optional

from tests_eats_nomenclature_viewer.models.base import BaseObject
from tests_eats_nomenclature_viewer.models.base import StrGenerator


@dataclasses.dataclass
class Image(BaseObject):
    url: str = dataclasses.field(default_factory=StrGenerator('url_').__next__)
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'Image'):
        return self.url < other.url
