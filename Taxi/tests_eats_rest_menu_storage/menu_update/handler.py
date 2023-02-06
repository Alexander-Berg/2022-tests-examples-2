import dataclasses
import typing

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage import models


@dataclasses.dataclass
class UpdateInnerOption:
    name: str
    origin_id: str
    group_name: str
    group_origin_id: str
    legacy_id: typing.Optional[int] = None
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    deleted_at: typing.Optional[str] = None
    updated_at: typing.Optional[str] = None


@dataclasses.dataclass
class UpdateOption:
    origin_id: str
    name: str
    multiplier: int = 1
    available: bool = True
    reactivate_at: typing.Optional[str] = None
    legacy_id: typing.Optional[int] = None
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    price: typing.Optional[str] = '100.0'
    promo_price: typing.Optional[str] = None
    vat: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    deleted_at: typing.Optional[str] = None
    updated_at: typing.Optional[str] = None


@dataclasses.dataclass
class UpdateOptionsGroup:
    origin_id: str
    name: str
    legacy_id: typing.Optional[int] = None
    is_required: typing.Optional[bool] = False
    sort: typing.Optional[int] = None
    min_selected_options: typing.Optional[int] = None
    max_selected_options: typing.Optional[int] = None
    options: typing.Optional[typing.List[UpdateOption]] = None
    deleted_at: typing.Optional[str] = None
    updated_at: typing.Optional[str] = None


@dataclasses.dataclass
class UpdateCategory:
    origin_id: str
    name: str
    available: bool
    parent_origin_id: typing.Optional[str] = None
    legacy_id: typing.Optional[int] = None
    pictures: typing.Optional[typing.List[definitions.Picture]] = None
    schedule: typing.Optional[typing.List[dict]] = None
    sort: typing.Optional[int] = None
    deleted_at: typing.Optional[str] = None
    updated_at: typing.Optional[str] = None
    synced_schedule: typing.Optional[bool] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Weight:
    unit: str
    value: str


@dataclasses.dataclass
class UpdateItem:
    origin_id: str
    name: str
    adult: bool = False
    available: bool = True
    shipping_types: typing.List[definitions.ShippingType] = dataclasses.field(
        default_factory=lambda: [
            definitions.ShippingType.Delivery,
            definitions.ShippingType.Pickup,
        ],
    )
    category_origin_ids: typing.Optional[typing.List[str]] = None
    legacy_id: typing.Optional[int] = None
    description: typing.Optional[str] = None
    weight: typing.Optional[definitions.Weight] = None
    pictures: typing.Optional[typing.List[definitions.Picture]] = None
    vat: typing.Optional[str] = None
    inner_options: typing.Optional[typing.List[UpdateInnerOption]] = None
    options_groups: typing.Optional[typing.List[UpdateOptionsGroup]] = None
    price: str = '100'
    promo_price: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    ordinary: typing.Optional[bool] = None
    choosable: typing.Optional[bool] = None
    deleted_at: typing.Optional[str] = None
    stock: typing.Optional[int] = None
    short_name: typing.Optional[str] = None
    updated_at: typing.Optional[str] = None
    nutrients: typing.Optional[models.Nutrients] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)
