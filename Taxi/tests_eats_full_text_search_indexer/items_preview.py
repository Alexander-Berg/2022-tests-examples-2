import dataclasses
import enum
import typing

# Потому что pylint считает что id
# не очень релевантное имя для поля класса
# pylint: disable=C0103


@dataclasses.dataclass
class CategoryInfo:
    id: str
    name: str
    legacy_id: typing.Optional[int] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


class ShippingType(str, enum.Enum):
    Delivery = 'delivery'
    Pickup = 'pickup'


@dataclasses.dataclass
class Picture:
    url: str
    avatarnica_identity: typing.Optional[str] = None
    ratio: typing.Optional[float] = None
    sort: typing.Optional[int] = None


@dataclasses.dataclass
class ItemPreview:
    id: str  # uuid #required
    name: str  # required
    adult: bool = False  # required
    available: bool = True  # required
    categories: typing.Optional[typing.List[CategoryInfo]] = None
    shipping_types: typing.List[ShippingType] = dataclasses.field(  # required
        default_factory=lambda: [ShippingType.Delivery, ShippingType.Pickup],
    )
    legacy_id: typing.Optional[int] = None
    weight_unit: typing.Optional[str] = None
    weight_value: typing.Optional[str] = None
    pictures: typing.Optional[typing.List[Picture]] = None
    price: str = '100'  # required
    promo_price: typing.Optional[str] = None

    def __lt__(self, other):
        return self.id < other.id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class ItemsPreviewPlaceResponse:
    place_id: str
    items: typing.List[ItemPreview]

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class ItemPreviewResponse:
    places: typing.List[ItemsPreviewPlaceResponse]

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
