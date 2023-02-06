import dataclasses
import datetime as dt
import decimal
import typing

import psycopg2.tz

from testsuite.utils import matching

from tests_eats_rest_menu_storage import definitions


UPDATED_AT = '2021-01-01T01:01:01.000+00:00'
DELETED_AT = '2021-01-01T01:01:01.000+00:00'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


@dataclasses.dataclass
class Place:
    place_id: int
    brand_id: int
    slug: str


@dataclasses.dataclass
class BrandMenuCategory:
    brand_id: int
    origin_id: str
    name: str

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id


@dataclasses.dataclass
class PlaceMenuCategory:
    brand_menu_category_id: typing.Union[str, matching.AnyString]
    place_id: int
    origin_id: str
    category_id: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    legacy_id: typing.Optional[int] = None
    name: typing.Optional[str] = None
    schedule: typing.Optional[typing.List[dict]] = None
    deleted_at: typing.Optional[str] = None
    updated_at: typing.Optional[str] = UPDATED_AT
    synced_schedule: bool = True

    def __lt__(self, other) -> bool:
        return self.category_id < other.category_id


@dataclasses.dataclass
class CategoryRelation:
    place_id: int
    category_id: int
    parent_id: int
    deleted: bool = False

    def __lt__(self, other) -> bool:
        return dataclasses.astuple(self) < dataclasses.astuple(other)


@dataclasses.dataclass
class Nutrients:
    calories: str
    proteins: str
    fats: str
    carbohydrates: str
    updated_at: typing.Optional[str] = None
    deleted: typing.Optional[bool] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class BrandMenuItem:
    brand_id: int
    origin_id: str
    name: typing.Optional[str] = 'brand_menu_item_name'
    adult: bool = False
    description: typing.Optional[str] = None
    weight_value: typing.Optional[str] = None
    weight_unit: typing.Optional[str] = None
    short_name: typing.Optional[str] = None
    deleted: bool = False
    nutrients: typing.Optional[Nutrients] = None


@dataclasses.dataclass
class PlaceMenuItem:
    place_id: int
    brand_menu_item_id: str
    origin_id: str
    adult: bool = False
    ordinary: bool = True
    choosable: bool = True
    shipping_types: typing.List[definitions.ShippingType] = dataclasses.field(
        default_factory=lambda: [
            definitions.ShippingType.Delivery,
            definitions.ShippingType.Pickup,
        ],
    )
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    weight_value: typing.Optional[float] = None
    weight_unit: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    legacy_id: typing.Optional[int] = None
    short_name: typing.Optional[str] = None
    deleted_at: typing.Optional[str] = None
    nutrients: typing.Optional[Nutrients] = None
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class PlaceMenuItemPrice:
    place_menu_item_id: int
    price: decimal.Decimal
    promo_price: typing.Optional[decimal.Decimal] = None
    vat: typing.Optional[decimal.Decimal] = None
    deleted: bool = False


@dataclasses.dataclass
class Picture:
    url: str
    ratio: typing.Optional[float]


@dataclasses.dataclass
class ItemPicture:
    place_menu_item_id: int
    picture_id: int
    deleted: bool = False


@dataclasses.dataclass
class CategoryPicture:
    place_menu_category_id: int
    picture_id: int
    deleted: bool = False


@dataclasses.dataclass
class BrandMenuItemInnerOption:
    brand_id: int
    origin_id: str
    name: typing.Optional[str] = 'brand_menu_item_inner_option_name'
    group_name: typing.Optional[
        str
    ] = 'brand_menu_item_inner_option_group_name'
    group_origin_id: typing.Optional[
        str
    ] = 'brand_menu_item_inner_option_group_origin_id'
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None


@dataclasses.dataclass
class PlaceMenuItemInnerOption:
    brand_menu_item_inner_option: str
    place_menu_item_id: int
    origin_id: str
    legacy_id: typing.Optional[int] = None
    name: typing.Optional[str] = None
    group_name: typing.Optional[str] = None
    group_origin_id: typing.Optional[str] = None
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class BrandMenuItemOptionGroup:
    brand_id: int
    origin_id: str
    name: str
    min_selected_options: typing.Optional[int] = None
    max_selected_options: typing.Optional[int] = None


@dataclasses.dataclass
class PlaceMenuItemOptionGroup:
    brand_menu_item_option_group: str
    place_menu_item_id: int
    origin_id: str
    legacy_id: typing.Optional[int] = None
    name: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    min_selected_options: typing.Optional[int] = None
    max_selected_options: typing.Optional[int] = None
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class BrandMenuItemOption:
    brand_id: int
    origin_id: str
    name: str
    multiplier: int = 1
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    sort: typing.Optional[int] = None


@dataclasses.dataclass
class PlaceMenuItemOption:
    brand_menu_item_option: str
    place_menu_item_option_group_id: int
    origin_id: str
    name: typing.Optional[str] = None
    legacy_id: typing.Optional[int] = None
    multiplier: typing.Optional[int] = None
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    sort: typing.Optional[int] = None
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class PlaceMenuItemOptionPrice:
    place_menu_item_option_id: int
    price: decimal.Decimal
    promo_price: typing.Optional[decimal.Decimal] = None
    vat: typing.Optional[decimal.Decimal] = None
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class PlaceMenuItemCategory:
    place_id: int
    place_menu_category_id: int
    place_menu_item_id: int
    deleted: bool = False


@dataclasses.dataclass
class PlaceMenuItemStock:
    place_menu_item_id: int
    stock: int
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class PlaceMenuItemOptionStatus:
    place_menu_item_option_id: int
    active: bool
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class PlaceMenuItemStatus:
    place_menu_item_id: int
    active: bool
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


@dataclasses.dataclass
class PlaceMenuCategoryStatus:
    place_menu_category_id: int
    active: bool
    deleted: bool = False
    updated_at: typing.Optional[str] = UPDATED_AT


def pg_time(time_point: str):
    result = dt.datetime.strptime(time_point, DATETIME_FORMAT)
    return result.replace(
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
    )
