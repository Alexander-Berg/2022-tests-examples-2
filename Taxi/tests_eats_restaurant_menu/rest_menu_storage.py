# pylint: disable=invalid-name

import dataclasses
import typing


@dataclasses.dataclass
class Category:
    id: str = 'id_1'
    origin_id: str = 'origin_id_1'
    name: str = 'Бургеры'
    legacy_id: typing.Optional[int] = 1
    sort: typing.Optional[int] = 100
    available: bool = True
    schedule: typing.Optional[typing.List[dict]] = None


@dataclasses.dataclass
class Picture:
    url: str = '/images/1387779/b13a00a671642b92c1ae31fb254053f2-450x300.png'
    ratio: typing.Optional[float] = 1.33


@dataclasses.dataclass
class Option:
    id: str = 'id_1'
    name: str = 'Котлета воппер'
    origin_id: str = 'origin_id_1'
    multiplier: int = 1
    legacy_id: typing.Optional[int] = 1
    available: bool = True
    price: str = '10.99'


@dataclasses.dataclass
class OptionGroup:
    id: str = 'id_1'
    origin_id: str = 'origin_id_1'
    is_required: bool = False
    name: str = 'Экстра Котлета Воппер'
    legacy_id: typing.Optional[int] = 1
    sort: typing.Optional[int] = 100
    min_selected_options: typing.Optional[int] = 0
    max_selected_options: typing.Optional[int] = 1
    options: typing.Optional[typing.List[Option]] = None


@dataclasses.dataclass
class CategoryIds:
    id: str = 'id_1'
    legacy_id: typing.Optional[int] = 1


@dataclasses.dataclass
class ItemNutrients:
    calories: str = '1.1'
    proteins: str = '2.2'
    fats: str = '3.3'
    carbohydrates: str = '4.4'


def default_shipping_types():
    return ['delivery', 'pickup']


@dataclasses.dataclass
class Item:
    id: str = 'id_1'
    origin_id: str = 'origin_id_1'
    name: str = 'Воппер с сыром'
    adult: bool = False
    shipping_types: typing.List[str] = dataclasses.field(
        default_factory=default_shipping_types,
    )
    legacy_id: typing.Optional[int] = 1
    description: typing.Optional[str] = None
    weight_unit: typing.Optional[str] = None
    weight_value: typing.Optional[str] = None
    pictures: typing.Optional[typing.List[Picture]] = None
    options_groups: typing.Optional[typing.List[OptionGroup]] = None
    price: str = '199.00'
    available: bool = True
    sort: typing.Optional[int] = 100
    ordinary: typing.Optional[bool] = None
    choosable: typing.Optional[bool] = None
    stock: typing.Optional[int] = None
    categories_ids: typing.Optional[typing.List[CategoryIds]] = None
    nutrients: typing.Optional[ItemNutrients] = ItemNutrients()

    def as_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Menu:
    categories: typing.Optional[typing.List[Category]] = None
    items: typing.Optional[typing.List[Category]] = None

    def as_dict(self):
        return dataclasses.asdict(self)
