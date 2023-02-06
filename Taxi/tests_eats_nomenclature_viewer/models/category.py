# pylint: disable=C5521

import dataclasses
import datetime as dt
from enum import Enum
import itertools
from typing import List
from typing import Optional

from tests_eats_nomenclature_viewer.models.assortment import Assortment
from tests_eats_nomenclature_viewer.models.base import BaseObject
from tests_eats_nomenclature_viewer.models.base import StrGenerator
from tests_eats_nomenclature_viewer.models.image import Image
from tests_eats_nomenclature_viewer.models.product import Product


class CategoryType(Enum):
    PARTNER = 'partner'
    CUSTOM_BASE = 'custom_base'
    CUSTOM_PROMO = 'custom_promo'
    CUSTOM_RESTAURANT = 'custom_restaurant'


@dataclasses.dataclass
class CategoryImage(BaseObject):
    image: Image
    sort_order: int = 0
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'CategoryImage'):
        return self.image < other.image


@dataclasses.dataclass
class CategoryProduct(BaseObject):
    product: Product
    sort_order: int = 0
    updated_at: Optional[dt.datetime] = None

    def __lt__(self, other: 'CategoryProduct'):
        return self.product < other.product


@dataclasses.dataclass
class Category(BaseObject):
    assortment: Assortment = dataclasses.field(default_factory=Assortment)
    nmn_id: int = dataclasses.field(
        default_factory=itertools.count(start=1).__next__,
    )
    origin_id: Optional[str] = None
    name: str = dataclasses.field(
        default_factory=StrGenerator('name_').__next__,
    )
    type: CategoryType = CategoryType.PARTNER
    category_images: List[CategoryImage] = dataclasses.field(
        default_factory=list,
    )
    category_products: List[CategoryProduct] = dataclasses.field(
        default_factory=list,
    )
    updated_at: Optional[dt.datetime] = None

    _category_relation: 'CategoryRelation' = dataclasses.field(init=False)

    def __post_init__(self):
        # category must always has a relation
        self._category_relation = CategoryRelation(category=self)

    @property
    def category_relation(self):
        return self._category_relation

    @category_relation.setter
    def category_relation(self, value: 'CategoryRelation'):
        assert value.category == self
        self._category_relation = value

    @property
    def parent(self):
        return self._category_relation.parent_category

    @parent.setter
    def parent(self, value: Optional['Category']):
        self._category_relation = CategoryRelation(
            category=self, parent_category=value,
        )

    @property
    def products(self):
        # pylint: disable=E1133
        return [i.product for i in self.category_products]

    def __lt__(self, other: 'Category'):
        if self.assortment == other.assortment:
            return self.nmn_id < other.nmn_id
        return self.assortment < other.assortment


@dataclasses.dataclass(eq=False)
class CategoryRelation(BaseObject):
    category: Category
    parent_category: Optional[Category] = None
    sort_order: int = dataclasses.field(
        default_factory=itertools.count(start=1).__next__,
    )
    updated_at: Optional[dt.datetime] = None

    @staticmethod
    def _category_nmn_id_or_empty(category: Optional[Category]):
        return category.nmn_id if category else ''

    def __lt__(self, other: 'CategoryRelation'):
        return (
            (
                self.category.assortment,
                self.category.nmn_id,
                self._category_nmn_id_or_empty(self.parent_category),
            )
            < (
                other.category.assortment,
                other.category.nmn_id,
                self._category_nmn_id_or_empty(other.parent_category),
            )
        )

    # break recursion via manual eq operator
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (
            (
                self.category.assortment,
                self.category.nmn_id,
                self._category_nmn_id_or_empty(self.parent_category),
                self.sort_order,
                self.updated_at,
            )
            == (
                other.category.assortment,
                other.category.nmn_id,
                self._category_nmn_id_or_empty(other.parent_category),
                other.sort_order,
                other.updated_at,
            )
        )


@dataclasses.dataclass
class PlaceCategory(BaseObject):
    assortment: Assortment = dataclasses.field(init=False)
    place_id: int
    category: Category
    active_items_count: int = 0
    updated_at: Optional[dt.datetime] = None
    created_at: Optional[dt.datetime] = None

    def __post_init__(self):
        self.assortment = self.category.assortment

    def __lt__(self, other: 'PlaceCategory'):
        return self.category < other.category
