import dataclasses
import enum
import typing

# pylint: disable=C0103


class PictureScale(enum.Enum):
    kAspectFit = 'aspect_fit'
    kAspectFill = 'aspect_fill'


@dataclasses.dataclass
class Picture:
    # required
    url: str
    # optional
    scale: typing.Optional[str] = None


@dataclasses.dataclass
class PromoType:
    # required
    id: int
    name: str
    # optional
    picture_url: typing.Optional[str] = None  # Изображение типа акции
    detailed_picture_url: typing.Optional[str] = None  # Изображение акции


@dataclasses.dataclass
class Option:
    # required
    id: str
    name: str
    price: int
    decimal_price: str
    multiplier: int
    promo_price: typing.Optional[int] = None
    decimal_promo_price: typing.Optional[str] = None


@dataclasses.dataclass
class OptionGroup:
    # required fields
    id: str
    name: str
    options: typing.List[Option]
    required: bool
    # optional fields
    min_selected: typing.Optional[int] = None
    max_selected: typing.Optional[int] = None


@dataclasses.dataclass
class Item:
    # required fields
    id: str
    title: str
    description: str
    adult: bool
    price: int
    decimal_price: str
    option_groups: typing.List[OptionGroup]
    shipping_type: str

    # optional fields
    gallery: typing.Optional[typing.List[Picture]] = None
    weight: typing.Optional[str] = None
    in_stock: typing.Optional[int] = None
    promo_price: typing.Optional[int] = None
    decimal_promo_price: typing.Optional[str] = None
    promo_types: typing.Optional[typing.List[PromoType]] = None
    public_id: typing.Optional[str] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
