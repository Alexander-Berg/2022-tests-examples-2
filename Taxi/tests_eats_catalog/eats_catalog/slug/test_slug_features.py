import datetime

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage


NOW = parser.parse('2021-01-01T12:00:00+00:00')


def fill_storage(eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            launched_at=NOW - datetime.timedelta(days=5),
            features=storage.Features(
                constraints=[
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderPrice, 50000,
                    ),
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderWeight, 12,
                    ),
                ],
            ),
            timing=storage.PlaceTiming(extra_preparation=60.0),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )


@pytest.mark.parametrize(
    'headers, plus_request_expected, plus_response,'
    'plus_response_code, plus_count_called, '
    'features_plus_expected, shipping_type',
    [
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
            },
            {
                'place_id': 1,
                'yandex_uid': 'testsuite',
                'shipping_type': 'delivery',
            },
            {
                'cashback': 77.777,
                'title': 'Рандомный процент:',
                'description': 'вернется баллами на Яндекс.Плюс',
                'icon_url': 'http://localhost/icon',
                'plus_details_form': {
                    'title': 'ДЕТАЛИ',
                    'description': 'Бла-бла',
                    'button': {
                        'title': 'жмак',
                        'deeplink': 'http://localhost',
                    },
                    'image_url': 'http://image-url.com',
                    'background': {'styles': {'rainbow': True}},
                },
            },
            200,
            1,
            {
                'cashback': '77.777%',
                'title': 'Рандомный процент:',
                'description': 'вернется баллами на Яндекс.Плюс',
                'iconUrl': 'http://localhost/icon',
                'extended': {
                    'title': 'ДЕТАЛИ',
                    'description': 'Бла-бла',
                    'button': {
                        'title': 'жмак',
                        'deeplink': 'http://localhost',
                    },
                    'image_url': 'http://image-url.com',
                    'background': {'styles': {'rainbow': True}},
                },
            },
            'delivery',
            id='double cashback',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
            },
            {
                'place_id': 1,
                'yandex_uid': 'testsuite',
                'shipping_type': 'delivery',
            },
            {
                'cashback': 99,
                'title': 'Рандомный процент:',
                'description': 'вернется баллами на Яндекс.Плюс',
                'icon_url': 'http://localhost/icon',
                'plus_details_form': {
                    'title': 'ДЕТАЛИ',
                    'description': 'Бла-бла',
                    'button': {
                        'title': 'жмак',
                        'deeplink': 'http://localhost',
                    },
                    'background': {'styles': {'rainbow': False}},
                },
            },
            200,
            1,
            {
                'cashback': '99%',
                'title': 'Рандомный процент:',
                'description': 'вернется баллами на Яндекс.Плюс',
                'iconUrl': 'http://localhost/icon',
                'extended': {
                    'title': 'ДЕТАЛИ',
                    'description': 'Бла-бла',
                    'button': {
                        'title': 'жмак',
                        'deeplink': 'http://localhost',
                    },
                    'background': {'styles': {'rainbow': False}},
                },
            },
            'delivery',
            id='integer cashback',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
            },
            {
                'place_id': 1,
                'yandex_uid': 'testsuite',
                'shipping_type': 'pickup',
            },
            {
                'cashback': 0.0001,
                'title': 'Попробуй быть курьером сам',
                'description': 'хочешь есть - иди сам',
                'icon_url': 'http://localhost/icon',
                'plus_details_form': {
                    'title': 'Самовывоз',
                    'description': 'Бла-бла',
                    'button': {
                        'title': 'жмак',
                        'deeplink': 'http://localhost',
                    },
                },
            },
            200,
            1,
            {
                'cashback': '0.0001%',
                'title': 'Попробуй быть курьером сам',
                'description': 'хочешь есть - иди сам',
                'iconUrl': 'http://localhost/icon',
                'extended': {
                    'title': 'Самовывоз',
                    'description': 'Бла-бла',
                    'button': {
                        'title': 'жмак',
                        'deeplink': 'http://localhost',
                    },
                },
            },
            'pickup',
            id='pickup',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
            },
            {
                'place_id': 1,
                'yandex_uid': 'testsuite',
                'shipping_type': 'delivery',
            },
            None,
            404,
            1,
            None,
            'delivery',
            id='no cashback',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
            },
            {
                'place_id': 1,
                'yandex_uid': 'testsuite',
                'shipping_type': 'delivery',
            },
            None,
            500,
            1,
            None,
            'delivery',
            id='error',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
            },
            None,
            None,
            None,
            0,
            None,
            'delivery',
            id='no yandex_uid',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat('T'))
