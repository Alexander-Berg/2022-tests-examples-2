import dataclasses
import enum
import typing


# pylint: disable=C0103


@dataclasses.dataclass
class UpsellItem:
    core_id: int
    is_promoted: bool = False


@dataclasses.dataclass
class Picture:
    uri: str
    ratio: float
    scale: typing.Optional[str] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


class PictureScale(enum.Enum):
    AspectFit = 'aspect_fit'
    AspectFill = 'aspect_fill'


class ItemShippingType(enum.Enum):
    ALL = 'all'
    Delivery = 'delivery'
    Pickup = 'pickup'


@dataclasses.dataclass
class PromoType:
    id: int
    name: str
    pictureUri: str
    detailedPictureUrl: str


def get_empty_promo_types() -> typing.List[PromoType]:
    return []


@dataclasses.dataclass
class ItemOption:
    id: int
    name: str
    price: int
    decimalPrice: str
    multiplier: int
    decimalPromoPrice: typing.Optional[str] = None
    promoPrice: typing.Optional[int] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ItemGroup:
    id: int
    name: str
    options: typing.List[ItemOption]
    required: bool
    minSelected: typing.Optional[int] = None
    maxSelected: typing.Optional[int] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class FullUpsellItem:
    id: int
    name: str
    available: bool
    price: int
    decimalPrice: str
    optionsGroups: typing.List[ItemGroup]
    picture: typing.Union[Picture, typing.Dict[str, float], None]
    adult: bool
    shippingType: str
    decimalPromoPrice: typing.Union[str, None] = None
    promoted: typing.Union[str, None] = None
    description: typing.Optional[str] = None
    promoTypes: typing.Optional[typing.List[PromoType]] = dataclasses.field(
        default_factory=get_empty_promo_types,
    )
    inStock: typing.Optional[int] = None
    weight: typing.Optional[str] = None
    promoPrice: typing.Optional[int] = None

    NULLABLE_FIELDS = ['promoted', 'description']

    def dict_factory(self, x):
        """
        Функция чтобы можно было возвращать
        поля с nullable: true и значением None,
        но при этом вообще не возвращать поля которых нет в required
        """
        result = dict()
        for (k, v) in x:
            if v is None:
                if k in self.NULLABLE_FIELDS:
                    continue
                result[k] = v
            else:
                result[k] = v
        return result

    def as_dict(self) -> dict:
        return dataclasses.asdict(self, dict_factory=self.dict_factory)


def assert_equal_to_response_item(want: UpsellItem, got: dict):
    assert got is not None
    assert want.core_id == got['id']
    if want.is_promoted:
        assert 'promoted' in got
    else:
        assert 'promoted' not in got
