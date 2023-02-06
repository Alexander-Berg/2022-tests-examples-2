# pylint: disable=C0302
import asyncio

from dateutil import parser
# pylint: disable=import-error
from eats_analytics import eats_analytics
import pytest


from testsuite.utils import matching

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import layout_utils


TRANSLATIONS = {
    'c4l.place_category.1': 'Завтраки',
    'c4l.filters.deserti.name': 'Десерты',
    'c4l.filters.zdorovaya-eda.name': 'Здоровая еда',
    'c4l.filters.zavtraki.name': 'Завтраки',
    'c4l.filters.obed.name': 'Обед',
    'c4l.filters.coffee.name': 'Кофе',
}


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@experiments.SHOW_PLACE_CATEGORIES
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_badge',
    consumers=['eats-catalog-layout-badge'],
    clauses=[
        {
            'title': 'All',
            'value': {'text': 'Беееейдж'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'place_id',
                    'arg_type': 'int',
                    'value': 3,
                },
            },
        },
        {
            'title': 'Wrong',
            'value': {'text': 'Wrong place'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'place_id',
                    'arg_type': 'int',
                    'value': 1,
                },
            },
        },
    ],
    default_value={'text': 'Wrong text'},
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_pumpkin(taxi_eats_catalog, eats_catalog_storage, surge):
    photo = '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg'

    surge_title = (
        'Курьеров на всех не хватает, поэтому стоимость '
        'доставки временно увеличилась'
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=3,
            brand=storage.Brand(brand_id=1),
            price_category=storage.PriceCategory(value=0),
            features=storage.Features(
                brand_ui_backgrounds=[
                    storage.BrandUIBackground(theme='light'),
                    storage.BrandUIBackground(theme='dark'),
                ],
                brand_ui_logos=[
                    storage.BrandUILogo(theme='light', url='http://light'),
                    storage.BrandUILogo(theme='dark', url='http://dark'),
                ],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=3,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_same_brand',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            price_category=storage.PriceCategory(value=0),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='closed', place_id=2, brand=storage.Brand(brand_id=2),
        ),
    )

    # Включаем cурж
    surge.set_place_info(
        place_id=3,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-layout',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        json={
            'location': {'longitude': 37.591503, 'latitude': 55.802998},
            'blocks': [
                {'id': 'open', 'type': 'open', 'disable_filters': False},
            ],
        },
    )

    assert eats_catalog_storage.search_times_called == 1
    assert surge.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'filters': {
            'list': [
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Десерты',
                    'slug': 'deserti',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Здоровая еда',
                    'slug': 'zdorovaya-eda',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Завтраки',
                    'slug': 'zavtraki',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Обед',
                    'slug': 'obed',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Кофе',
                    'slug': 'coffee',
                },
            ],
        },
        'filters_v2': {
            'meta': {'selected_count': 0},
            'list': [
                {
                    'payload': {
                        'name': 'Десерты',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'deserti',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Здоровая еда',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'zdorovaya-eda',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Завтраки',
                        'state': 'enabled',
                        'picture_url': '/images/1387779-{w}x{h}.jpg',
                    },
                    'slug': 'zavtraki',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Обед',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'obed',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Кофе',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'coffee',
                    'type': 'quickfilter',
                },
            ],
        },
        'timepicker': [
            [
                '2021-01-01T12:30:00+03:00',
                '2021-01-01T13:00:00+03:00',
                '2021-01-01T13:30:00+03:00',
                '2021-01-01T14:00:00+03:00',
            ],
            [
                '2021-01-02T10:00:00+03:00',
                '2021-01-02T10:30:00+03:00',
                '2021-01-02T11:00:00+03:00',
                '2021-01-02T11:30:00+03:00',
                '2021-01-02T12:00:00+03:00',
                '2021-01-02T12:30:00+03:00',
                '2021-01-02T13:00:00+03:00',
                '2021-01-02T13:30:00+03:00',
                '2021-01-02T14:00:00+03:00',
            ],
        ],
        'sort': {
            'current': 'default',
            'default': 'default',
            'list': [
                {'description': 'Доверюсь вам', 'slug': 'default'},
                {'description': 'С высоким рейтингом', 'slug': 'high_rating'},
                {'description': 'Быстрые', 'slug': 'fast_delivery'},
                {'description': 'Недорогие', 'slug': 'cheap_first'},
                {'description': 'Дорогие', 'slug': 'expensive_first'},
            ],
        },
        'blocks': [
            {
                'id': 'open',
                'stats': {
                    'places_count': 1,
                    'native_surge_places_count': 1,
                    'market_surge_places_count': 0,
                    'orders_count': 0,
                    'radius_surge_orders_count': 0,
                },
                'list': [
                    {
                        'payload': {
                            'name': 'Тестовое заведение 1293',
                            'slug': 'open',
                            'availability': {'is_available': True},
                            'media': {'photos': [{'uri': photo}]},
                            'brand': {
                                'slug': 'coffee_boy_euocq',
                                'name': 'COFFEE BOY',
                                'business': 'restaurant',
                            },
                            'analytics': layout_utils.MatchingAnalyticsContext(
                                eats_analytics.AnalyticsContext(
                                    item_id='3',
                                    item_name='Тестовое заведение 1293',
                                    item_slug='open',
                                    item_type=eats_analytics.ItemType.PLACE,
                                    place_eta=eats_analytics.DeliveryEta(
                                        min=25, max=35,
                                    ),
                                    place_business=(
                                        eats_analytics.Business.RESTAURANT
                                    ),
                                ),
                            ),
                            'data': {
                                'meta': [
                                    {
                                        'id': matching.UuidString(),
                                        'type': 'rating',
                                        'payload': {
                                            'icon': {
                                                'color': [
                                                    {
                                                        'theme': 'light',
                                                        'value': '#FAC220',
                                                    },
                                                    {
                                                        'theme': 'dark',
                                                        'value': '#FAC220',
                                                    },
                                                ],
                                                'uri': 'asset://rating_star',
                                            },
                                            'description': {
                                                'color': [
                                                    {
                                                        'theme': 'light',
                                                        'value': '#21201F',
                                                    },
                                                    {
                                                        'theme': 'dark',
                                                        'value': '#F5F4F2',
                                                    },
                                                ],
                                                'text': '4.8 Хорошо',
                                            },
                                            'additional_text': {
                                                'color': [
                                                    {
                                                        'theme': 'light',
                                                        'value': '#21201F',
                                                    },
                                                    {
                                                        'theme': 'dark',
                                                        'value': '#F5F4F2',
                                                    },
                                                ],
                                                'text': '(123)',
                                            },
                                            'title': '4.8 Хорошо',
                                            'icon_url': 'asset://rating_star',
                                            'color': [
                                                {
                                                    'theme': 'light',
                                                    'value': '#21201F',
                                                },
                                                {
                                                    'theme': 'dark',
                                                    'value': '#F5F4F2',
                                                },
                                            ],
                                        },
                                    },
                                    {
                                        'id': matching.UuidString(),
                                        'type': 'info',
                                        'payload': {
                                            'icon_url': '',
                                            'title': 'Завтраки',
                                        },
                                    },
                                    {
                                        'id': matching.UuidString(),
                                        'type': 'price_category',
                                        'payload': {
                                            'icon_url': (
                                                'asset://price_category'
                                            ),
                                            'currency_sign': '₽',
                                            'total_symbols': 3,
                                            'highlighted_symbols': 1,
                                        },
                                    },
                                ],
                                'actions': [],
                                'features': {
                                    'accent_color': [
                                        {'theme': 'light', 'value': '#bada55'},
                                        {'theme': 'dark', 'value': '#bada55'},
                                    ],
                                    'logo': [
                                        {
                                            'theme': 'dark',
                                            'value': [
                                                {
                                                    'logo_url': 'http://dark',
                                                    'size': 'small',
                                                },
                                            ],
                                        },
                                        {
                                            'theme': 'light',
                                            'value': [
                                                {
                                                    'logo_url': 'http://light',
                                                    'size': 'small',
                                                },
                                            ],
                                        },
                                    ],
                                    'badge': {
                                        'text': 'Беееейдж',
                                        'color': [
                                            {
                                                'theme': 'dark',
                                                'value': 'lightgray',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': 'lightgray',
                                            },
                                        ],
                                    },
                                    'delivery': {
                                        'icons': [
                                            'asset://surge',
                                            'asset://native_delivery',
                                        ],
                                        'text': '25\u2009–\u200935 мин',
                                    },
                                    'surge': {
                                        'icon_url': 'asset://surge',
                                        'accent_color': [
                                            {
                                                'theme': 'dark',
                                                'value': '#9845E6',
                                            },
                                            {
                                                'theme': 'light',
                                                'value': '#9845E6',
                                            },
                                        ],
                                        'title': (
                                            'Высокий спрос, доставка 288₽'
                                        ),
                                        'description': surge_title,
                                        'extended': {
                                            'title': surge_title,
                                            'content': '',
                                            'button': {
                                                'title': 'Все равно закажу',
                                                'url': '',
                                            },
                                        },
                                    },
                                },
                            },
                            'layout': [
                                {
                                    'type': 'meta',
                                    'layout': [
                                        {
                                            'id': matching.UuidString(),
                                            'type': 'rating',
                                        },
                                        {
                                            'id': matching.UuidString(),
                                            'type': 'info',
                                        },
                                        {
                                            'id': matching.UuidString(),
                                            'type': 'price_category',
                                        },
                                    ],
                                },
                            ],
                        },
                        'meta': {
                            'place_id': 3,
                            'brand_id': 1,
                            'surge_level': 2,
                            'is_available_now': True,
                            'is_ultima': False,
                            'categories': ['Завтраки'],
                        },
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_no_data(catalog_for_layout, eats_catalog_storage, surge):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=3, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=3,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='open_same_brand',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            price_category=storage.PriceCategory(value=0),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    # Включаем cурж
    surge.set_place_info(
        place_id=3,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'no_data': True,
            },
        ],
    )

    assert surge.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'filters': {
            'list': [
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Десерты',
                    'slug': 'deserti',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Здоровая еда',
                    'slug': 'zdorovaya-eda',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Завтраки',
                    'slug': 'zavtraki',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Обед',
                    'slug': 'obed',
                },
                {
                    'active': False,
                    'group': 'quick',
                    'type': 'quickfilter',
                    'name': 'Кофе',
                    'slug': 'coffee',
                },
            ],
        },
        'filters_v2': {
            'meta': {'selected_count': 0},
            'list': [
                {
                    'payload': {
                        'name': 'Десерты',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'deserti',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Здоровая еда',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'zdorovaya-eda',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Завтраки',
                        'state': 'enabled',
                        'picture_url': '/images/1387779-{w}x{h}.jpg',
                    },
                    'slug': 'zavtraki',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Обед',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'obed',
                    'type': 'quickfilter',
                },
                {
                    'payload': {
                        'name': 'Кофе',
                        'state': 'enabled',
                        'picture_url': '/images/1380157-{w}x{h}.jpg',
                    },
                    'slug': 'coffee',
                    'type': 'quickfilter',
                },
            ],
        },
        'timepicker': [[], []],
        'sort': {
            'current': 'default',
            'default': 'default',
            'list': [
                {'description': 'Доверюсь вам', 'slug': 'default'},
                {'description': 'С высоким рейтингом', 'slug': 'high_rating'},
                {'description': 'Быстрые', 'slug': 'fast_delivery'},
                {'description': 'Недорогие', 'slug': 'cheap_first'},
                {'description': 'Дорогие', 'slug': 'expensive_first'},
            ],
        },
        'blocks': [
            {
                'id': 'open',
                'stats': {
                    'places_count': 1,
                    'native_surge_places_count': 1,
                    'market_surge_places_count': 0,
                    'orders_count': 0,
                    'radius_surge_orders_count': 0,
                },
                'list': [],
            },
        ],
    }