async def test_slug_features_yandex_plus(
        slug,
        eats_user_reactions_400,
        mockserver,
        eats_catalog_storage,
        headers,
        plus_request_expected,
        plus_response,
        plus_response_code,
        plus_count_called,
        features_plus_expected,
        shipping_type,
):
    fill_storage(eats_catalog_storage)

    @mockserver.handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/place',
    )
    def eats_plus(request):
        assert request.headers['X-Device-Id'] == headers['x-device-id']
        assert request.method == 'POST'
        assert request.json == plus_request_expected

        if plus_response is None:
            return mockserver.make_response(status=plus_response_code)

        return mockserver.make_response(json=plus_response)

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'shippingType': shipping_type,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert eats_plus.times_called == plus_count_called

    features = response.json()['payload']['foundPlace']['place']['features']

    assert features['yandexPlus'] == features_plus_expected


@experiments.ENABLE_FAVORITES
@pytest.mark.parametrize(
    'headers, params, reactions_request_expected, reactions_response,'
    'reactions_response_code, reactions_count_called,'
    'features_favorite_expected',
    [
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
                'X-Eats-User': 'user_id=333',
            },
            {'latitude': 55.802998, 'longitude': 37.591503},
            {
                'eater_id': '333',
                'pagination': {'limit': 1000},
                'subject_namespaces': ['catalog_brand'],
            },
            {
                'reactions': [
                    {
                        'subject': {'id': '1', 'namespace': 'catalog_brand'},
                        'created_at': '2021-01-01T13:00:00+03:00',
                    },
                ],
                'pagination': {'cursor': '1', 'has_more': False},
            },
            200,
            1,
            {'isFavorite': True},
            id='is favorite',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
                'X-Eats-User': 'user_id=333',
            },
            {'latitude': 55.802998, 'longitude': 37.591503},
            {
                'eater_id': '333',
                'pagination': {'limit': 1000},
                'subject_namespaces': ['catalog_brand'],
            },
            {
                'reactions': [
                    {
                        'subject': {'id': '2', 'namespace': 'catalog_brand'},
                        'created_at': '2021-01-01T13:00:00+03:00',
                    },
                ],
                'pagination': {'cursor': '1', 'has_more': False},
            },
            200,
            1,
            {'isFavorite': False},
            id='is not favorite',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
                'X-Eats-User': 'user_id=333',
            },
            {'latitude': 55.802998, 'longitude': 37.591503},
            {
                'eater_id': '333',
                'pagination': {'limit': 1000},
                'subject_namespaces': ['catalog_brand'],
            },
            None,
            400,
            1,
            None,
            id='error',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
                'x-yandex-uid': 'testsuite',
                'X-Eats-User': 'user_id=333',
            },
            None,
            None,
            None,
            None,
            0,
            None,
            id='no position',
        ),
        pytest.param(
            {
                'x-device-id': 'test_simple',
                'x-platform': 'superapp_taxi_web',
                'x-app-version': '1.12.0',
            },
            {'latitude': 55.802998, 'longitude': 37.591503},
            None,
            None,
            None,
            0,
            {'isFavorite': False},
            id='no eater_id',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat('T'))
async def test_slug_features_favourite(
        taxi_eats_catalog,
        eats_plus_404,
        mockserver,
        eats_catalog_storage,
        headers,
        params,
        reactions_request_expected,
        reactions_response,
        reactions_response_code,
        reactions_count_called,
        features_favorite_expected,
):

    fill_storage(eats_catalog_storage)

    @mockserver.handler(
        '/eats-user-reactions/eats-user-reactions/v1/favourites/find-by-eater',
    )
    def eats_user_reactions(request):
        assert request.method == 'POST'
        assert request.json == reactions_request_expected

        if reactions_response is None:
            return mockserver.make_response(status=reactions_response_code)

        return mockserver.make_response(json=reactions_response)

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/coffee_boy_novodmitrovskaya_2k6',
        params=params,
        headers=headers,
    )

    assert response.status_code == 200
    assert eats_user_reactions.times_called == reactions_count_called

    features = response.json()['payload']['foundPlace']['place']['features']

    assert features['favorite'] == features_favorite_expected


