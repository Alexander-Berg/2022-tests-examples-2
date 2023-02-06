# pylint: disable=C0302
# pylint: disable=import-error
from eats_analytics import eats_analytics  # noqa: F401
from eats_catalog_predicate import eats_catalog_predicate  # noqa: F401
import pytest

from testsuite.utils import matching

from . import experiments
from . import utils


FEEDS_SERVICE = 'eats-promotions-banner'


def feed_for_device_id(feed: str, device_id: str):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name=feed,
        consumers=['eats-communications/eats-promotions-banner'],
        clauses=[
            {
                'title': 'match_device_id',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'device_id',
                        'arg_type': 'string',
                        'value': device_id,
                    },
                },
            },
        ],
    )


FEED_TEST_DEVICE = feed_for_device_id('feed_1', 'test_device')


USE_EATS_CATALOG = pytest.mark.experiments3(
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


@pytest.mark.parametrize(
    'autoscale_mode',
    [
        pytest.param('disabled'),
        pytest.param('client', marks=experiments.ENABLE_AUTOSCALING),
    ],
)
@pytest.mark.parametrize(
    'feeds,banners',
    [
        pytest.param({}, [], id='empty'),
        pytest.param(
            utils.make_feeds_payload(
                {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'info'},
                    'url': 'http://yandex.ru',
                    'appLink': 'http://yandex.ru/mobile',
                    'priority': 10,
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
            ),
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
            utils.make_feeds_payload(
                {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'info'},
                    'url': 'http://yandex.ru',
                    'appLink': 'http://yandex.ru/mobile',
                    'priority': 10,
                    'images': [
                        {
                            'url': 'beautiful_pic.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
                {
                    'banner_id': 2,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'info'},
                    'url': 'http://yandex.com',
                    'appLink': 'http://yandex.com/mobile',
                    'priority': 100,
                    'images': [
                        {
                            'url': 'beautiful_pic.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
            ),
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
@feed_for_device_id('feed_1', 'test_device')
@feed_for_device_id('feed_2', 'super_device')
@feed_for_device_id('feed_3', 'test_device')
async def test_response(
        taxi_eats_communications, mockserver, feeds, banners, autoscale_mode,
):
    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _communications(request):
        return mockserver.make_response(json={}, status=500)

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        assert request.json['service'] == FEEDS_SERVICE
        assert request.json['channels'] == [
            'experiment:feed_1',
            'experiment:feed_3',
        ]
        assert request.json['media_info']['autoscale_mode'] == autoscale_mode
        return feeds

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


@pytest.mark.parametrize('show_counter', [True, False])
@FEED_TEST_DEVICE
async def test_filter_collection_banners(
        taxi_eats_communications, mockserver, show_counter,
):
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

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        return utils.make_feeds_payload(
            {
                'banner_id': 1,
                'experiment': 'feed_1',
                'recipients': {
                    'type': 'collection',
                    'collections': ['collection_1'],
                    'hide_counter': not show_counter,
                },
                'url': '/',
                'app_url': '/',
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            {
                'banner_id': 2,
                'experiment': 'feed_1',
                'recipients': {
                    'type': 'collection',
                    'collections': ['collection_10'],
                },
                'url': 'http://yandex.ru',
                'app_url': 'http://yandex.ru/mobile',
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            {
                'banner_id': 3,
                'experiment': 'feed_1',
                'recipients_type': 'brand',
                'recipients': {'brands': [10]},
                'url': 'http://yandex.ru',
                'app_url': 'http://yandex.ru/mobile',
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
                'payload': {'badge': {'counter': 10} if show_counter else {}},
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


@pytest.mark.parametrize(
    'expected_banners',
    [
        pytest.param(
            [
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
                        'meta': {
                            'analytics': eats_analytics.encode(
                                eats_analytics.AnalyticsContext(item_id='3'),
                            ),
                        },
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
                        'meta': {
                            'analytics': eats_analytics.encode(
                                eats_analytics.AnalyticsContext(item_id='1'),
                            ),
                        },
                    },
                },
            ],
            id='eda-catalog',
        ),
        pytest.param(
            [
                {
                    'id': 3,
                    'kind': 'brand',
                    'formats': ['classic'],
                    'brand_id': 1,
                    'payload': {
                        'id': 3,
                        'kind': 'brand',
                        'url': utils.URL_ROOT + '/restaurant/place_1',
                        'appLink': 'eda.yandex://restaurant/place_1',
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
                        'meta': {
                            'analytics': eats_analytics.encode(
                                eats_analytics.AnalyticsContext(item_id='3'),
                            ),
                        },
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
                        'meta': {
                            'analytics': eats_analytics.encode(
                                eats_analytics.AnalyticsContext(item_id='1'),
                            ),
                        },
                    },
                },
            ],
            marks=USE_EATS_CATALOG,
            id='eats-catalog',
        ),
    ],
)
@FEED_TEST_DEVICE
async def test_place_brand_banners(
        taxi_eats_communications, mockserver, expected_banners,
):
    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _eda_banner_places(request):
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

    @mockserver.json_handler('/eats-catalog/internal/v1/places')
    def _eats_banner_places(request):
        return {
            'blocks': [
                {
                    'id': '__open',
                    'list': [
                        {
                            'id': '1',
                            'slug': 'place_1',
                            'brand': {
                                'id': '1',
                                'slug': 'brand_1',
                                'business': 'restaurant',
                                'name': '1',
                                'logo': {
                                    'light': [
                                        {
                                            'size': 'large',
                                            'logo_url': 'logo_url',
                                        },
                                    ],
                                    'dark': [
                                        {
                                            'size': 'large',
                                            'logo_url': 'logo_url',
                                        },
                                    ],
                                },
                            },
                        },
                    ],
                    'stats': {'places_count': 1},
                },
            ],
        }

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        return utils.make_feeds_payload(
            {
                'banner_id': 1,
                'experiment': 'feed_1',
                'recipients': {'type': 'restaurant', 'places': [1]},
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            {
                'banner_id': 2,
                'experiment': 'feed_1',
                'recipients': {'type': 'restaurant', 'places': [2]},
                'priority': 15,
                'shortcuts': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            {
                'banner_id': 3,
                'experiment': 'feed_1',
                'recipients': {'type': 'brand', 'brands': [1]},
                'priority': 20,
                'images': [
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
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert response.status_code == 200
    assert response.json()['payload']['banners'] == expected_banners


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='eda-catalog'),
        pytest.param(marks=USE_EATS_CATALOG, id='eats-catalog'),
    ],
)
@FEED_TEST_DEVICE
async def test_deduplicate(taxi_eats_communications, mockserver):
    """
    Проверяем, что если включен и инап и фидс
    для дубликатов по banner_id придет
    баннер из inapp
    """

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

    @mockserver.json_handler('/eats-catalog/internal/v1/places')
    def _eats_banner_places(request):
        return {
            'blocks': [
                {
                    'id': '__open',
                    'list': [
                        {
                            'id': '1',
                            'slug': 'place_1',
                            'brand': {
                                'id': '1',
                                'slug': 'brand_1',
                                'business': 'restaurant',
                                'name': '1',
                                'logo': {
                                    'light': [
                                        {
                                            'size': 'large',
                                            'logo_url': 'logo_url',
                                        },
                                    ],
                                    'dark': [
                                        {
                                            'size': 'large',
                                            'logo_url': 'logo_url',
                                        },
                                    ],
                                },
                            },
                        },
                    ],
                    'stats': {'places_count': 1},
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
                                        'url': 'BANNER_FROM_INAPP.png',
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

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        return utils.make_feeds_payload(
            {
                'banner_id': 1,
                'experiment': 'feed_1',
                'recipients': {'type': 'restaurant', 'places': [1]},
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
                        'url': 'BANNER_FROM_INAPP.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
                'meta': {'analytics': matching.AnyString()},
            },
        },
    ]


@experiments.has_ya_plus(
    'only_plus', ['eats-communications/eats-promotions-banner'],
)
async def test_banner_has_ya_plus(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert 'experiment:only_plus' in request.json['channels']
        return {
            'polling_delay': 30,
            'etag': '5b750d8bbe805737aead72de77ebf7da',
            'feed': [],
        }

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'session',
            'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
        },
        json={'latitude': 0, 'longitude': 0},
    )
    assert feeds.times_called == 1
    assert response.status_code == 200


MAP_BANNER_EXP = 'eda_map_pickup_banner'
MAP_FALLBACK_NAME = 'eats-communications.map.fallback'


@pytest.mark.config(
    EATS_COMMUNICATIONS_MAP_FALLBACK={
        'service': 'userver@eats-layout-constructor',
        'fallback': MAP_FALLBACK_NAME,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name=MAP_BANNER_EXP,
    consumers=['eats-communications/eats-promotions-banner'],
    clauses=[
        {
            'title': 'match',
            'value': {'enabled': True},
            'predicate': {
                'init': {
                    'value': True,
                    'arg_name': 'is_map_available',
                    'arg_type': 'bool',
                },
                'type': 'eq',
            },
        },
    ],
)
@pytest.mark.parametrize('fallback_fired', [True, False])
async def test_is_map_available(
        taxi_eats_communications, mockserver, statistics, fallback_fired,
):
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
                ],
            },
        }

    banner_id = 1

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert request.json['channels'] == [f'experiment:{MAP_BANNER_EXP}']
        return utils.make_feeds_payload(
            {
                'banner_id': banner_id,
                'experiment': MAP_BANNER_EXP,
                'recipients': {
                    'type': 'collection',
                    'collections': ['collection_1'],
                },
                'url': 'http://yandex.ru',
                'app_url': 'http://yandex.ru/mobile',
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

    if fallback_fired:
        statistics.fallbacks = [MAP_FALLBACK_NAME]
        await taxi_eats_communications.invalidate_caches()

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 0, 'longitude': 0},
    )

    assert feeds.times_called == (not fallback_fired)
    assert response.status_code == 200

    payload_banners = response.json()['payload']['banners']
    if fallback_fired:
        assert not payload_banners
    else:
        assert payload_banners[0]['id'] == banner_id


@USE_EATS_CATALOG
@FEED_TEST_DEVICE
@pytest.mark.collection(
    slug='testsuite',
    title='testsuite collection',
    strategy=eats_catalog_predicate.Strategy.by_brand_id,
    args=eats_catalog_predicate.BrandArgs(brand_ids=[737]),
)
@pytest.mark.collection(
    slug='testsuite_empty',
    title='testsuite collection',
    strategy=eats_catalog_predicate.Strategy.by_place_id,
    args=eats_catalog_predicate.PlaceArgs(place_ids=[1031]),
)
@pytest.mark.now('2022-07-08T16:58:50+03:00')
async def test_pseudo_collector(
        taxi_eats_communications, eats_catalog, mockserver,
):
    any_shipping = {
        'predicates': [
            {
                'init': {
                    'arg_name': 'shipping_types',
                    'arg_type': 'string',
                    'value': 'pickup',
                },
                'type': 'contains',
            },
            {
                'init': {
                    'arg_name': 'shipping_types',
                    'arg_type': 'string',
                    'value': 'delivery',
                },
                'type': 'contains',
            },
        ],
        'type': 'any_of',
    }

    @mockserver.json_handler('/eats-catalog/internal/v1/places')
    def places(request):
        assert request.json == {
            'blocks': [
                {'id': '__open', 'no_data': False, 'type': 'open'},
                {'id': '__closed', 'no_data': False, 'type': 'closed'},
                {
                    'condition': {
                        'predicates': [
                            any_shipping,
                            {
                                'init': {
                                    'arg_name': 'brand_id',
                                    'set': [737],
                                    'set_elem_type': 'int',
                                },
                                'type': 'in_set',
                            },
                        ],
                        'type': 'all_of',
                    },
                    'id': 'testsuite',
                    'no_data': True,
                    'type': 'any',
                },
                {
                    'condition': {
                        'predicates': [
                            any_shipping,
                            {
                                'init': {
                                    'arg_name': 'place_id',
                                    'set': [1031],
                                    'set_elem_type': 'int',
                                },
                                'type': 'in_set',
                            },
                        ],
                        'type': 'all_of',
                    },
                    'id': 'testsuite_empty',
                    'no_data': True,
                    'type': 'any',
                },
            ],
            'enable_deduplication': False,
            'delivery_time': {'time': '2022-07-08T13:58:50+00:00', 'zone': 0},
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'shipping_type': 'delivery',
        }

        return {
            'blocks': [
                {'id': '__open', 'list': [], 'stats': {'places_count': 0}},
                {'id': '__closed', 'list': [], 'stats': {'places_count': 0}},
                {
                    'id': 'testsuite',
                    'list': [],
                    'stats': {'places_count': 202},
                },
                {
                    'id': 'testsuite_empty',
                    'list': [],
                    'stats': {'places_count': 0},
                },
            ],
        }

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        return utils.make_feeds_payload(
            {
                'banner_id': 1,
                'experiment': 'feed_1',
                'recipients': {
                    'type': 'collection',
                    'collections': ['testsuite'],
                },
                'priority': 10,
                'wide_and_short': [
                    {
                        'url': 'beautiful_pic.png',
                        'theme': 'light',
                        'platform': 'web',
                    },
                ],
            },
            {
                'banner_id': 2,
                'experiment': 'feed_1',
                'recipients': {
                    'type': 'collection',
                    'collections': ['testsuite_empty'],
                },
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
        },
        json={'latitude': 0, 'longitude': 0},
    )

    assert response.status_code == 200
    assert places.times_called == 1

    data = response.json()
    assert data['payload']['banners'] == [
        {
            'collection_slug': 'testsuite',
            'formats': ['wide_and_short'],
            'id': 1,
            'kind': 'collection',
            'payload': {
                'appLink': 'eda.yandex://collections/testsuite',
                'id': 1,
                'images': [],
                'kind': 'collection',
                'meta': {'analytics': matching.any_string},
                'payload': {'badge': {'counter': 202}},
                'shortcuts': [],
                'url': '/collections/testsuite',
                'wide_and_short': [
                    {
                        'platform': 'web',
                        'theme': 'light',
                        'url': 'beautiful_pic.png',
                    },
                ],
            },
        },
    ]
