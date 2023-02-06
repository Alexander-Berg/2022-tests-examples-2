# pylint: disable=C0302
import asyncio

# pylint: disable=import-error
from eats_bigb import eats_bigb
import pytest

from testsuite.utils import matching

from . import experiments
from . import utils


@pytest.mark.parametrize(
    'communications,banners',
    [
        pytest.param({}, [], id='empty'),
        pytest.param(
            {
                'banners': [
                    {
                        'id': 1,
                        'type': 'info',
                        'url': 'http://yandex.ru',
                        'app_url': 'http://yandex.ru/mobile',
                        'priority': 10,
                        'payload': {
                            'pages': [
                                {
                                    'shortcuts': [
                                        {
                                            'url': 'beautiful_shortcut.png',
                                            'theme': 'light',
                                            'platform': 'web',
                                        },
                                        {
                                            'url': 'beautiful_shortcut.png',
                                            'theme': 'dark',
                                            'platform': 'web',
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ],
            },
            [
                {
                    'id': 1,
                    'kind': 'info',
                    'formats': ['shortcut'],
                    'payload': {
                        'id': 1,
                        'kind': 'info',
                        'url': 'http://yandex.ru',
                        'appLink': 'http://yandex.ru/mobile',
                        'payload': {'badge': {}},
                        'images': [],
                        'shortcuts': [
                            {
                                'url': 'beautiful_shortcut.png',
                                'theme': 'light',
                                'platform': 'web',
                            },
                            {
                                'url': 'beautiful_shortcut.png',
                                'theme': 'dark',
                                'platform': 'web',
                            },
                        ],
                        'wide_and_short': [],
                        'meta': {'analytics': matching.AnyString()},
                    },
                },
            ],
            id='single',
        ),
        pytest.param(
            {
                'banners': [
                    {
                        'id': 1,
                        'type': 'info',
                        'url': 'http://yandex.ru',
                        'app_url': 'http://yandex.ru/mobile',
                        'priority': 10,
                        'payload': {
                            'pages': [
                                {
                                    'images': [
                                        {
                                            'url': 'beautiful_pic.png',
                                            'theme': 'light',
                                            'platform': 'web',
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                    {
                        'id': 2,
                        'type': 'info',
                        'url': 'http://yandex.com',
                        'app_url': 'http://yandex.com/mobile',
                        'priority': 100,
                        'payload': {
                            'pages': [
                                {
                                    'images': [
                                        {
                                            'url': 'beautiful_pic.png',
                                            'theme': 'light',
                                            'platform': 'web',
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ],
            },
            [
                {
                    'id': 2,
                    'kind': 'info',
                    'formats': ['classic'],
                    'payload': {
                        'id': 2,
                        'kind': 'info',
                        'url': 'http://yandex.com',
                        'appLink': 'http://yandex.com/mobile',
                        'payload': {'badge': {}},
                        'images': [
                            {
                                'url': 'beautiful_pic.png',
                                'theme': 'light',
                                'platform': 'web',
                            },
                        ],
                        'shortcuts': [],
                        'wide_and_short': [],
                        'meta': {'analytics': matching.AnyString()},
                    },
                },
                {
                    'id': 1,
                    'kind': 'info',
                    'formats': ['classic'],
                    'payload': {
                        'id': 1,
                        'kind': 'info',
                        'url': 'http://yandex.ru',
                        'appLink': 'http://yandex.ru/mobile',
                        'payload': {'badge': {}},
                        'images': [
                            {
                                'url': 'beautiful_pic.png',
                                'theme': 'light',
                                'platform': 'web',
                            },
                        ],
                        'shortcuts': [],
                        'wide_and_short': [],
                        'meta': {'analytics': matching.AnyString()},
                    },
                },
            ],
            id='sorted',
        ),
    ],
)
async def test_response(
        taxi_eats_communications, mockserver, communications, banners,
):
    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _communications(request):
        return communications

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert response.status_code == 200
    assert response.json()['payload']['banners'] == banners


async def test_filter_collection_banners(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {}

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {
            'payload': {
                'collections': [
                    {
                        'slug': 'collection_1',
                        'title': '1',
                        'description': '1',
                        'items_count': 10,
                    },
                    {
                        'slug': 'collection_2',
                        'title': '2',
                        'description': '2',
                        'items_count': 5,
                    },
                    {
                        'slug': 'collection_3',
                        'title': '3',
                        'description': '3',
                        'items_count': 7,
                    },
                ],
            },
        }

    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _communications(request):
        collections = request.json['state']['collections']
        assert collections
        request_slugs = frozenset(
            collection['slug'] for collection in collections
        )
        assert request_slugs == frozenset(
            ['collection_1', 'collection_2', 'collection_3'],
        )
        return {
            'banners': [
                {
                    'id': 1,
                    'type': 'collection',
                    'url': '/',
                    'app_url': '/',
                    'collection_slug': 'collection_1',
                    'priority': 10,
                    'payload': {
                        'pages': [
                            {
                                'wide': [
                                    {
                                        'url': 'beautiful_pic.png',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    'id': 2,
                    'type': 'collection',
                    'url': 'http://yandex.ru',
                    'app_url': 'http://yandex.ru/mobile',
                    'collection_slug': 'collection_10',
                    'priority': 10,
                    'payload': {
                        'pages': [
                            {
                                'wide': [
                                    {
                                        'url': 'beautiful_pic.png',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    'id': 3,
                    'type': 'brand',
                    'url': 'http://yandex.ru',
                    'app_url': 'http://yandex.ru/mobile',
                    'brand_id': 10,
                    'priority': 10,
                    'payload': {
                        'pages': [
                            {
                                'wide': [
                                    {
                                        'url': 'beautiful_pic.png',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        }

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert response.status_code == 200
    assert response.json()['payload']['banners'] == [
        {
            'id': 1,
            'kind': 'collection',
            'formats': ['wide_and_short'],
            'collection_slug': 'collection_1',
            'payload': {
                'id': 1,
                'kind': 'collection',
                'url': utils.URL_ROOT + '/collections/collection_1',
                'appLink': 'eda.yandex://collections/collection_1',
                'payload': {'badge': {'counter': 10}},
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
                'shortcuts': [],
                'images': [],
                'meta': {'analytics': matching.AnyString()},
            },
        },
    ]


async def test_place_brand_banners(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {
            'payload': [
                {
                    'id': 1,
                    'slug': 'place_1',
                    'type': 'restaurant',
                    'brand': {
                        'id': 1,
                        'slug': 'brand_1',
                        'placeSlug': 'place_2',
                    },
                },
            ],
        }

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _communications(request):
        return {
            'banners': [
                {
                    'id': 1,
                    'type': 'place',
                    'place_id': 1,
                    'priority': 10,
                    'payload': {
                        'pages': [
                            {
                                'wide': [
                                    {
                                        'url': 'beautiful_pic.png',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    'id': 2,
                    'type': 'place',
                    'place_id': 2,
                    'priority': 15,
                    'payload': {
                        'pages': [
                            {
                                'shortcuts': [
                                    {
                                        'url': 'beautiful_pic.png',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    'id': 3,
                    'type': 'brand',
                    'brand_id': 1,
                    'priority': 20,
                    'payload': {
                        'pages': [
                            {
                                'images': [
                                    {
                                        'url': 'beautiful_pic.png',
                                        'theme': 'light',
                                        'platform': 'web',
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        }

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert response.status_code == 200
    assert response.json()['payload']['banners'] == [
        {
            'id': 3,
            'kind': 'brand',
            'formats': ['classic'],
            'brand_id': 1,
            'payload': {
                'id': 3,
                'kind': 'brand',
                'url': utils.URL_ROOT + '/restaurant/place_2',
                'appLink': 'eda.yandex://restaurant/place_2',
                'payload': {'badge': {}},
                'images': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
                'shortcuts': [],
                'wide_and_short': [],
                'meta': {'analytics': matching.AnyString()},
            },
        },
        {
            'id': 1,
            'kind': 'place',
            'formats': ['wide_and_short'],
            'place_id': 1,
            'payload': {
                'id': 1,
                'kind': 'restaurant',
                'url': utils.URL_ROOT + '/restaurant/place_1',
                'appLink': 'eda.yandex://restaurant/place_1',
                'payload': {'badge': {}},
                'images': [],
                'shortcuts': [],
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
                'meta': {'analytics': matching.AnyString()},
            },
        },
    ]


@pytest.mark.parametrize(
    'platform,expected_platform',
    [
        pytest.param('eda_ios_app', 'eda_ios_app'),
        pytest.param('ios_app', 'eda_ios_app'),
        pytest.param('eda_android_app', 'eda_android_app'),
        pytest.param('android_app', 'eda_android_app'),
        pytest.param('eda_desktop_web', 'eda_desktop_web'),
        pytest.param('desktop_web', 'eda_desktop_web'),
        pytest.param('eda_mobile_web', 'eda_mobile_web'),
        pytest.param('mobile_web', 'eda_mobile_web'),
        pytest.param('uknown', 'eda_desktop_web'),
        pytest.param('magnit_app_web', 'eda_desktop_web'),
    ],
)
async def test_parse_application_platform(
        taxi_eats_communications, mockserver, platform, expected_platform,
):
    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _communications(request):
        assert request.json['application']['platform'] == expected_platform
        return {'banners': []}

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': platform,
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert response.status_code == 200


@experiments.feeds(list(f'feed_{i}' for i in range(1, 11)))
async def test_banners_count_metric(
        taxi_eats_communications, taxi_eats_communications_monitor, mockserver,
):
    await taxi_eats_communications.tests_control(reset_metrics=True)

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        feeds = []
        for i in range(1, 11):
            feeds.append(
                {
                    'banner_id': i,
                    'experiment': f'feed_{i}',
                    'recipients': {'type': 'info'},
                    'priority': 10,
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
            )

        return utils.make_feeds_payload(*feeds)

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert response.status_code == 200
    assert feeds.times_called == 1

    banners = response.json()['payload']['banners']
    assert len(banners) == 10

    # Мы используем метрики 'RecentPeriod', где одна эпоха длится 5 секунд.
    # Ждём 6 секунд чтобы текущая эпоха точно была добавлена в метрику.
    await asyncio.sleep(6)

    metric = await taxi_eats_communications_monitor.get_metric('response')
    banners_count = metric['v1-layout-banners']['banners-count']

    assert banners_count['1min']['max'] == len(banners)


@experiments.feed('default')
@pytest.mark.experiments3(
    name='grocery_new',
    consumers=['eats-communications/eats-promotions-banner'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'bool',
                'init': {'arg_name': 'is_grocery_new_user'},
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
)
@pytest.mark.eats_regions_cache(
    [
        {
            'id': 1,
            'name': 'Moscow',
            'slug': 'moscow',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [35.918658, 54.805858, 39.133684, 56.473673],
            'center': [37.642806, 55.724266],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {'id': 35, 'code': 'RU', 'name': 'Русь'},
        },
    ],
)
@pytest.mark.parametrize(
    'is_grocery_new_user, channels',
    [
        pytest.param(
            True,
            {
                'user_id:test_eats_user_id',
                'experiment:grocery_new',
                'experiment:default',
            },
            id='new grocery user',
        ),
        pytest.param(
            False,
            {'user_id:test_eats_user_id', 'experiment:default'},
            id='old grocery user',
        ),
    ],
)
async def test_grocery_tags(
        taxi_eats_communications, mockserver, is_grocery_new_user, channels,
):
    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v1/user-tags',
    )
    def grocery_tags(request):
        assert request.json == {
            'eats_user_id': 'test_eats_user_id',
            'personal_phone_id': 'test_pesonal_phone_id',
        }
        return {'is_new_user': is_grocery_new_user}

    @mockserver.handler('/eda-delivery-price/v1/user-promo')
    def eda_delivery_price(_):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert set(request.json['channels']) == channels
        return {}

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-Eats-User': (
                'user_id=test_eats_user_id,'
                'personal_phone_id=test_pesonal_phone_id,'
            ),
        },
        json={'latitude': 55.749953, 'longitude': 37.534143},
    )

    assert grocery_tags.times_called == 1
    assert eda_delivery_price.times_called == 1
    assert feeds.times_called == 1
    assert response.status_code == 200


@experiments.feed('brand_banner')
@experiments.brand_link([{'brand_id': 1, 'link': 'http://yandex.ru'}])
async def test_link_override(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def banner_places(_):
        return {
            'payload': [
                {
                    'id': 1,
                    'slug': 'place_1',
                    'type': 'restaurant',
                    'brand': {
                        'id': 1,
                        'slug': 'brand_1',
                        'placeSlug': 'place_2',
                    },
                },
            ],
        }

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'brand_banner',
                    'recipients': {'type': 'brand', 'brands': [1]},
                    'priority': 10,
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
            },
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-Eats-User': (
                'user_id=test_eats_user_id,'
                'personal_phone_id=test_pesonal_phone_id,'
            ),
        },
        json={'latitude': 55.749953, 'longitude': 37.534143},
    )

    assert response.status_code == 200
    assert feeds.times_called == 1
    assert banner_places.times_called == 1

    data = response.json()
    assert len(data['payload']['banners']) == 1

    banner = data['payload']['banners'][0]
    assert banner['payload']['appLink'] == 'http://yandex.ru'
    assert banner['payload']['url'] == 'http://yandex.ru'


@experiments.ENABLE_LINKS_OVERRIDE
@experiments.feeds(['feed_1', 'feed_2'])
async def test_link_override_via_admin(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def collections(request):
        return {
            'payload': {
                'collections': [
                    {
                        'slug': 'collection_1',
                        'title': '1',
                        'description': '1',
                        'items_count': 10,
                    },
                ],
            },
        }

    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def banner_places(_):
        return {
            'payload': [
                {
                    'id': 1,
                    'slug': 'place_1',
                    'type': 'restaurant',
                    'brand': {
                        'id': 1,
                        'slug': 'brand_1',
                        'placeSlug': 'place_1',
                    },
                },
                {
                    'id': 2,
                    'slug': 'place_1',
                    'type': 'restaurant',
                    'brand': {
                        'id': 2,
                        'slug': 'brand_2',
                        'placeSlug': 'place_2',
                    },
                },
            ],
        }

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            # Валидирует подмену ссылки баннера на бренд
            {
                'banner_id': 1,
                'experiment': 'feed_1',
                'url': 'http://from-feeds.ru',
                'appLink': 'http://from-feeds.ru/mobile',
                'recipients': {'type': 'brand', 'brands': [1]},
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'BANNER_FROM_FEEDS.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            # Валидирует подмену ссылки баннера на ресторан
            {
                'banner_id': 2,
                'experiment': 'feed_2',
                'url': 'http://from-feeds.ru',
                'appLink': 'http://from-feeds.ru/mobile',
                'recipients': {'type': 'restaurant', 'places': [2]},
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'BANNER_FROM_FEEDS.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            # Валидирует подмену ссылки баннера на коллекцию
            {
                'banner_id': 3,
                'experiment': 'feed_1',
                'recipients': {
                    'type': 'collection',
                    'collections': ['collection_1'],
                    'hide_counter': True,
                },
                'url': 'http://from-feeds.ru',
                'appLink': 'http://from-feeds.ru/mobile',
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-Eats-User': (
                'user_id=test_eats_user_id,'
                'personal_phone_id=test_pesonal_phone_id,'
            ),
        },
        json={'latitude': 55.749953, 'longitude': 37.534143},
    )

    assert response.status_code == 200
    assert feeds.times_called == 1
    assert collections.times_called == 1
    assert banner_places.times_called == 1

    data = response.json()
    assert len(data['payload']['banners']) == 3

    for banner in data['payload']['banners']:
        assert banner['payload']['appLink'] == 'http://from-feeds.ru/mobile'
        assert banner['payload']['url'] == 'http://from-feeds.ru'


@pytest.mark.experiments3(
    name='eats_communications_use_eats_catalog_places',
    consumers=['eats-communications/layout-banners'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)
async def test_pass_filters_to_catalog(taxi_eats_communications, mockserver):
    """
    Проверяем что фильтры пробрасываются в запрос к eats-catalog
    """

    filters_v2 = {
        'groups': [
            {
                'type': 'and',
                'filters': [{'slug': 'steak', 'type': 'quickfilter'}],
            },
        ],
    }

    @mockserver.json_handler('/eats-catalog/internal/v1/places')
    def eats_places(request):
        assert request.json['filters_v2'] == filters_v2
        return {'blocks': []}

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'brand', 'brands': [1]},
                    'priority': 10,
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
            },
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-Eats-User': (
                'user_id=test_eats_user_id,'
                'personal_phone_id=test_pesonal_phone_id,'
            ),
        },
        json={
            'latitude': 55.749953,
            'longitude': 37.534143,
            'filters_v2': filters_v2,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'payload': {'banners': [], 'blocks': [], 'header_notes': []},
    }

    assert feeds.times_called == 1
    assert eats_places.times_called == 1


@pytest.mark.bigb(
    eats_bigb.Profile(
        passport_uid='12341212', audience_segments={1, 100, 2, 1021},
    ),
)
@pytest.mark.experiments3(
    name='crypta_audience',
    consumers=['eats-communications/eats-promotions-banner'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'audience_segments',
                    'set_elem_type': 'int',
                    'value': 1021,
                },
                'type': 'contains',
            },
            'value': {'enabled': True},
        },
    ],
)
async def test_bigb(taxi_eats_communications, mockserver, testpoint):
    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert 'experiment:crypta_audience' in request.json['channels']
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'brand', 'brands': [1]},
                    'priority': 10,
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
            },
        )

    @testpoint('eats-bigb:parse_profile')
    def bigb_parse(data):
        assert data['passport_uid'] == '12341212'

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-Eats-User': (
                'user_id=test_eats_user_id,'
                'personal_phone_id=test_pesonal_phone_id,'
            ),
            'x-yandex-uid': '12341212',
        },
        json={'latitude': 55.749953, 'longitude': 37.534143},
    )

    assert response.status_code == 200
    assert feeds.times_called == 1
    assert bigb_parse.times_called == 1


@experiments.feed('placeholder')
@pytest.mark.now('2022-01-02T03:00:00+03:00')
@pytest.mark.bigb(
    eats_bigb.Profile(
        passport_uid='12341212',
        audience_segments={1, 100, 2, 1021},
        heuristic_segments={112},
    ),
)
async def test_kwargs(taxi_eats_communications, mockserver, experiments3):

    recorder = experiments3.record_match_tries('placeholder')

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v1/user-tags',
    )
    def grocery_tags(request):
        assert request.json == {
            'eats_user_id': 'test_eats_user_id',
            'personal_phone_id': 'test_pesonal_phone_id',
        }
        return {'is_new_user': True}

    @mockserver.json_handler('/corp-users/v1/users-limits/eats/fetch')
    def corp_users(request):
        assert request.headers['X-Yandex-UID'] == '12341212'
        assert request.headers['X-YaTaxi-User'] == 'eats_user_id=12345'
        assert request.headers['X-YaTaxi-Pass-Flags'] == 'portal,ya-plus'
        return {
            'users': [
                {
                    'id': 'corp_user_id_1',
                    'client_id': 'corp_client_id_1',
                    'client_name': 'Corp Client 1',
                    'limits': [],
                },
                {
                    'id': 'corp_user_id_2',
                    'client_id': 'corp_client_id_2',
                    'client_name': 'Corp Client 2',
                    'limits': [],
                },
            ],
        }

    @mockserver.json_handler('/eda-delivery-price/v1/user-promo')
    def eda_delivery_price(_):
        return {
            'is_eda_new_user': True,
            'is_retail_new_user': True,
            'tags': ['tag1', 'tag2'],
        }

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        return utils.make_feeds()

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-Eats-User': (
                'user_id=test_eats_user_id,'
                'personal_phone_id=test_pesonal_phone_id,'
            ),
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'session',
            'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
            'x-yandex-uid': '12341212',
        },
        json={'latitude': 55.749953, 'longitude': 37.534143},
    )

    assert response.status_code == 200
    assert feeds.times_called == 1
    assert eda_delivery_price.times_called == 1
    assert grocery_tags.times_called == 1
    assert corp_users.times_called == 1

    match_tries = await recorder.get_match_tries(ensure_ntries=1)

    assert match_tries[0].kwargs == {
        'application': 'eda_ios_app',
        'audience_segments': utils.MatchingSet([1, 100, 2, 1021]),
        'cgroups': matching.IsInstance(list),
        'client_location': [37.534143, 55.749953],
        'consumer': 'eats-communications/eats-promotions-banner',
        'day_of_week': 7,
        'device_id': 'test_device',
        'eats_id': 'test_eats_user_id',
        'has_plus_cashback': False,
        'has_ya_plus': True,
        'heuristic_segments': utils.MatchingSet([112]),
        'host': matching.AnyString(),
        'hour': 3,
        'is_authorized': True,
        'is_eda_new_user': True,
        'is_grocery_new_user': True,
        'is_map_available': True,
        'is_prestable': False,
        'is_retail_new_user': True,
        'location': [37.534143, 55.749953],
        'ngroups': matching.IsInstance(list),
        'personal_phone_id': 'test_pesonal_phone_id',
        'platform': 'eda_ios_app',
        'request_timestamp': matching.IsInstance(int),
        'request_timestamp_minutes': matching.IsInstance(int),
        'show_time_hour': 3,
        'show_time_weekday': 7,
        'timezone': 'Europe/Moscow',
        'user_promo_tags': utils.MatchingSet(['tag1', 'tag2']),
        'version': '5.4.0',
        'yandex_uid': '12341212',
        'corp_user_ids': utils.MatchingSet(
            ['corp_user_id_1', 'corp_user_id_2'],
        ),
        'corp_client_ids': utils.MatchingSet(
            ['corp_client_id_1', 'corp_client_id_2'],
        ),
    }
