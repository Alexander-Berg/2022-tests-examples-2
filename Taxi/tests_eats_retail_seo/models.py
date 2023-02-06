import dataclasses
import datetime as dt
import decimal
from typing import Dict
from typing import List
from typing import Optional

import pytz


DEFAULT_LAST_REFERENCED_AT = dt.datetime(
    2020, 1, 11, 14, 0, 0, tzinfo=pytz.UTC,
)


def recursive_dict(x):
    result_dict = {}
    for key, value in x.__dict__.items():
        if isinstance(value, List):
            result_dict[key] = [recursive_dict(i) for i in sorted(value)]
        elif '__dict__' in dir(value):
            result_dict[key] = recursive_dict(value)
        else:
            result_dict[key] = value
    return result_dict


@dataclasses.dataclass
class Place:
    place_id: str
    slug: str
    brand_id: str

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.place_id < other.place_id


@dataclasses.dataclass
class Brand:
    brand_id: str
    slug: str
    name: str
    places: Dict[str, Place] = dataclasses.field(default_factory=dict)

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.brand_id < other.brand_id


@dataclasses.dataclass
class SnapshotTable:
    table_id: str
    table_path: str

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.table_id < other.table_id


@dataclasses.dataclass
class BrandMarketFeed:
    brand: Brand
    s3_path: str
    last_generated_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.brand < other.brand


@dataclasses.dataclass
class BrandGoogleFeed:
    brand: Brand
    s3_path: str
    last_generated_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.brand < other.brand


@dataclasses.dataclass
class ProductBrand:
    name: str
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.name < other.name


@dataclasses.dataclass
class ProductTypeProductBrand:
    product_brand: ProductBrand
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.product_brand < other.product_brand


