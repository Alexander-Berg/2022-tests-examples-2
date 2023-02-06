import dataclasses
import enum
import json
import typing


@dataclasses.dataclass
class MenuItem:
    # Идентификатор товара
    menu_item_id: str
    # Идентификатор заведеня
    place_id: str


class RuleEffect(enum.Enum):
    MAP = 'map'
    UNMAP = 'unmap'


class RuleType(enum.Enum):
    PREDICATE = 'predicate'


class Rule(typing.NamedTuple):
    # Идентификатор правила
    rule_id: str
    # Человекочитаемый идентификатор правила
    slug: str
    # Название правила, может быть не уникальным
    name: str

    # Эффект применения правила
    effect: RuleEffect
    # Идентификаторы категорий
    category_ids: typing.List[str]
    # Тип правила
    type: RuleType
    # Включено ли правило
    enabled: bool
    # Содержимое правила
    payload: dict

    # Время создания правила
    created_at: str
    # Время последнего обновления правила
    updated_at: str

    def as_json(
            self,
            with_id=True,
            with_slug=True,
            with_times=True,
            with_created_at=True,
            with_updated_at=True,
    ):
        return {
            **({'id': self.rule_id} if with_id else {}),
            **({'slug': self.slug} if with_slug else {}),
            'name': self.name,
            'effect': self.effect.value,
            'category_ids': self.category_ids,
            'type': self.type.value,
            'enabled': self.enabled,
            'payload': {'type': 'predicate', 'predicate': self.payload},
            **(
                {'created_at': self.created_at}
                if with_times and with_created_at
                else {}
            ),
            **(
                {'updated_at': self.updated_at}
                if with_times and with_updated_at
                else {}
            ),
        }


class CategoryStatus(enum.Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    HIDDEN = 'hidden'


@dataclasses.dataclass
class Category:
    # Идентификатор категории
    category_id: str
    # Человекочитаемый идентификатор категории
    slug: str
    # Название категории
    name: str
    # Текущий статус
    status: CategoryStatus
    # Время создания
    created_at: str
    # Время последнего обновления
    updated_at: str
    # Логин автора
    created_by: typing.Optional[str] = None
    # Логин последнего редактора
    updated_by: typing.Optional[str] = None


@dataclasses.dataclass
class YtMenuItem:
    # pylint: disable=C0103
    item_legacy_id: int = 256404750
    adult: int = 0
    available: int = 0
    avatarnica_identity: str = '2370127/61fcc7fc4734cf94aae721da96035588'
    created_at: str = '2021-01-01 03:19:54.000000'
    deactivated_at: typing.Optional[str] = None
    decimal_old_price: typing.Optional[str] = None
    decimal_price: str = '30.0000'
    deleted_at: typing.Optional[str] = None
    description: str = (
        'Срок годности в днях: 1<br>Страна изготовления:'
        'Россия<br>Производитель: Кулинария Мм'
    )
    is_choosable: int = 1
    name: str = 'La lorraine Чиабатта клас п/уп Кулинария'
    old_price: typing.Optional[int] = None
    ordinary: int = 0
    origin_id: str = '1000302894'
    picture: str = '61fcc7fc4734cf94aae721da96035588.jpeg'
    picture_enabled: int = 1
    picture_ratio: float = 1.51
    place_id: int = 281503
    place_menu_category_id: int = 16729530
    price: int = 30
    promotional_item_id: typing.Optional[int] = None
    reactivate_at: typing.Optional[str] = None
    shipping_type: str = 'all'
    short_name: typing.Optional[str] = None
    sort: int = 100
    updated_at: str = '2021-02-16 10:51:24.000000'
    uuid: str = '47e4a5b2-26b0-5243-a974-47937b8ef7cf'
    vat: int = 20
    weight: str = '120 г'


@dataclasses.dataclass
class Mapping:
    # Идентификатор блюда
    menu_item_id: str
    # Идентификатор категории к которой относится блюдо
    category_id: str
    # Идентификатор правила по которому произошел матч
    rule_id: str
    # Показатель того, насколько точно блюдо матчится с категорией [0, 1]
    score: float = 1.0


@dataclasses.dataclass
class MenuItemMessage:
    item_id: int
    place_id: int = 1
    name: str = 'item 1'
    updated_at: str = '2021-12-13T13:00:00+03:00'

    def as_json(self) -> str:
        return json.dumps(
            {
                'doc': {
                    'item_legacy_id': self.item_id,
                    'place_id': self.place_id,
                    'name': self.name,
                    'updated_at': self.updated_at,
                },
            },
        )


@dataclasses.dataclass
class ScoredCategory:
    category_id: str
    score: float = 1.0


@dataclasses.dataclass
class ItemWithCategories:
    # идентификатор блюда
    item_id: str
    # категории к которым относится блюдо
    categories: typing.List[ScoredCategory]
