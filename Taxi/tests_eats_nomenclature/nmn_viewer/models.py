import dataclasses
import itertools
from typing import List
from typing import Optional
import uuid as uuid_gen


class StrGenerator:
    def __init__(self, prefix=None):
        self.cnt = 1
        self.prefix = prefix

    def __iter__(self):
        return self

    def __next__(self):
        self.cnt += 1
        return f'{self.prefix}{self.cnt}'


@dataclasses.dataclass
class Vendor:
    name: str = 'name'
    country: str = ''


@dataclasses.dataclass
class Image:
    raw_url: str
    processed_url: Optional[str] = None


@dataclasses.dataclass
class ProductAttributes:
    brand: Optional[str] = None
    type: Optional[str] = None


@dataclasses.dataclass
class Sku:
    uuid: str = dataclasses.field(
        default_factory=lambda: str(uuid_gen.uuid4()),
    )
    name: str = dataclasses.field(
        default_factory=StrGenerator('sku_name_').__next__,
    )
    composition: Optional[str] = None
    storage_requirements: Optional[str] = None
    weight: Optional[str] = None
    сarbohydrates: Optional[str] = None  # pylint: disable=C0103
    proteins: Optional[str] = None
    fats: Optional[str] = None
    calories: Optional[str] = None
    country: Optional[str] = None
    package_type: Optional[str] = None
    expiration_info: Optional[str] = None
    volume: Optional[str] = None
    is_alcohol: Optional[bool] = None
    is_fresh: Optional[bool] = None
    is_adult: Optional[bool] = None
    fat_content: Optional[float] = None
    milk_type: Optional[str] = None
    cultivar: Optional[str] = None
    flavour: Optional[str] = None
    meat_type: Optional[str] = None
    carcass_part: Optional[str] = None
    egg_category: Optional[str] = None
    images: List[Image] = dataclasses.field(default_factory=list)
    attributes: Optional[ProductAttributes] = None


@dataclasses.dataclass
class Product:
    brand_id: int
    name: str = dataclasses.field(
        default_factory=StrGenerator('name_').__next__,
    )
    origin_id: str = dataclasses.field(
        default_factory=StrGenerator('origin_').__next__,
    )
    public_id: str = dataclasses.field(
        default_factory=lambda: str(uuid_gen.uuid4()),
    )
    quantum: float = 0
    measure_unit: str = 'GRM'
    measure_value: int = 1
    sku: Optional[Sku] = None
    use_sku_override: bool = False
    sku_override: Optional[Sku] = None
    description: Optional[str] = None
    vendor: Vendor = dataclasses.field(default_factory=Vendor)
    is_adult: bool = False
    is_catch_weight: bool = False
    is_choosable: bool = False
    package_info: Optional[str] = None
    images: List[Image] = dataclasses.field(default_factory=list)
    overriden_attributes: Optional[ProductAttributes] = None


@dataclasses.dataclass
class CategoryProduct:
    assortment_id: int
    product: Product
    sort_order: int = 0


@dataclasses.dataclass
class Category:
    assortment_id: int
    name: str = dataclasses.field(
        default_factory=StrGenerator('name_').__next__,
    )
    origin_id: str = dataclasses.field(
        default_factory=StrGenerator('origin_').__next__,
    )
    public_id: int = dataclasses.field(
        default_factory=itertools.count().__next__,
    )
    is_base: bool = True
    is_custom: bool = False
    is_restaurant: bool = False
    images: List[Image] = dataclasses.field(default_factory=list)
    parent_category: Optional['Category'] = None
    sort_order: int = 1

    _products: List[CategoryProduct] = dataclasses.field(
        default_factory=list, init=False,
    )

    def add_product(self, product: Product, sort_order: int = 0):
        # pylint: disable=E1101
        self._products.append(
            CategoryProduct(
                assortment_id=self.assortment_id,
                product=product,
                sort_order=sort_order,
            ),
        )

    def get_products(self) -> List[Product]:
        # pylint: disable=E1133
        return [i.product for i in self._products]

    def get_category_products(self) -> List[CategoryProduct]:
        return self._products