@dataclasses.dataclass
class ProductType:
    name: str
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    _type_brands: List[ProductTypeProductBrand] = dataclasses.field(
        default_factory=list,
    )

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.name < other.name

    # Add linked entity
    def add_product_brand(
            self,
            product_brand: ProductBrand,
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._type_brands.append(
            ProductTypeProductBrand(product_brand, last_referenced_at),
        )

    # Set links
    def set_type_brands(self, type_brands: List[ProductTypeProductBrand]):
        self._type_brands = type_brands

    # Set linked entities
    def set_product_brands(
            self,
            product_brands: List[ProductBrand],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._type_brands = [
            ProductTypeProductBrand(product_brand, last_referenced_at)
            for product_brand in product_brands
        ]

    # Get links
    def get_type_brands(self) -> List[ProductTypeProductBrand]:
        return self._type_brands

    # Get linked entities
    def get_product_brands(self) -> List[ProductBrand]:
        return [type_brand.product_brand for type_brand in self._type_brands]


@dataclasses.dataclass
class Tag:
    name: str
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.name < other.name


@dataclasses.dataclass
class Barcode:
    value: str
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.value < other.value


@dataclasses.dataclass
class Picture:
    url: str
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.url < other.url


@dataclasses.dataclass
class ProductBarcode:
    barcode: Barcode
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.barcode < other.barcode


@dataclasses.dataclass
class ProductPicture:
    picture: Picture
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.picture < other.picture


@dataclasses.dataclass
class ProductInPlace:
    place: Place
    is_available: bool
    price: decimal.Decimal
    old_price: Optional[decimal.Decimal] = None
    stocks: Optional[int] = None
    vat: Optional[int] = None
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.place < other.place


@dataclasses.dataclass
class Product:
    nomenclature_id: str
    name: str
    brand: Brand
    origin_id: str
    sku_id: Optional[str] = None
    is_choosable: bool = True
    is_catch_weight: bool = False
    is_adult: bool = False
    description: Optional[str] = None
    composition: Optional[str] = None
    carbohydrates_in_grams: Optional[decimal.Decimal] = None
    proteins_in_grams: Optional[decimal.Decimal] = None
    fats_in_grams: Optional[decimal.Decimal] = None
    calories: Optional[decimal.Decimal] = None
    storage_requirements: Optional[str] = None
    expiration_info: Optional[str] = None
    package_info: Optional[str] = None
    product_type: Optional[ProductType] = None
    product_brand: Optional[ProductBrand] = None
    vendor_name: Optional[str] = None
    vendor_country: Optional[str] = None
    measure_in_grams: Optional[int] = None
    measure_in_milliliters: Optional[int] = None
    volume: Optional[int] = None
    delivery_flag: Optional[bool] = None
    pick_flag: Optional[bool] = None
    marking_type: Optional[str] = None
    is_alcohol: bool = False
    is_fresh: bool = False
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    _product_barcodes: List[ProductBarcode] = dataclasses.field(
        default_factory=list,
    )
    _product_pictures: List[ProductPicture] = dataclasses.field(
        default_factory=list,
    )
    _product_in_places: List[ProductInPlace] = dataclasses.field(
        default_factory=list,
    )

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.nomenclature_id < other.nomenclature_id

    # Add linked entity
    def add_barcode(
            self,
            barcode: Barcode,
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._product_barcodes.append(
            ProductBarcode(barcode, last_referenced_at),
        )

    def add_picture(
            self,
            picture: Picture,
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._product_pictures.append(
            ProductPicture(picture, last_referenced_at),
        )

    def add_product_in_place(self, product_in_place: ProductInPlace):
        self._product_in_places.append(product_in_place)

    # Set links
    def set_product_barcodes(self, product_barcodes: List[ProductBarcode]):
        self._product_barcodes = product_barcodes

    def set_product_pictures(self, product_pictures: List[ProductPicture]):
        self._product_pictures = product_pictures

    def set_product_in_places(self, product_in_places: List[ProductInPlace]):
        self._product_in_places = product_in_places

    # Set linked entities
    def set_barcodes(
            self,
            barcodes: List[Barcode],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._product_barcodes = [
            ProductBarcode(barcode, last_referenced_at) for barcode in barcodes
        ]

    def set_pictures(
            self,
            pictures: List[Picture],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._product_pictures = [
            ProductPicture(picture, last_referenced_at) for picture in pictures
        ]

    # Get links
    def get_product_barcodes(self) -> List[ProductBarcode]:
        return self._product_barcodes

    def get_product_pictures(self) -> List[ProductPicture]:
        return self._product_pictures

    def get_product_in_places(self) -> List[ProductInPlace]:
        return self._product_in_places

    # Get linked entities
    def get_barcodes(self) -> List[Barcode]:
        return [
            product_barcode.barcode
            for product_barcode in self._product_barcodes
        ]

    def get_pictures(self) -> List[Picture]:
        return [
            product_picture.picture
            for product_picture in self._product_pictures
        ]


@dataclasses.dataclass
class CategoryProduct:
    product: Product
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.product < other.product


@dataclasses.dataclass
class CategoryProductType:
    product_type: ProductType
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.product_type < other.product_type


@dataclasses.dataclass
class CategoryTag:
    tag: Tag
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.tag < other.tag


@dataclasses.dataclass
class CategoryRelation:
    category: 'Category'
    last_referenced_at: dt.datetime

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.category < other.category


@dataclasses.dataclass
class Category:
    category_id: str
    name: str
    image_url: Optional[str] = None
    last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT

    _category_products: List[CategoryProduct] = dataclasses.field(
        default_factory=list,
    )
    _category_product_types: List[CategoryProductType] = dataclasses.field(
        default_factory=list,
    )
    _category_tags: List[CategoryTag] = dataclasses.field(default_factory=list)
    _child_categories_relations: List[CategoryRelation] = dataclasses.field(
        default_factory=list,
    )

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.category_id < other.category_id

    # Add linked entity
    def add_product(
            self,
            product: Product,
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._category_products.append(
            CategoryProduct(product, last_referenced_at),
        )

    def add_product_type(
            self,
            product_type: ProductType,
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._category_product_types.append(
            CategoryProductType(product_type, last_referenced_at),
        )

    def add_tag(
            self,
            tag: Tag,
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._category_tags.append(CategoryTag(tag, last_referenced_at))

    def add_child_category(
            self,
            category: 'Category',
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._child_categories_relations.append(
            CategoryRelation(category, last_referenced_at),
        )

    # Set links
    def set_category_products(self, category_products: List[CategoryProduct]):
        self._category_products = category_products

    def set_category_product_types(
            self, category_product_types: List[CategoryProductType],
    ):
        self._category_product_types = category_product_types

    def set_category_tags(self, category_tags: List[CategoryTag]):
        self._category_tags = category_tags

    def set_child_categories_relations(
            self, category_relations: List[CategoryRelation],
    ):
        self._child_categories_relations = category_relations

    # Set linked entities
    def set_products(
            self,
            products: List[Product],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._category_products = [
            CategoryProduct(product, last_referenced_at)
            for product in products
        ]

    def set_product_types(
            self,
            product_types: List[ProductType],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._category_product_types = [
            CategoryProductType(product_type, last_referenced_at)
            for product_type in product_types
        ]

    def set_tags(
            self,
            tags: List[Tag],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._category_tags = [
            CategoryTag(tag, last_referenced_at) for tag in tags
        ]

    def set_child_categories(
            self,
            categories: List['Category'],
            last_referenced_at: dt.datetime = DEFAULT_LAST_REFERENCED_AT,
    ):
        self._child_categories_relations = [
            CategoryRelation(category, last_referenced_at)
            for category in categories
        ]

    # Get links
    def get_category_products(self) -> List[CategoryProduct]:
        return self._category_products

    def get_category_product_types(self) -> List[CategoryProductType]:
        return self._category_product_types

    def get_category_tags(self) -> List[CategoryTag]:
        return self._category_tags

    def get_child_categories_relations(self) -> List[CategoryRelation]:
        return self._child_categories_relations

    # Get linked entities
    def get_products(self) -> List[Product]:
        return [
            category_product.product
            for category_product in self._category_products
        ]

    def get_product_types(self) -> List[ProductType]:
        return [
            category_product_type.product_type
            for category_product_type in self._category_product_types
        ]

    def get_tags(self) -> List[Tag]:
        return [category_tag.tag for category_tag in self._category_tags]

    def get_child_categories(self) -> List['Category']:
        return [
            category_relation.category
            for category_relation in self._child_categories_relations
        ]


@dataclasses.dataclass
class GeneralizedPlacesProduct:
    product: Product
    category: Category
    price: decimal.Decimal
    old_price: Optional[decimal.Decimal] = None
    vat: Optional[int] = None

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.product < other.product


@dataclasses.dataclass
class SeoQueryData:
    slug: str
    query: str
    title: str
    description: str
    priority: int = 100

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        return self.slug < other.slug or (
            self.slug == other.slug and self.query < other.query
        )


@dataclasses.dataclass
class SeoQuery:
    product_type: Optional[ProductType] = None
    product_brand: Optional[ProductBrand] = None
    is_enabled: bool = True
    generated_data: Optional[SeoQueryData] = None
    manual_data: Optional[SeoQueryData] = None

    def get_data(self) -> Optional[SeoQueryData]:
        if self.manual_data:
            return self.manual_data
        if self.generated_data:
            return self.generated_data
        return None

    def get_type_brand_key(self):
        return (
            f'{self.product_type.name if self.product_type else ""}'
            f'_{self.product_brand.name if self.product_brand else ""}'
        )

    def __eq__(self, other):
        return recursive_dict(self) == recursive_dict(other)

    def __lt__(self, other):
        self_data = self.get_data()
        other_data = other.get_data()
        if not self_data and not other_data:
            return self.get_type_brand_key() < other.get_type_brand_key()
        if not self_data:
            return True
        if not other_data:
            return False
        return self_data < other_data