@pytest.mark.now('2021-01-01T12:00:00+03:00')
async def test_no_picture(catalog_for_layout, eats_catalog_storage):
    """
    EDACAT-762: проверяет, что в выдачу не попадает заведений, у которых
    нет кратинок. На практике такое поведение не обязательно, но оно
    крашило IOS, поэтому если тебе хочется удалить этот тест, то нужно
    убедиться, что в проде нет версий приложения <= 5.10
    """

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-01-01T10:00:00+03:00'),
        end=parser.parse('2021-01-01T14:00:00+03:00'),
    )

    # Добавляем заведение, в котором есть картинка оно нужно
    # для контроля, что что-то все таки возвращается
    eats_catalog_storage.add_place(
        storage.Place(
            slug='with_picture', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=[schedule]),
    )

    # Добавляем заведение без картинки - его не должно быть в выдаче
    eats_catalog_storage.add_place(
        storage.Place(
            slug='without_picture',
            place_id=2,
            brand=storage.Brand(brand_id=2),
            gallery=[],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=2, place_id=2, working_intervals=[schedule]),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    layout_utils.assert_no_slug(
        'without_picture', layout_utils.find_block('open', data),
    )


@pytest.mark.now('2021-04-11T18:46:00+03:00')
async def test_availability_strategy(catalog_for_layout, eats_catalog_storage):
    """
    EDACAT-838: проверяет, что в выдаче ручки catalog-for-layout
    будут появляться только заведения с availability_strategy == default
    """

    eats_catalog_storage.add_place(
        storage.Place(
            slug='default',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            features=storage.Features(availability_strategy='default'),
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            slug='burger_king',
            place_id=2,
            brand=storage.Brand(brand_id=2),
            features=storage.Features(availability_strategy='burger_king'),
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            slug='whitelabel_only',
            place_id=3,
            brand=storage.Brand(brand_id=3),
            features=storage.Features(availability_strategy='whitelabel_only'),
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    layout_utils.assert_no_slug('burger_king', block)
    layout_utils.assert_no_slug('whitelabel_only', block)
    layout_utils.find_place_by_slug('default', block)

    assert len(block) == 1


@pytest.mark.now('2021-04-13T11:00:00+03:00')
@pytest.mark.parametrize(
    'filters, sorts',
    [
        pytest.param(
            None,
            [
                {'description': 'Доверюсь вам', 'slug': 'default'},
                {'description': 'С высоким рейтингом', 'slug': 'high_rating'},
                {'description': 'Быстрые', 'slug': 'fast_delivery'},
                {'description': 'Недорогие', 'slug': 'cheap_first'},
                {'description': 'Дорогие', 'slug': 'expensive_first'},
            ],
            id='delivery with all sorts',
        ),
        pytest.param(
            [{'type': 'pickup', 'slug': 'pickup'}],
            [
                {'description': 'Доверюсь вам', 'slug': 'default'},
                {'description': 'С высоким рейтингом', 'slug': 'high_rating'},
                {'description': 'Недорогие', 'slug': 'cheap_first'},
                {'description': 'Дорогие', 'slug': 'expensive_first'},
            ],
            id='pickup with no fast delivery',
        ),
    ],
)
async def test_layout_sorts(
        catalog_for_layout, eats_catalog_storage, filters, sorts,
):
    """EDACAT-829: тест проверяет, что список доступных сортировок соответствует
    выбранному способу получения заказа."""
    eats_catalog_storage.add_place(
        storage.Place(
            slug='default', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-04-13T9:00:00+03:00'),
        end=parser.parse('2021-04-13T22:00:00+03:00'),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Delivery,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=1,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Pickup,
        ),
    )

    body: dict = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': 'any', 'type': 'any', 'disable_filters': False}],
    }
    if filters:
        body['filters'] = filters

    response = await catalog_for_layout(**body)
    assert response.status_code == 200

    assert response.json()['sort']['list'] == sorts


@pytest.mark.now('2021-04-15T13:00:00+03:00')
@pytest.mark.parametrize(
    'filters_v1, filters_v2, umlaas_calls',
    [
        pytest.param(None, None, 1, id='delivery has umlaas ranking'),
        pytest.param(
            [{'type': 'pickup', 'slug': 'pickup'}],
            None,
            0,
            id='pickup filters v1 has no umlaas ranking',
        ),
        pytest.param(
            None,
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'type': 'pickup', 'slug': 'pickup'}],
                    },
                ],
            },
            0,
            id='pickup filters v2 has no umlaas ranking',
        ),
    ],
)
async def test_ignore_umlaas_on_pickup(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        filters_v1,
        filters_v2,
        umlaas_calls,
):
    """
    EDACAT-863: тест проверяет, что при включенном фильтре самовывоза, не будет
    запроса в umlaas-eats за ранжированием каталога.
    """

    eats_catalog_storage.add_place(storage.Place(place_id=1))

    shipping_types: list = [
        storage.ShippingType.Delivery,
        storage.ShippingType.Pickup,
    ]

    for zone_id, shipping_type in zip([1, 2], shipping_types):
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=zone_id,
                shipping_type=shipping_type,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-04-15T9:00:00+03:00'),
                        end=parser.parse('2021-04-15T22:00:00+03:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_catalog(request):
        if umlaas_calls == 0:
            assert False, 'expected no umlaas calls'

        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': [],
        }

    body: dict = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': 'any', 'type': 'any', 'disable_filters': False}],
    }
    if filters_v1:
        body['filters'] = filters_v1
    if filters_v2:
        body['filters_v2'] = filters_v2

    response = await catalog_for_layout(**body)
    assert response.status_code == 200
    assert umlaas_catalog.times_called == umlaas_calls

    layout_utils.find_block('any', response.json())


