# pylint: disable=C5521

import dataclasses
import datetime as dt
import decimal as dec
from typing import Optional

from tests_eats_nomenclature_viewer.models.base import BaseObject


@dataclasses.dataclass
class PlaceProductPrice(BaseObject):
    place_id: int
    product_nmn_id: str
    price: dec.Decimal = dec.Decimal('1')
    old_price: Optional[dec.Decimal] = None
    full_price: Optional[dec.Decimal] = None
    old_full_price: Optional[dec.Decimal] = None
    vat: Optional[int] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceProductPrice'):
        return (self.place_id, self.product_nmn_id) < (
            other.place_id,
            other.product_nmn_id,
        )


@dataclasses.dataclass
class PlaceProductVendorData(BaseObject):
    place_id: int
    product_nmn_id: str
    vendor_code: Optional[str] = None
    position: Optional[str] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceProductPrice'):
        return (self.place_id, self.product_nmn_id) < (
            other.place_id,
            other.product_nmn_id,
        )


@dataclasses.dataclass
class PlaceProductStock(BaseObject):
    place_id: int
    product_nmn_id: str
    value: Optional[dec.Decimal] = None
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'PlaceProductPrice'):
        return (self.place_id, self.product_nmn_id) < (
            other.place_id,
            other.product_nmn_id,
        )
