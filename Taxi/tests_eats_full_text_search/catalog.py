# pylint: disable=C0103

import dataclasses
import enum
import typing

from . import colors


@dataclasses.dataclass
class Availability:
    available_from: str = '2021-02-18T00:00:00+03:00'
    available_to: str = '2021-02-18T23:00:00+03:00'
    is_available: bool = True


@dataclasses.dataclass
class Brand:
    id: int = 1
    slug: str = 'brand_slug'


class Business(str, enum.Enum):
    Restaurant = 'restaurant'
    Store = 'store'
    Shop = 'shop'
    Pharmacy = 'pharmacy'
    Zapravki = 'zapravki'


@dataclasses.dataclass
class Currency:
    code: str = 'RUB'
    sign: str = '₽'


@dataclasses.dataclass
class Delivery:
    text: str = '10 - 20 min'


@dataclasses.dataclass
class Picture:
    uri: str = 'picture.url'
    ratio: float = 1.33


@dataclasses.dataclass
class PriceCategory:
    name: str = '₽'


@dataclasses.dataclass
class Tag:
    name: str = 'Завтраки'


@dataclasses.dataclass
class Advertisement:
    view_url: str
    click_url: str


@dataclasses.dataclass
class Rating:
    icon: colors.ColoredIconV2
    text: str


@dataclasses.dataclass
class Place:
    availability: Availability = Availability()
    brand: Brand = Brand()
    business: str = Business.Restaurant
    currency: Currency = Currency()
    delivery: Delivery = Delivery()
    id: int = 1
    name: str = 'Рест'
    picture: Picture = Picture()
    rating: typing.Optional[Rating] = None
    price_category: PriceCategory = PriceCategory()
    slug: str = 'slug_1'
    tags: typing.Iterable[Tag] = (Tag(),)
    advertisement: typing.Optional[Advertisement] = None


@dataclasses.dataclass
class Stats:
    places_count: int = 1


@dataclasses.dataclass
class Block:
    id: str = 'block_id'
    type: str = 'open'
    list: typing.Iterable[Place] = (Place(),)
    stats: Stats = Stats()


@dataclasses.dataclass
class BlockParam:
    custom_filter_type: str = 'open'
    brand_ids: typing.Optional[typing.List[int]] = None
    place_ids: typing.Optional[typing.List[int]] = None
    businesses: typing.Optional[typing.List[str]] = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)