@pytest.mark.now('2021-05-25T02:26:00+03:00')
@experiments.qsr_pickup_user('special_user')
@experiments.couriers_pickup(brand_ids=[1])
@pytest.mark.parametrize(
    'personal_phone_id, places, places_count, filters_v1, filters_v2',
    [
        pytest.param(
            'special_user',
            ['qsr_pickup', 'regular_pickup'],
            2,
            [{'type': 'pickup', 'slug': 'pickup'}],
            None,
            id='special user - filters_v1',
        ),
        pytest.param(
            'special_user',
            ['qsr_pickup', 'regular_pickup'],
            2,
            None,
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'type': 'pickup', 'slug': 'pickup'}],
                    },
                ],
            },
            id='special user - filters_v2',
        ),
        pytest.param(
            'regular_user',
            ['regular_pickup'],
            1,
            [{'type': 'pickup', 'slug': 'pickup'}],
            None,
            id='regular_user - filters_v1',
        ),
        pytest.param(
            'regular_user',
            ['regular_pickup'],
            1,
            None,
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'type': 'pickup', 'slug': 'pickup'}],
                    },
                ],
            },
            id='regular_user - filters_v2',
        ),
    ],
)
async def test_special_pickup(
        catalog_for_layout,
        eats_catalog_storage,
        personal_phone_id,
        places,
        places_count,
        filters_v1,
        filters_v2,
):
    """
    Проверяет, что заведения помеченые экспериментом eats_couriers_pickup
    отображаются как доступные для самовывоза только для пользователей,
    которые входят в эксперимент open_qsr_pickup
    """

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-05-25T00:00:00+03:00'),
            end=parser.parse('2021-05-25T08:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='qsr_pickup', brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=schedule,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2, slug='regular_pickup', brand=storage.Brand(brand_id=2),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=schedule,
        ),
    )

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'ios_app',
            'x-app-version': '6.1.0',
            'X-Eats-User': 'personal_phone_id={}'.format(personal_phone_id),
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
        filters=filters_v1,
        filters_v2=filters_v2,
    )
    assert response.status_code == 200

    block = layout_utils.find_block('open', response.json())

    assert len(block) == places_count
    for slug in places:
        layout_utils.find_place_by_slug(slug, block)


