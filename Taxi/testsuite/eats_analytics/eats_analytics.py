import base64
import dataclasses
import enum
import json
import typing

# pylint: disable=import-error
from eats.analytics import field_pb2  # noqa: F401


class ItemType(enum.IntEnum):
    # Сниппет заведения.
    PLACE = 1
    # Минисниппет заведения.
    MINI_PLACE = 2
    # Баннер.
    BANNER = 3
    # Турбо кнопка.
    TURBO_BUTTON = 4


class ViewType(enum.IntEnum):
    # Коллекция
    COLLECTION = 1
    # Таб
    TAB = 2


class BannerType(enum.IntEnum):
    SHORTCUT = 1
    WIDE_AND_SHORT = 2
    CLASSIC = 3
    PAGED = 4


class BannerWidth(enum.IntEnum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3


class Business(enum.IntEnum):
    # Ресторан
    RESTAURANT = 1
    # Лавка
    STORE = 2
    # Аптека
    PHARMACY = 3
    # Магазин
    SHOP = 4
    # Заправка
    ZAPRAVKI = 5


class SearchItemType(enum.IntEnum):
    # Общая информация о поисковом запросе.
    REQUEST = 1
    # Информация о заведении в поисковой выдаче.
    PLACE = 2


class SearchBlockType(enum.IntEnum):
    # Заведения
    PLACES = 1
    # Товары
    ITEMS = 2
    # Категории
    CATEGORIES = 3
    # Баннеры
    BANNERS = 4


@dataclasses.dataclass
class Position:
    column: int
    row: int


@dataclasses.dataclass
class DeliveryEta:
    min: int
    max: int


@dataclasses.dataclass
class SearchBlock:
    # Тип блока (places, items, categories, banners)
    type: typing.Optional[SearchBlockType] = None
    # Название блока (товары, категории)
    title: typing.Optional[str] = None
    # Количество найденных записей в блоке (заведений,
    # товаров, категорий, баннеров)
    items_count: typing.Optional[int] = None

    def __repr__(self):
        return json.dumps(dataclasses.asdict(self), sort_keys=True, indent=4)


@dataclasses.dataclass
class AnalyticsContext:
    # Название экрана, на котором отобразился layout
    screen: typing.Optional[str] = None

    # Идентификатор виджета, в котором отображается элемент
    widget_id: typing.Optional[str] = None
    # Идентификатор шаблон
    widget_template_id: typing.Optional[str] = None
    # Заголовок виджет
    widget_title: typing.Optional[str] = None

    # Идентификатор элемента
    item_id: typing.Optional[str] = None
    # Тип элемента
    item_type: typing.Optional[ItemType] = None
    # Слаг элемента
    item_slug: typing.Optional[str] = None
    # Название элемента
    item_name: typing.Optional[str] = None
    # Ссылка, на которую будет осущствлен переход при клике на элемент
    item_link: typing.Optional[str] = None
    # Горизонтальная и вертикальная позиция в выдаче
    item_position: typing.Optional[Position] = None

    # Идентификатор представления
    view_id: typing.Optional[str] = None
    # Тип представления
    view_type: typing.Optional[ViewType] = None

    # Тип баннера
    banner_type: typing.Optional[BannerType] = None
    # Ширина баннера
    banner_width: typing.Optional[BannerWidth] = None

    # Тип деятельности заведения
    place_business: typing.Optional[Business] = None
    # Текст бейджа
    place_badge: typing.Optional[str] = None
    # Список экшенов
    place_actions: typing.Optional[typing.List[str]] = None
    # Список экшенов
    place_eta: typing.Optional[DeliveryEta] = None
    # Флаг рекламности
    is_ad: typing.Optional[bool] = None

    # Slug заведения
    place_slug: typing.Optional[str] = None
    # Название заведения
    place_name: typing.Optional[str] = None
    # Признак доступности заведения
    place_available: typing.Optional[bool] = None

    # Данные для поиска
    # Тип элемента, для которого пишутся данные
    search_item_type: typing.Optional[SearchItemType] = None
    # Текстовый поисковый запрос
    search_query: typing.Optional[str] = None
    # Id поискового запроса
    search_request_id: typing.Optional[str] = None
    # Slug селектора (все, магазины, рестораны)
    search_selector: typing.Optional[str] = None
    # Количество найденных заведений (по всем блокам places в ответе)
    search_places_found: typing.Optional[int] = None
    # Количество доступных найденных заведений (по всем блокам places в ответе)
    search_places_available: typing.Optional[int] = None
    # Блоки с данными в ответе поиска
    search_blocks: typing.Optional[typing.List[SearchBlock]] = None
    # Позиция заведения в поисковой выдаче
    search_place_position: typing.Optional[int] = None
    # Количество найденных товаров у заведения
    search_place_items_count: typing.Optional[int] = None
    # Название блока, в котором находится заведение
    search_place_block_title: typing.Optional[str] = None

    def __repr__(self):
        return json.dumps(dataclasses.asdict(self), sort_keys=True, indent=4)


def add_screen(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.screen is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_SCREEN
    value.strings.append(src.screen)


def add_widget_id(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.widget_id is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_WIDGET_ID
    value.strings.append(src.widget_id)


def add_widget_template_id(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.widget_template_id is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_WIDGET_TEMPLATE_ID
    value.strings.append(src.widget_template_id)


def add_widget_title(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.widget_title is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_WIDGET_TITLE
    value.strings.append(src.widget_title)


def add_item_id(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.item_id is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_ITEM_ID
    value.strings.append(src.item_id)


def add_item_type(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.item_type is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_ITEM_TYPE
    value.item_type = src.item_type.value


def add_item_slug(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.item_slug is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_ITEM_SLUG
    value.strings.append(src.item_slug)


def add_item_name(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.item_name is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_ITEM_NAME
    value.strings.append(src.item_name)


def add_item_link(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.item_link is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_ITEM_LINK
    value.strings.append(src.item_link)


def add_item_position(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.item_position is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_ITEM_POSITION
    value.integers.append(src.item_position.column)
    value.integers.append(src.item_position.row)


def add_layout_view_id(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.view_id is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_VIEW_ID
    value.strings.append(src.view_id)


def add_layout_view_type(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.view_type is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_LAYOUT_VIEW_TYPE
    value.view_type = src.view_type.value


def add_banner_type(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.banner_type is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_BANNER_TYPE
    value.banner_type = src.banner_type.value


def add_banner_width(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.banner_width is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_BANNER_WIDTH
    value.banner_width = src.banner_width.value


def add_place_business(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.place_business is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_BUSINESS
    value.business = src.place_business.value


def add_place_badge(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.place_badge is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_BADGE
    value.strings.append(src.place_badge)


def add_place_actions(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.place_actions is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_ACTIONS
    for action in src.place_actions:
        value.strings.append(action)


def add_place_eta(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.place_eta is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_ETA
    value.integers.append(src.place_eta.min)
    value.integers.append(src.place_eta.max)


def add_is_ad(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.is_ad is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_AD
    value.integers.append(int(src.is_ad))


def add_place_slug(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.place_slug is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_SLUG
    value.strings.append(src.place_slug)


def add_place_name(context: field_pb2.AnalyticsContext, src: AnalyticsContext):
    if src.place_name is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_NAME
    value.strings.append(src.place_name)


def add_place_available(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.place_available is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_PLACE_AVAILABLE
    value.integers.append(int(src.place_available))


def add_search_item_type(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_item_type is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_ITEM_TYPE
    value.search_item_type = src.search_item_type.value


def add_search_query(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_query is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_QUERY
    value.strings.append(src.search_query)


def add_search_request_id(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_request_id is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_REQUEST_ID
    value.strings.append(src.search_request_id)


def add_search_selector(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_selector is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_SELECTOR
    value.strings.append(src.search_selector)


def add_search_places_found(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_places_found is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_PLACES_FOUND
    value.integers.append(src.search_places_found)


def add_search_places_available(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_places_available is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_PLACES_AVAILABLE
    value.integers.append(src.search_places_available)


def add_search_blocks(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_blocks is None:
        return

    appliers = [
        add_search_block_type,
        add_search_block_title,
        add_search_block_items_count,
    ]

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_BLOCK
    for block in src.search_blocks:
        search_block = field_pb2.SearchBlock()
        for apply_field in appliers:
            apply_field(search_block, block)
        value.search_blocks.append(search_block)


def add_search_block_type(context: field_pb2.SearchBlock, src: SearchBlock):
    if src.type is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_BLOCK_TYPE
    value.type = src.type.value


def add_search_block_title(context: field_pb2.SearchBlock, src: SearchBlock):
    if src.title is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_BLOCK_TITLE
    value.strings.append(src.title)


def add_search_block_items_count(
        context: field_pb2.SearchBlock, src: SearchBlock,
):
    if src.items_count is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_BLOCK_ITEMS_COUNT
    value.integers.append(src.items_count)


def add_search_place_position(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_place_position is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_PLACE_POSITION
    value.integers.append(src.search_place_position)


def add_search_place_items_count(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_place_items_count is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_PLACE_ITEMS_COUNT
    value.integers.append(src.search_place_items_count)


def add_search_place_block_title(
        context: field_pb2.AnalyticsContext, src: AnalyticsContext,
):
    if src.search_place_block_title is None:
        return

    value = context.value.add()
    value.key = field_pb2.Key.KEY_SEARCH_BLOCK_TITLE
    value.strings.append(src.search_place_block_title)


def encode(context: AnalyticsContext) -> str:
    msg = field_pb2.AnalyticsContext()

    appliers = [
        add_screen,
        add_widget_id,
        add_widget_template_id,
        add_widget_title,
        add_item_id,
        add_item_type,
        add_item_slug,
        add_item_name,
        add_item_link,
        add_item_position,
        add_layout_view_id,
        add_layout_view_type,
        add_banner_type,
        add_banner_width,
        add_place_business,
        add_place_badge,
        add_place_actions,
        add_place_eta,
        add_is_ad,
        add_place_slug,
        add_place_name,
        add_place_available,
        add_search_item_type,
        add_search_query,
        add_search_request_id,
        add_search_selector,
        add_search_places_found,
        add_search_places_available,
        add_search_blocks,
        add_search_place_position,
        add_search_place_items_count,
        add_search_place_block_title,
    ]

    for apply_field in appliers:
        apply_field(msg, context)

    proto_raw = msg.SerializeToString(deterministic=True)
    return str(base64.standard_b64encode(proto_raw), 'utf-8')


def parse_screen(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.screen = src.strings[-1]


def parse_widget_id(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.widget_id = src.strings[-1]


def parse_widget_template_id(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.widget_template_id = src.strings[-1]


def parse_widget_title(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.widget_title = src.strings[-1]


def parse_item_type(context: AnalyticsContext, src: field_pb2.Value):

    if not src.item_type:
        return

    context.item_type = ItemType(src.item_type)


def parse_item_id(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.item_id = src.strings[-1]


def parse_item_slug(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.item_slug = src.strings[-1]


def parse_item_name(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.item_name = src.strings[-1]


def parse_item_link(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.item_link = src.strings[-1]


def parse_item_poistion(context: AnalyticsContext, src: field_pb2.Value):

    if len(src.integers) != 2:
        return

    context.item_position = Position(
        column=src.integers[0], row=src.integers[1],
    )


def parse_view_id(context: AnalyticsContext, src: field_pb2.Value):
    if not src.strings:
        return

    context.view_id = src.strings[-1]


def parse_view_type(context: AnalyticsContext, src: field_pb2.Value):
    if not src.view_type:
        return

    context.view_type = ViewType(src.view_type)


def parse_banner_type(context: AnalyticsContext, src: field_pb2.Value):
    if not src.banner_type:
        return

    context.banner_type = BannerType(src.banner_type)


def parse_banner_width(context: AnalyticsContext, src: field_pb2.Value):
    if not src.banner_width:
        return

    context.banner_width = BannerWidth(src.banner_width)


def parse_business(context: AnalyticsContext, src: field_pb2.Value):
    if src.business is None:
        return

    context.place_business = Business(src.business)


def parse_place_badge(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.place_badge = src.strings[-1]


def parse_place_actions(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.place_actions = []
    for action in src.strings:
        context.place_actions.append(action)


def parse_place_eta(context: AnalyticsContext, src: field_pb2.Value):

    if len(src.integers) != 2:
        return

    context.place_eta = DeliveryEta(min=src.integers[0], max=src.integers[1])


def parse_is_ad(context: AnalyticsContext, src: field_pb2.Value):

    if not src.integers:
        return

    context.is_ad = bool(src.integers[0])


def parse_place_slug(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.place_slug = src.strings[-1]


def parse_place_name(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.place_name = src.strings[-1]


def parse_place_available(context: AnalyticsContext, src: field_pb2.Value):

    if not src.integers:
        return

    context.place_available = bool(src.integers[0])


def parse_search_item_type(context: AnalyticsContext, src: field_pb2.Value):

    if not src.search_item_type:
        return

    context.search_item_type = SearchItemType(src.search_item_type)


def parse_search_query(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.search_query = src.strings[-1]


def parse_search_request_id(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.search_request_id = src.strings[-1]


def parse_search_selector(context: AnalyticsContext, src: field_pb2.Value):

    if not src.strings:
        return

    context.search_selector = src.strings[-1]


def parse_search_places_found(context: AnalyticsContext, src: field_pb2.Value):

    if not src.integers:
        return

    context.search_places_found = src.integers[0]


def parse_search_places_available(
        context: AnalyticsContext, src: field_pb2.Value,
):

    if not src.integers:
        return

    context.search_places_available = src.integers[0]


def parse_search_blocks(context: AnalyticsContext, src: field_pb2.Value):

    if not src.search_blocks:
        return

    parsers = {
        field_pb2.Key.KEY_SEARCH_BLOCK_TYPE: parse_search_block_type,
        field_pb2.Key.KEY_SEARCH_BLOCK_TITLE: parse_search_block_title,
        field_pb2.Key.KEY_SEARCH_BLOCK_ITEMS_COUNT: (
            parse_search_block_items_count
        ),
    }

    context.search_blocks = []
    for block in src.search_blocks:
        search_block = SearchBlock()
        for field in block.value:
            if field.key not in parsers:
                raise Exception(f'Unexpected field key: {field.key}')

            parse = parsers[field.key]
            parse(search_block, field)
        context.search_blocks.append(search_block)


def parse_search_block_type(context: SearchBlock, src: field_pb2.Value):

    if not src.type:
        return

    context.type = SearchBlockType(src.type)


def parse_search_block_title(context: SearchBlock, src: field_pb2.Value):

    if not src.strings:
        return

    context.title = src.strings[-1]


def parse_search_block_items_count(context: SearchBlock, src: field_pb2.Value):

    if not src.integers:
        return

    context.items_count = src.integers[0]


def parse_search_place_position(
        context: AnalyticsContext, src: field_pb2.Value,
):

    if not src.integers:
        return

    context.search_place_position = src.integers[0]


def parse_search_place_items_count(
        context: AnalyticsContext, src: field_pb2.Value,
):

    if not src.integers:
        return

    context.search_place_items_count = src.integers[0]


def parse_search_place_block_title(
        context: AnalyticsContext, src: field_pb2.Value,
):

    if not src.strings:
        return

    context.search_place_block_title = src.strings[-1]


def decode(src: str) -> typing.Optional[AnalyticsContext]:

    parsers = {
        field_pb2.Key.KEY_LAYOUT_SCREEN: parse_screen,
        field_pb2.Key.KEY_LAYOUT_WIDGET_ID: parse_widget_id,
        field_pb2.Key.KEY_LAYOUT_WIDGET_TEMPLATE_ID: parse_widget_template_id,
        field_pb2.Key.KEY_LAYOUT_WIDGET_TITLE: parse_widget_title,
        field_pb2.Key.KEY_LAYOUT_ITEM_TYPE: parse_item_type,
        field_pb2.Key.KEY_LAYOUT_ITEM_ID: parse_item_id,
        field_pb2.Key.KEY_LAYOUT_ITEM_SLUG: parse_item_slug,
        field_pb2.Key.KEY_LAYOUT_ITEM_NAME: parse_item_name,
        field_pb2.Key.KEY_LAYOUT_ITEM_LINK: parse_item_link,
        field_pb2.Key.KEY_LAYOUT_ITEM_POSITION: parse_item_poistion,
        field_pb2.Key.KEY_LAYOUT_VIEW_ID: parse_view_id,
        field_pb2.Key.KEY_LAYOUT_VIEW_TYPE: parse_view_type,
        field_pb2.Key.KEY_BANNER_TYPE: parse_banner_type,
        field_pb2.Key.KEY_BANNER_WIDTH: parse_banner_width,
        field_pb2.Key.KEY_PLACE_BUSINESS: parse_business,
        field_pb2.Key.KEY_PLACE_BADGE: parse_place_badge,
        field_pb2.Key.KEY_PLACE_ACTIONS: parse_place_actions,
        field_pb2.Key.KEY_PLACE_ETA: parse_place_eta,
        field_pb2.Key.KEY_AD: parse_is_ad,
        field_pb2.Key.KEY_PLACE_SLUG: parse_place_slug,
        field_pb2.Key.KEY_PLACE_NAME: parse_place_name,
        field_pb2.Key.KEY_PLACE_AVAILABLE: parse_place_available,
        field_pb2.Key.KEY_SEARCH_ITEM_TYPE: parse_search_item_type,
        field_pb2.Key.KEY_SEARCH_QUERY: parse_search_query,
        field_pb2.Key.KEY_SEARCH_REQUEST_ID: parse_search_request_id,
        field_pb2.Key.KEY_SEARCH_SELECTOR: parse_search_selector,
        field_pb2.Key.KEY_SEARCH_PLACES_FOUND: parse_search_places_found,
        field_pb2.Key.KEY_SEARCH_PLACES_AVAILABLE: (
            parse_search_places_available
        ),
        field_pb2.Key.KEY_SEARCH_BLOCK: parse_search_blocks,
        field_pb2.Key.KEY_SEARCH_PLACE_POSITION: parse_search_place_position,
        field_pb2.Key.KEY_SEARCH_PLACE_ITEMS_COUNT: (
            parse_search_place_items_count
        ),
        field_pb2.Key.KEY_SEARCH_BLOCK_TITLE: parse_search_place_block_title,
    }

    msg = field_pb2.AnalyticsContext()
    msg.ParseFromString(base64.standard_b64decode(src))

    if not msg.value:
        return None

    context = AnalyticsContext()
    for field in msg.value:
        if field.key not in parsers:
            raise Exception(f'Unexpected field key: {field.key}')

        parse = parsers[field.key]
        parse(context, field)

    return context