@pytest.mark.now(NOW.isoformat('T'))
async def test_slug_features_favourite_experiment_disabled(
        slug, eats_plus_404, eats_catalog_storage,
):
    fill_storage(eats_catalog_storage)

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 55.802998, 'longitude': 37.591503},
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'x-yandex-uid': 'testsuite',
            'X-Eats-User': 'user_id=333',
        },
    )

    assert response.status_code == 200

    features = response.json()['payload']['foundPlace']['place']['features']

    assert features['favorite'] is None


BADGE_DEFAULT_COLOR = 'lightgray'

BADGE_DEFAULT_COLOR_PAIR = [
    {'theme': 'dark', 'value': BADGE_DEFAULT_COLOR},
    {'theme': 'light', 'value': BADGE_DEFAULT_COLOR},
]

CLOSE_NOTIFICATION = experiments.always_match(
    name='eats_catalog_close_notify',
    is_config=True,
    consumer='eats-catalog-close-notify-badge',
    value={
        'menu_badge': {
            'enabled': True,
            'notify_interval': 30,
            'icon_url': 'http://close_icon',
            'text_key': 'test.badge.close_notify',
            'text_color': BADGE_DEFAULT_COLOR_PAIR,
            'background_color': BADGE_DEFAULT_COLOR_PAIR,
            'button_text_key': 'text.badge.close_notification_button',
            'url': 'http://none',
        },
    },
)

CLOSE_NOTIFICATION_TRANSLATION = pytest.mark.translations(
    **{
        'eats-catalog': {
            'test.badge.close_notify': {
                'ru': [
                    '%(minutes)s минута до закрытия',
                    '%(minutes)s минуты до закрытия',
                    '%(minutes)s минут до закрытия',
                    '%(minutes)s минут до закрытия',
                ],
            },
            'text.badge.close_notification_button': {'ru': 'Шмак'},
        },
    },
)


@pytest.mark.parametrize(
    'text',
    [
        pytest.param(
            None,
            id='no badge',
            marks=pytest.mark.now('2022-02-07T22:32:00+03:00'),
        ),
        pytest.param(
            None,
            marks=(
                pytest.mark.now('2022-02-07T22:32:00+03:00'),
                CLOSE_NOTIFICATION,
            ),
            id='no translation',
        ),
        pytest.param(
            '18 минут до закрытия',
            marks=(
                pytest.mark.now('2022-02-07T22:32:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='badge',
        ),
        pytest.param(
            '1 минута до закрытия',
            marks=(
                pytest.mark.now('2022-02-07T22:49:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='badge',
        ),
        pytest.param(
            None,
            marks=(
                pytest.mark.now('2022-02-07T23:32:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='after close',
        ),
        pytest.param(
            None,
            marks=(
                pytest.mark.now('2022-02-07T20:00:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='long before close',
        ),
    ],
)
async def test_special_project_close_notify(slug, eats_catalog_storage, text):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='test_place',
            brand=storage.Brand(brand_id=1),
            timing=storage.PlaceTiming(average_preparation=10 * 60),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-02-07T00:00:00+03:00'),
                    end=parser.parse('2022-02-07T23:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'test_place',
        query={'latitude': 55.802998, 'longitude': 37.591503},
        headers={'x-yandex-uid': 'testsuite', 'X-Eats-User': 'user_id=333'},
    )

    assert response.status_code == 200

    data = response.json()
    place = data['payload']['foundPlace']

    banner = place.get('specialProjectBanner', None)
    if text is None:
        assert banner is None
    else:
        assert banner == {
            'icon': {'url': 'http://close_icon', 'width': 'single'},
            'text': {'color': BADGE_DEFAULT_COLOR_PAIR, 'text': text},
            'backgroundColor': BADGE_DEFAULT_COLOR_PAIR,
            'url': 'http://none',
            'buttonText': 'Шмак',
            'projectTag': 'close_notification',
        }