@pytest.mark.now('2021-09-09T12:00:00+03:00')
async def test_layout_count_metrics(
        catalog_for_layout,
        taxi_eats_catalog,
        eats_catalog_storage,
        taxi_eats_catalog_monitor,
        surge,
):
    # Добавляем 10 заведений
    for i in range(1, 11):
        eats_catalog_storage.add_place(
            storage.Place(
                slug='default_{}'.format(i),
                place_id=i,
                brand=storage.Brand(brand_id=i),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                shipping_type=storage.ShippingType.Delivery,
            ),
        )

    # Включаем cурж для 3-х заведений
    for i in [3, 8, 10]:
        surge.set_place_info(
            place_id=i,
            surge={
                'nativeInfo': {
                    'deliveryFee': 199,
                    'loadLevel': 91,
                    'surgeLevel': 2,
                },
            },
        )

    await taxi_eats_catalog.tests_control(reset_metrics=True)

    response_metrics = (
        await taxi_eats_catalog_monitor.get_metric('response')
    )['catalog-for-layout']
    assert response_metrics['places-count'] == {}
    assert response_metrics['surge-places-count'] == {}
    assert response_metrics['blocks-count'] == {}

    response = await catalog_for_layout(
        blocks=[
            {'id': 'any_1', 'type': 'any', 'disable_filters': False},
            {'id': 'any_2', 'type': 'any', 'disable_filters': False},
        ],
    )
    assert response.status_code == 200

    data = response.json()
    layout_utils.find_block('any_1', data)
    layout_utils.find_block('any_2', data)

    slow_metrics_test = False
    if not slow_metrics_test:
        return

    # Мы используем метрики 'RecentPeriod', где одна эпоха длится 5 секунд.
    # Ждём 6 секунд чтобы текущая эпоха точно была добавлена в метрику.
    await asyncio.sleep(6)

    response_metrics = (
        await taxi_eats_catalog_monitor.get_metric('response')
    )['catalog-for-layout']

    # 2 блока по 10 заведений в каждом
    places_count = response_metrics['places-count']['1min']
    assert places_count['max'] == 2 * 10

    # 2 блока по 3 заведения с суржом в каждом
    surge_places_count = response_metrics['surge-places-count']['1min']
    assert surge_places_count['max'] == 2 * 3

    blocks_count = response_metrics['blocks-count']['1min']
    assert blocks_count['max'] == 2


