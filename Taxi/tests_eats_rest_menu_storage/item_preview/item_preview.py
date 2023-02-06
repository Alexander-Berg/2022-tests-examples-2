import dataclasses
import typing

from tests_eats_rest_menu_storage import definitions

# Потому что pylint считает что id
# не очень релевантное имя для поля класса
# pylint: disable=C0103


@dataclasses.dataclass
class ItemPreview:
    id: str  # uuid #required
    name: str  # required
    adult: bool = False  # required
    available: bool = True  # required
    shipping_types: typing.List[
        definitions.ShippingType
    ] = dataclasses.field(  # required
        default_factory=lambda: [
            definitions.ShippingType.Delivery,
            definitions.ShippingType.Pickup,
        ],
    )
    legacy_id: typing.Optional[int] = None
    weight_unit: typing.Optional[str] = None
    weight_value: typing.Optional[str] = None
    pictures: typing.Optional[typing.List[definitions.Picture]] = None
    price: str = '100'  # required
    promo_price: typing.Optional[str] = None
    choosable: bool = True
    categories: typing.Optional[typing.List[definitions.CategoryInfo]] = None

    def __lt__(self, other):
        return self.id < other.id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class ItemsPreviewPlaceRequest:
    place_id: str
    items: typing.List[str]


@dataclasses.dataclass
class ItemsPreviewRequest:
    places: typing.List[ItemsPreviewPlaceRequest]


@dataclasses.dataclass
class ItemsPreviewPlaceResponse:
    place_id: str
    items: typing.List[ItemPreview]


@dataclasses.dataclass
class ItemPreviewResponse:
    places: typing.List[ItemsPreviewPlaceResponse]
