# pylint: disable=C5521

import dataclasses
import datetime as dt
import itertools
from typing import Optional

from tests_eats_nomenclature_viewer.models.base import BaseObject
from tests_eats_nomenclature_viewer.models.base import StrGenerator


@dataclasses.dataclass
class Assortment(BaseObject):
    # start id with big number to avoid collisions
    # with bigserial generator in DB
    assortment_id: int = dataclasses.field(
        default_factory=itertools.count(start=10000).__next__,
    )
    updated_at: Optional[dt.datetime] = None
    created_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'Assortment'):
        return self.assortment_id < other.assortment_id


@dataclasses.dataclass
class AssortmentName(BaseObject):
    name: str = dataclasses.field(
        default_factory=StrGenerator('name_').__next__,
    )
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'AssortmentName'):
        return self.name < other.name


@dataclasses.dataclass
class PlaceAssortment(BaseObject):
    place_id: int
    assortment_name: AssortmentName = dataclasses.field(
        default_factory=lambda: AssortmentName('partner'),
    )
    active_assortment: Optional[Assortment] = None
    in_progress_assortment: Optional[Assortment] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceAssortment'):
        if self.place_id == other.place_id:
            return self.assortment_name < other.assortment_name

        return self.place_id < other.place_id