async def _get_no_places_sum(taxi_eats_catalog_monitor):
    return (await taxi_eats_catalog_monitor.get_metric('response'))[
        'catalog-for-layout'
    ]['no-places']['sum']


@pytest.mark.now('2021-09-09T12:00:00+03:00')
async def test_layout_count_no_places_metric(
        catalog_for_layout,
        taxi_eats_catalog,
        eats_catalog_storage,
        taxi_eats_catalog_monitor,
):
    await taxi_eats_catalog.tests_control(reset_metrics=True)

    headers = {
        'x-device-id': 'test_simple',
        'x-request-id': 'hello',
        'x-platform': 'ios_app',
        'x-app-version': '6.1.0',
        'X-Eats-Session': 'blablabla',
        'cookie': 'just a cookie',
    }

    # 1 Нет блоков
    response = await catalog_for_layout(headers=headers, blocks=[])
    assert response.status_code == 200
    no_places_sum = await _get_no_places_sum(taxi_eats_catalog_monitor)
    assert no_places_sum == 1

    # 2 Не найдено ни одного заведения
    response = await catalog_for_layout(
        headers=headers,
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )
    assert response.status_code == 200
    no_places_sum = await _get_no_places_sum(taxi_eats_catalog_monitor)
    assert no_places_sum == 2

    # 3 Нет заведений в блоке
    eats_catalog_storage.add_place(
        storage.Place(
            slug='default_{}'.format(1),
            place_id=1,
            brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('1990-01-01T10:00:00+03:00'),
                    end=parser.parse('1990-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )
    await taxi_eats_catalog.tests_control(invalidate_caches=True)

    response = await catalog_for_layout(
        headers=headers,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )
    assert response.status_code == 200
    no_places_sum = await _get_no_places_sum(taxi_eats_catalog_monitor)
    assert no_places_sum == 3

    # 4 Есть заведение в блоке
    response = await catalog_for_layout(
        headers=headers,
        blocks=[{'id': 'closed', 'type': 'closed', 'disable_filters': False}],
    )
    assert response.status_code == 200
    no_places_sum = await _get_no_places_sum(taxi_eats_catalog_monitor)
    assert no_places_sum == 3  # Инкремента не было


async def test_layout_general_condition(
        catalog_for_layout, eats_catalog_storage,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='shop',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1, place_id=1, shipping_type=storage.ShippingType.Delivery,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='restaurant',
            place_id=2,
            brand=storage.Brand(brand_id=2),
            business=storage.Business.Restaurant,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2, place_id=2, shipping_type=storage.ShippingType.Delivery,
        ),
    )

    response = await catalog_for_layout(
        [{'id': 'any', 'type': 'any', 'disable_filters': False}],
        condition={
            'type': 'eq',
            'init': {
                'arg_name': 'business',
                'arg_type': 'string',
                'value': 'shop',
            },
        },
    )

    assert response.status_code == 200
    block = layout_utils.find_block('any', response.json())
    assert len(block) == 1
    layout_utils.find_place_by_slug('shop', block)


@pytest.mark.parametrize(
    'expected_ids',
    [
        pytest.param({2, 4, 6}, id='no filter'),
        pytest.param(
            {1, 6},
            marks=(
                experiments.filter_source_response(
                    place_ids=[2], brand_ids=[2],
                )
            ),
            id='filter',
        ),
        pytest.param(
            {4},
            marks=(
                experiments.always_match(
                    name='eats_places_filter_one',
                    consumer='eats-catalog-places-storage',
                    value={'brand_ids': [3], 'place_ids': []},
                ),
                experiments.always_match(
                    name='eats_places_filter_random_places',
                    consumer='eats-catalog-places-storage',
                    value={'brand_ids': [], 'place_ids': [1, 2]},
                ),
            ),
            id='multiple',
        ),
    ],
)
async def test_filter_source_response(
        catalog_for_layout, eats_catalog_storage, expected_ids,
):
    """
    Проверяет применение эксперимента filter_source_response, который
    отфильтровывает заведения из выдачи при поиске
    """
    brand_id = 0
    for i in range(1, 7):
        brand_id += i % 2
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{i}',
                place_id=i,
                brand=storage.Brand(brand_id=brand_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                shipping_type=storage.ShippingType.Delivery,
            ),
        )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200
    block = layout_utils.find_block('any', response.json())

    place_ids = {place['meta']['place_id'] for place in block}

    assert expected_ids == place_ids
