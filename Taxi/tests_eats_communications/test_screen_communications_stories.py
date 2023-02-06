import copy

import pytest

from testsuite.utils import matching

from . import experiments
from . import utils

EXP_NAME = 'stories_experiment'
SCREEN = 'shop_main_page'
PLACE_BUSINESS_TYPE = 'shop'
EATER_ID = '12345'
DEVICE_ID = 'test_device'
PLACE_ID = '123'
BRAND_ID = '12'
TYPE = 'stories'
FEED_IDS = [
    '333c69c8afe947ba887fd6404428b31c',
    '333c69c8afe947ba887fd6404428b31d',
    '333c69c8afe947ba887fd6404428b31e',
]


def preview_to_offer(preview: dict, shortcut_id: str) -> dict:
    result = copy.deepcopy(preview)
    result['subtitle'] = result.pop('text')
    result['shortcut_id'] = shortcut_id
    return result


def communications_config(brand_orders_count_request_enabled: bool):
    return pytest.mark.config(
        EATS_COMMUNICATIONS_COMMUNICATIONS_SETTINGS={
            'brand_orders_count_request_enabled': (
                brand_orders_count_request_enabled
            ),
        },
    )


@pytest.mark.parametrize(
    'max_stories',
    [
        pytest.param(
            1, marks=experiments.stories_limit_settings(max_screen_stories=1),
        ),
        pytest.param(
            2, marks=experiments.stories_limit_settings(max_screen_stories=2),
        ),
        pytest.param(
            3, marks=experiments.stories_limit_settings(max_screen_stories=3),
        ),
        pytest.param(
            100,
            marks=experiments.stories_limit_settings(max_screen_stories=100),
        ),
    ],
)
@experiments.screen_stories(EXP_NAME)
@communications_config(brand_orders_count_request_enabled=True)
async def test_screen_communications_stories(
        taxi_eats_communications, mockserver, max_stories,
):
    """
    Проверяет логику работы ручки /internal/v1/screen/communications
    1) Ходит в эксы по консьюмеру, передает в кварги
    контекст пользователя из запроса и статистику заказов в ретейле
    из order_stats
    2) Ходит в feeds за сторизами по полученным каналам
    и сервису
    3) Сортирует сторизы в соответствии с приоритетом
    4) Ограничивает количество сториз в соответствии с конфигом
    5) Формирует ответ
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        utils.assert_feeds_channels(request, [EXP_NAME], EATER_ID, DEVICE_ID)
        return utils.make_fetch_stories_response(
            [
                {'id': FEED_IDS[0], 'priority': 1},
                {'id': FEED_IDS[1], 'priority': 3},
                {'id': FEED_IDS[2], 'priority': 2},
            ],
        )

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        return utils.make_eats_orders_stats_response(
            request, EATER_ID, BRAND_ID, 1, 2,
        )

    request_body = {
        'types': [TYPE],
        'screen': SCREEN,
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
        'position': {'lat': 1.0, 'lon': 2.0},
    }

    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID}',
            'X-App-Version': '5.27.1',
            'X-Device-Id': DEVICE_ID,
        },
        json=request_body,
    )

    assert order_stats.times_called == 1

    assert feeds.times_called == 1
    assert response.status_code == 200
    payload = response.json()['payload']

    expected_payload = [
        {
            'offer': preview_to_offer(utils.STORY_PREVIEW, FEED_IDS[1]),
            'pages': utils.STORY_PAGES,
        },
        {
            'offer': preview_to_offer(utils.STORY_PREVIEW, FEED_IDS[2]),
            'pages': utils.STORY_PAGES,
        },
        {
            'offer': preview_to_offer(utils.STORY_PREVIEW, FEED_IDS[0]),
            'pages': utils.STORY_PAGES,
        },
    ]
    assert payload['stories'] == expected_payload[:max_stories]
    assert payload['informers'] == []


@pytest.mark.parametrize('brand_id', [None, BRAND_ID])
@pytest.mark.parametrize('place_id', [None, PLACE_ID])
@pytest.mark.parametrize('location', [None, [2.0, 1.0]])
@pytest.mark.parametrize('retail_orders_count', [4, 5])
@pytest.mark.parametrize('brand_orders_count', [1, 2])
@pytest.mark.parametrize(
    'brand_orders_count_enabled',
    [
        pytest.param(
            False,
            marks=communications_config(
                brand_orders_count_request_enabled=False,
            ),
        ),
        pytest.param(
            True,
            marks=communications_config(
                brand_orders_count_request_enabled=True,
            ),
        ),
    ],
)
@experiments.always_match(
    'placeholder', 'eats-communications/screen-stories', {'enabled': True},
)
async def test_screen_communications_stories_kwargs(
        taxi_eats_communications,
        mockserver,
        experiments3,
        place_id,
        brand_id,
        location,
        retail_orders_count,
        brand_orders_count,
        brand_orders_count_enabled,
):
    """
    Проверяет кварги сториз в ручке
    /internal/v1/screen/communications
    """
    recorder = experiments3.record_match_tries('placeholder')

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        return utils.make_feeds()

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        return utils.make_eats_orders_stats_response(
            request,
            EATER_ID,
            brand_id,
            retail_orders_count,
            brand_orders_count,
        )

    request_body = {
        'types': [TYPE],
        'screen': SCREEN,
        'place_id': place_id,
        'brand_id': brand_id,
    }
    if location is not None:
        request_body['position'] = {'lon': location[0], 'lat': location[1]}
    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID},',
            'X-App-Version': '5.27.1',
            'X-Platform': 'eda_ios_app',
            'X-Device-Id': 'some_device',
        },
        json=request_body,
    )

    assert response.status_code == 200
    assert feeds.times_called == 1
    assert order_stats.times_called == (1 if brand_orders_count_enabled else 0)

    match_tries = await recorder.get_match_tries(ensure_ntries=1)
    location = location or [0, 0]
    expected_kwargs = {
        'application': 'eda_ios_app',
        'cgroups': matching.IsInstance(list),
        'client_location': location,
        'consumer': 'eats-communications/screen-stories',
        'device_id': 'some_device',
        'eats_id': str(EATER_ID),
        'has_plus_cashback': False,
        'has_ya_plus': False,
        'host': matching.AnyString(),
        'is_authorized': True,
        'is_prestable': False,
        'location': location,
        'ngroups': matching.IsInstance(list),
        'platform': 'eda_ios_app',
        'request_timestamp': matching.IsInstance(int),
        'request_timestamp_minutes': matching.IsInstance(int),
        'screen': 'shop_main_page',
        'version': '5.27.1',
    }
    if brand_id is not None:
        expected_kwargs['brand_id'] = brand_id
    if brand_id and brand_orders_count_enabled:
        expected_kwargs['brand_orders_count'] = brand_orders_count
    if brand_orders_count_enabled:
        expected_kwargs['retail_orders_count'] = retail_orders_count
    if place_id is not None:
        expected_kwargs['place_id'] = place_id
    assert match_tries[0].kwargs == expected_kwargs


@experiments.always_match(
    'placeholder', 'eats-communications/screen-stories', {'enabled': True},
)
@pytest.mark.parametrize(
    ['status_code', 'is_timeout'],
    [(400, False), (429, False), (500, False), (500, True)],
)
@communications_config(brand_orders_count_request_enabled=True)
async def test_screen_communications_stories_bad_stats_response(
        taxi_eats_communications,
        mockserver,
        experiments3,
        status_code,
        is_timeout,
):
    """
    Проверяет, что плохие ответы eats-orders-stats в ручке
    /internal/v1/screen/communications не приводят к 500,
    а поле retail_orders_count не прокидывается в экспы
    """
    recorder = experiments3.record_match_tries('placeholder')

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        return utils.make_feeds()

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        if is_timeout:
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=status_code)

    request_body = {
        'types': [TYPE],
        'screen': SCREEN,
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
        'position': {'lat': 1.0, 'lon': 2.0},
    }

    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID}',
            'X-App-Version': '5.27.1',
        },
        json=request_body,
    )

    match_tries = await recorder.get_match_tries(ensure_ntries=1)
    assert 'retail_orders_count' not in match_tries[0].kwargs
    assert 'brand_orders_count' not in match_tries[0].kwargs

    assert order_stats.times_called == 1

    assert feeds.times_called == 1
    assert response.status_code == 200
    payload = response.json()['payload']
    assert payload['stories'] == []
    assert payload['informers'] == []


async def test_screen_communications_stories_no_types(
        taxi_eats_communications,
):
    """
    Проверяет, что если не указаны типы коммуникаций
    /internal/v1/screen/communications возвращает 400
    """
    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID},',
            'X-App-Version': '5.27.1',
            'X-Platform': 'eda_ios_app',
            'X-Device-Id': 'some_device',
        },
        json={'types': [], 'screen': SCREEN},
    )

    assert response.status_code == 400


@experiments.screen_stories(EXP_NAME)
async def test_screen_communications_stories_filter(
        taxi_eats_communications, mockserver,
):
    """
    Проверяет логику фильтрации просмотренных стори
    в ручке /internal/v1/screen/communications
    1) Если статус viewed, то стори не вернется
    2) В остальных статусах или при отсутствии стори вернется
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert f'experiment:{EXP_NAME}' in request.json['channels']
        return utils.make_fetch_stories_response(
            [
                # Просмотрена -> не вернется в ответе
                {'id': FEED_IDS[0], 'priority': 1, 'status': 'viewed'},
                # Вернутся в ответе
                {'id': FEED_IDS[1], 'priority': 2, 'status': 'published'},
                {'id': FEED_IDS[2], 'priority': 1, 'status': None},
            ],
        )

    request_body = {
        'types': [TYPE],
        'screen': SCREEN,
        'place_id': PLACE_ID,
        'brand_id': BRAND_ID,
        'position': {'lat': 1.0, 'lon': 2.0},
    }

    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID}',
            'X-App-Version': '5.27.1',
        },
        json=request_body,
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    payload = response.json()['payload']

    assert payload['stories'] == [
        {
            'offer': preview_to_offer(utils.STORY_PREVIEW, FEED_IDS[1]),
            'pages': utils.STORY_PAGES,
        },
        {
            'offer': preview_to_offer(utils.STORY_PREVIEW, FEED_IDS[2]),
            'pages': utils.STORY_PAGES,
        },
    ]
    assert payload['informers'] == []
