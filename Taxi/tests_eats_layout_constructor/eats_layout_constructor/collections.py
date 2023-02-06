import enum
import typing

from . import experiments


class Strategy(str, enum.Enum):
    by_place_id = 'by_place_id'
    by_brand_id = 'by_brand_id'
    by_business = 'by_business'
    by_courier_type = 'by_courier_type'
    by_promo_type = 'by_promo_type'
    ultima = 'ultima'


class PlaceArgs(typing.NamedTuple):
    """
    Аргумент для стратегии by_place_id
    """

    place_ids: typing.List[int]


class BrandArgs(typing.NamedTuple):
    """
    Аргумент для стратегии by_brand_id
    """

    brand_ids: typing.List[int]


class CourierArgs(typing.NamedTuple):
    """
    Аргумент для стратегии by_courier_type
    """

    types: typing.List[str]


class PromoArgs(typing.NamedTuple):
    """
    Аргумент для стратегии by_courier_type
    """

    promo_type_ids: typing.List[int]


class BusinessArgs(typing.NamedTuple):
    """
    Аргумент для стратегии by_business
    """

    businesses: typing.List[str]


Args = typing.Union[PlaceArgs, BrandArgs, CourierArgs, PromoArgs, BusinessArgs]


def serialize_args(args: typing.Optional[Args]):
    if args is None:
        return None

    if isinstance(args, PlaceArgs):
        return {'place_ids': args.place_ids}

    if isinstance(args, BrandArgs):
        return {'brand_ids': args.brand_ids}

    if isinstance(args, CourierArgs):
        return {'types': args.types}

    if isinstance(args, PromoArgs):
        return {'promo_ids': args.promo_type_ids}

    if isinstance(args, BusinessArgs):
        return {'businesses': args.businesses}

    raise Exception('Unknonwn collection argument type')


class Information(typing.NamedTuple):
    """
    Содержит информацию для дополнительных блоков, в ревью коллекции
    """

    title: str
    body: str


class Meta(typing.NamedTuple):
    """
    Содержит данные, которые необходимо добавить к плейсу, в коллекции
    """

    # Описание заведения
    description: str
    # Содерижит дополнительную информацию о заведении
    information: typing.List[Information]
    # Позиция заведения
    position: typing.Optional[int] = None
    # Является ли заведение рекламным
    is_ad: typing.Optional[bool] = None


def serialize_meta(meta: Meta):

    blocks: list = []

    for info in meta.information:
        blocks.append({'titile': info.title, 'body': info.body})

    return {
        'description': meta.description,
        'informationBlocks': blocks,
        'isAds': meta.is_ad,
    }


class BrandMeta(typing.NamedTuple):
    """
    Описывает мету плейса по brand_slug
    """

    brand_slug: str
    meta: Meta


class PlaceMeta(typing.NamedTuple):
    """
    Описывает мету плейса по place_id
    """

    place_id: int
    meta: Meta


MetaType = typing.Union[BrandMeta, PlaceMeta]


class Image(typing.NamedTuple):
    """
    Описывает картинку для заголовка коллекции
    """

    light: str
    dark: str


def serialize_image(image: typing.Optional[Image]):
    if image is None:
        return None

    return {'light': image.light, 'dark': image.dark}


class Collection(typing.NamedTuple):
    """
    Описывает коллекцию
    """

    # Слаг коллекции
    slug: str
    # Заголовок коллекции
    title: str
    # Стратегия коллекции
    strategy: Strategy
    # Картинка для заголовка
    image: typing.Optional[Image] = None
    # Описание коллекции
    description: typing.Optional[str] = None
    # Способ получения заказа
    shipping_type: typing.Optional[str] = None
    # Аргументы для фильтрации коллеции
    args: typing.Optional[Args] = None
    # Мета для плейсов
    metas: typing.Optional[typing.List[MetaType]] = None
    # Язык коллекции
    locale: typing.Optional[str] = None


def serialize_metas(metas: typing.Optional[typing.List[MetaType]]):
    if metas is None:
        return None

    result = []

    for meta in metas:
        if isinstance(meta, BrandMeta):
            result.append(
                {
                    'brand_slug': meta.brand_slug,
                    'position': meta.meta.position,
                    'meta': serialize_meta(meta.meta),
                },
            )
        if isinstance(meta, PlaceMeta):
            result.append(
                {
                    'place_id': meta.place_id,
                    'position': meta.meta.position,
                    'meta': serialize_meta(meta.meta),
                },
            )

    return {'addMetaToPlace': result}


def experiment(**kwargs):
    collection = Collection(**kwargs)

    return experiments.always_match(
        name=f'eats_collections_{collection.slug}',
        consumer='eats-collections/collections',
        value={
            'title': collection.title,
            'description': collection.description,
            'image': serialize_image(collection.image),
            'locale': collection.locale,
            'searchConditions': {
                'shipping_type': collection.shipping_type,
                'strategy': collection.strategy.name,
                'arguments': serialize_args(collection.args),
                'actions': serialize_metas(collection.metas),
            },
        },
    )
