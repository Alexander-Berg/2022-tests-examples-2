# pylint: disable=C5521

import dataclasses
import datetime as dt
import decimal as dec
from typing import List
from typing import Optional
import uuid as uuid_gen

from tests_eats_nomenclature_viewer.models.base import BaseObject
from tests_eats_nomenclature_viewer.models.base import StrGenerator
from tests_eats_nomenclature_viewer.models.image import Image


@dataclasses.dataclass
class ProductImage(BaseObject):
    image: Image
    sort_order: int = 0
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'ProductImage'):
        return self.image < other.image


@dataclasses.dataclass
class Attribute(BaseObject):
    name: str = dataclasses.field(
        default_factory=StrGenerator('name_').__next__,
    )
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'Attribute'):
        return self.name < other.name


@dataclasses.dataclass
class ProductAttribute(BaseObject):
    attribute: Attribute
    attribute_value: object
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'ProductAttribute'):
        return self.attribute < other.attribute


@dataclasses.dataclass
class Product(BaseObject):
    brand_id: int
    nmn_id: str = dataclasses.field(
        default_factory=lambda: str(uuid_gen.uuid4()),
    )
    name: str = dataclasses.field(
        default_factory=StrGenerator('name_').__next__,
    )
    origin_id: str = dataclasses.field(
        default_factory=StrGenerator('origin_').__next__,
    )
    sku_id: Optional[str] = None
    quantum: Optional[float] = None
    measure_unit: str = 'г'
    measure_value: dec.Decimal = dec.Decimal('1')
    product_attributes: List[ProductAttribute] = dataclasses.field(
        default_factory=list,
    )
    product_images: List[ProductImage] = dataclasses.field(
        default_factory=list,
    )
    updated_at: Optional[dt.datetime] = None

    def __post_init__(self):
        # casts measure_value to a proper type
        if isinstance(self.measure_value, float):
            self.measure_value = dec.Decimal(self.measure_value).quantize(
                dec.Decimal('.01'),
            )

    def __lt__(self, other: 'Product'):
        return self.nmn_id < other.nmn_id


@dataclasses.dataclass
class ProductUsage(BaseObject):
    product_nmn_id: str
    last_referenced_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None
    created_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'ProductUsage'):
        return self.product_nmn_id < other.product_nmn_id
