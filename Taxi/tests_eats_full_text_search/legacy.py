import dataclasses
import enum
import typing

# pylint: disable=C0103


class PictureScale(enum.Enum):
    kAspectFit = 'aspect_fit'
    kAspectFill = 'aspect_fill'


@dataclasses.dataclass
class LegacyPicture:
    # required
    url: str
    # optional
    scale: typing.Optional[str] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class GoodCategory:
    id: int
    parentId: int
    name: str
    schedule: str
    available: bool
    gallery: typing.List[LegacyPicture]


@dataclasses.dataclass
class PromoType:
    id: int
    name: str
    pictureUri: str
    detailedLegacyPictureUrl: str


@dataclasses.dataclass
class LegacyOption:
    id: int
    name: str
    price: int
    decimalPrice: str
    multiplier: int
    promoPrice: typing.Optional[int] = None
    decimalPromoPrice: typing.Optional[str] = None


@dataclasses.dataclass
class LegacyOptionGroup:
    # required
    id: int
    name: str
    options: typing.List[LegacyOption]
    required: bool
    minSelected: typing.Union[int, None] = None
    maxSelected: typing.Union[int, None] = None


@dataclasses.dataclass
class Goods:
    id: int
    name: str
    available: bool
    price: int
    decimalPrice: str
    adult: bool
    shippingType: str
    description: str = ''
    picture: typing.Union[
        LegacyPicture, None, typing.Dict[typing.Any, typing.Any],
    ] = None
    weight: typing.Union[str, None] = None
    inStock: typing.Union[int, None] = None
    promoPrice: typing.Union[int, None] = None
    decimalPromoPrice: typing.Union[str, None] = None
    ancestors: typing.List[GoodCategory] = dataclasses.field(
        default_factory=list,
    )
    promoTypes: typing.List[PromoType] = dataclasses.field(
        default_factory=list,
    )
    optionGroups: typing.List[LegacyOptionGroup] = dataclasses.field(
        default_factory=list,
    )

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)
