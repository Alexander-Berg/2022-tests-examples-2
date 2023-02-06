import dataclasses
import enum
import typing

# pylint: disable=invalid-name
# pylint: disable=C0103


class WeightUnits(enum.Enum):
    UNKNOWN = ''
    LITER = 'l'
    MILLILITER = 'ml'
    GRAM = 'g'
    KILOGRAM = 'kg'
    PIECES = 'pcs'


@dataclasses.dataclass
class CategoryIds:
    # pylint: disable=C0103
    id: str
    legacy_id: typing.Optional[int] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class ItemPicture:
    url: str = 'https://eda.yandex.ru/image.png'


class ShippingType(str, enum.Enum):
    Delivery = 'delivery'
    Pickup = 'pickup'


def make_default_shipping_types() -> typing.List[ShippingType]:
    return list([ShippingType.Delivery, ShippingType.Pickup])


@dataclasses.dataclass
class ItemPreview:
    id: str = 'f6a274f9-b187-4593-8def-16ae66fea2c7'
    legacy_id: int = 1
    adult: bool = False
    available: bool = True
    name: str = 'Сочная курочка'
    price: str = '399'
    weight_value: str = '100'
    weight_unit: str = 'g'
    pictures: typing.Optional[typing.List[ItemPicture]] = None
    choosable: bool = True
    shipping_types: typing.List[ShippingType] = dataclasses.field(
        default_factory=make_default_shipping_types,
    )


@dataclasses.dataclass
class Place:
    place_id: str = '1'
    place_slug: str = 'place_slug_1'
    items: typing.List[ItemPreview] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ItemsPreviewResponse:
    places: typing.List[Place] = dataclasses.field(default_factory=list)

    def as_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class GetItemsResponse:
    places: typing.List[Place] = dataclasses.field(
        default_factory=typing.List[Place],
    )

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class InnerOption:
    id: str
    name: str
    origin_id: str
    group_name: str
    group_origin_id: str
    legacy_id: typing.Optional[int] = None
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    deleted_at: typing.Optional[str] = None

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class Option:
    id: str
    origin_id: str
    name: str
    multiplier: int = 1
    available: bool = True
    reactivate_at: typing.Optional[str] = None
    legacy_id: typing.Optional[int] = None
    min_amount: typing.Optional[int] = None
    max_amount: typing.Optional[int] = None
    price: typing.Optional[str] = None
    promo_price: typing.Optional[str] = None
    vat: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    deleted_at: typing.Optional[str] = None

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class OptionsGroup:
    id: str
    origin_id: str
    name: str
    legacy_id: typing.Optional[int] = None
    sort: typing.Optional[int] = None
    min_selected_options: typing.Optional[int] = None
    max_selected_options: typing.Optional[int] = None
    options: typing.Optional[typing.List[Option]] = None
    is_required: typing.Optional[bool] = False
    deleted_at: typing.Optional[str] = None

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class Item:
    id: str
    origin_id: str
    name: str
    adult: bool = False
    available: bool = True
    shipping_types: typing.List[ShippingType] = dataclasses.field(
        default_factory=make_default_shipping_types,
    )
    category_origin_ids: typing.Optional[typing.List[str]] = None
    legacy_id: typing.Optional[int] = None
    description: typing.Optional[str] = None
    categories_ids: typing.Optional[typing.List[CategoryIds]] = None
    weight_unit: typing.Optional[str] = None
    weight_value: typing.Optional[str] = None
    pictures: typing.Optional[typing.List[ItemPicture]] = None
    vat: typing.Optional[str] = None
    inner_options: typing.Optional[typing.List[InnerOption]] = None
    options_groups: typing.Optional[typing.List[OptionsGroup]] = None
    price: str = '500'
    promo_price: typing.Optional[str] = None
    sort: typing.Optional[int] = None
    ordinary: typing.Optional[bool] = None
    choosable: typing.Optional[bool] = None
    deleted_at: typing.Optional[str] = None
    stock: typing.Optional[int] = None
    short_name: typing.Optional[str] = None

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
