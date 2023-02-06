import dataclasses
import typing

from testsuite.utils import matching

from tests_eats_rest_menu_storage import definitions
from tests_eats_rest_menu_storage.menu_update import handler


# Потому что pylint считает что id
# не очень релевантное имя для поля класса
# pylint: disable=C0103


@dataclasses.dataclass
class InnerOption(handler.UpdateInnerOption):
    id: str = ''

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class Option(handler.UpdateOption):
    id: str = ''
    multiplier: int = 1

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class OptionsGroup(handler.UpdateOptionsGroup):
    id: str = ''

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class Category(handler.UpdateCategory):
    id: str = ''
    parent_ids: typing.Optional[typing.List[matching.UuidString]] = None

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class Item(handler.UpdateItem):
    id: str = ''
    weight_unit: typing.Optional[str] = None
    weight_value: typing.Optional[str] = None
    categories_ids: typing.Optional[
        typing.List[definitions.CategoryIds]
    ] = None

    def __lt__(self, other) -> bool:
        return self.origin_id < other.origin_id

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class MenuResponse:
    categories: typing.Optional[typing.List[Category]] = None
    items: typing.Optional[typing.List[Item]] = None

    def as_dict(self) -> dict:
        if not self.items:
            self.items = None
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class GetItemsPlaceResponse:
    place_id: str
    place_slug: str
    items: typing.List[Item] = dataclasses.field(
        default_factory=typing.List[Item],
    )

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )


@dataclasses.dataclass
class GetItemsResponse:
    places: typing.List[GetItemsPlaceResponse] = dataclasses.field(
        default_factory=typing.List[GetItemsPlaceResponse],
    )

    def as_dict(self) -> dict:
        return dataclasses.asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
