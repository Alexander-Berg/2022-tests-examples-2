import copy

import pytest

from testsuite.utils import matching

from . import experiments
from . import utils


EXP_NAME = 'informers_experiment'
SCREEN = 'shop_main_page'
PLACE_BUSINESS_TYPE = 'shop'
EATER_ID = '12345'
DEVICE_ID = 'test_device'
PLACE_ID = '123'
BRAND_ID = '12'
TYPE = 'informers'
FEED_IDS = [
    '333c69c8afe947ba887fd6404428b31c',
    '333c69c8afe947ba887fd6404428b31d',
    '333c69c8afe947ba887fd6404428b31e',
    '333c69c8afe947ba887fd6404428b31f',
    '333c69c8afe947ba887fd6404428b31g',
]


def communications_config(brand_orders_count_request_enabled: bool):
    return pytest.mark.config(
        EATS_COMMUNICATIONS_COMMUNICATIONS_SETTINGS={
            'brand_orders_count_request_enabled': (
                brand_orders_count_request_enabled
            ),
        },
    )


@pytest.mark.parametrize(
    'max_informers',
    [
        pytest.param(
            1,
            marks=experiments.informers_limit_settings(max_screen_informers=1),
        ),
        pytest.param(
            2,
            marks=experiments.informers_limit_settings(max_screen_informers=2),
        ),
        pytest.param(
            3,
            marks=experiments.informers_limit_settings(max_screen_informers=3),
        ),
        pytest.param(
            100,
            marks=experiments.informers_limit_settings(
                max_screen_informers=100,
            ),
        ),
    ],
)
@experiments.informers(EXP_NAME)
@communications_config(brand_orders_count_request_enabled=True)
async def test_screen_communications_informers(
        taxi_eats_communications, mockserver, max_informers,
):
    """
    Проверяет логику работы ручки /internal/v1/screen/communications
    1) Ходит в эксы по консьюмеру, передает в кварги
    контекст пользователя из запроса
    2) Ходит в feeds за информерами по полученным каналам
    и сервису
    3) Сортирует информеры в соответствии с приоритетом
    4) Ограничивает количество информеров в соответствии с конфигом
    5) Формирует ответ
    """

    invalid_informer = copy.deepcopy(utils.INFORMER)
    invalid_informer['content']['text']['color']['dark'] = 'invalid_color'

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        utils.assert_feeds_channels(request, [EXP_NAME], EATER_ID, DEVICE_ID)
        return utils.make_fetch_informers_response(
            [
                {'id': FEED_IDS[0], 'priority': 1},
                {'id': FEED_IDS[1], 'priority': 3},
                {
                    'id': FEED_IDS[2],
                    'priority': 2,
                    'payload': utils.BACKGROUND_INFORMER,
                },
                {
                    'id': FEED_IDS[3],
                    'priority': 5,
                    'payload': invalid_informer,
                },
            ],
        )

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        return utils.make_eats_orders_stats_response(
            request, EATER_ID, BRAND_ID, 1, 2,
        )

    request_body = {'types': [TYPE], 'screen': SCREEN, 'brand_id': BRAND_ID}

    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID}',
            'X-App-Version': '5.27.1',
            'X-Device-Id': DEVICE_ID,
        },
        json=request_body,
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    assert order_stats.times_called == 1
    payload = response.json()['payload']

    expected_payload = [
        utils.format_informer(utils.INFORMER, FEED_IDS[1]),
        utils.format_informer(utils.BACKGROUND_INFORMER, FEED_IDS[2]),
        utils.format_informer(utils.INFORMER, FEED_IDS[0]),
    ]
    assert payload['informers'] == expected_payload[:max_informers]
    assert payload['stories'] == []


@pytest.mark.parametrize(
    [
        'brand_id',
        'place_id',
        'location',
        'retail_orders_count',
        'brand_orders_count',
    ],
    [(None, None, None, 4, 1), (BRAND_ID, PLACE_ID, [2.0, 1.0], 5, 2)],
)
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
@experiments.informers(EXP_NAME)
async def test_screen_communications_informers_kwargs(
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
    Проверяет кварги иноформеров в ручке
    /internal/v1/screen/communications
    """
    recorder = experiments3.record_match_tries(EXP_NAME)

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
        'consumer': 'eats-communications/informers',
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
    if place_id is not None:
        expected_kwargs['place_id'] = place_id
    if brand_id and brand_orders_count_enabled:
        expected_kwargs['brand_orders_count'] = brand_orders_count
    if brand_orders_count_enabled:
        expected_kwargs['retail_orders_count'] = retail_orders_count
    assert match_tries[0].kwargs == expected_kwargs


@pytest.mark.parametrize(
    ['eater_id', 'has_retail_orders'],
    [(EATER_ID, False), (EATER_ID, True), (None, False)],
)
@communications_config(brand_orders_count_request_enabled=True)
@experiments.informers(EXP_NAME)
async def test_screen_communications_informers_kwargs_no_orders(
        taxi_eats_communications,
        mockserver,
        experiments3,
        eater_id,
        has_retail_orders,
):
    """
    Проверяет получение количество заказов пользователя в ручке
    /internal/v1/screen/communications
    Если пользователь неавторизован(запроса статистики не будет) или не имеет
    заказов в ритейле, то оба параметра будут равны 0
    """
    recorder = experiments3.record_match_tries(EXP_NAME)
    retail_orders_count = 5

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        return utils.make_feeds()

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        return utils.make_eats_orders_stats_response(
            request,
            eater_id,
            'unknown_brand',
            retail_orders_count,
            1,
            has_retail_orders,
        )

    request_body = {
        'types': [TYPE, 'stories'],
        'screen': SCREEN,
        'brand_id': BRAND_ID,
    }
    headers = {'X-Eats-User': f'user_id={eater_id}'} if eater_id else {}
    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers=headers,
        json=request_body,
    )

    assert response.status_code == 200
    assert feeds.times_called == 1
    assert order_stats.times_called == (1 if eater_id else 0)

    match_tries = await recorder.get_match_tries(ensure_ntries=1)
    kwargs = match_tries[0].kwargs
    assert kwargs['brand_orders_count'] == 0
    assert kwargs['retail_orders_count'] == (
        retail_orders_count if has_retail_orders and eater_id else 0
    )


@experiments.informers(EXP_NAME)
@experiments.screen_stories('stories_exp')
@communications_config(brand_orders_count_request_enabled=True)
async def test_screen_communications_informers_and_stories(
        taxi_eats_communications, mockserver,
):
    """
    Проверяет логику работы ручки /internal/v1/screen/communications
    при запросе и сториз и информеров одновременно
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        if request.json['service'] == 'eats-promotions-informer':
            return utils.make_fetch_informers_response(
                [{'id': FEED_IDS[0], 'priority': 1}],
            )
        return utils.make_fetch_stories_response(
            [{'id': FEED_IDS[1], 'priority': 1}],
        )

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        return utils.make_eats_orders_stats_response(
            request, EATER_ID, BRAND_ID, 3, 1,
        )

    request_body = {
        'types': [TYPE, 'stories'],
        'screen': SCREEN,
        'brand_id': BRAND_ID,
    }

    response = await taxi_eats_communications.post(
        '/internal/v1/screen/communications',
        headers={
            'X-Eats-User': f'user_id={EATER_ID}',
            'X-App-Version': '5.27.1',
        },
        json=request_body,
    )

    assert feeds.times_called == 2
    assert order_stats.times_called == 1
    assert response.status_code == 200
    payload = response.json()['payload']

    assert payload['informers'] == [
        utils.format_informer(utils.INFORMER, FEED_IDS[0]),
    ]
    stories = payload['stories']
    assert len(stories) == 1
    assert stories[0]['offer']['shortcut_id'] == FEED_IDS[1]


@experiments.informers(EXP_NAME)
@pytest.mark.parametrize('status', [404, 429, 500, 'timeout'])
async def test_screen_communications_informers_bad_feeds_response(
        taxi_eats_communications, mockserver, status,
):
    """
    Проверяет, что плохие ответы feeds в ручке
    /internal/v1/screen/communications не приводят к 500
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        if status == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=status)

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

    assert feeds.has_calls
    assert response.status_code == 200
    payload = response.json()['payload']
    assert payload['stories'] == []
    assert payload['informers'] == []


@experiments.informers(EXP_NAME)
@pytest.mark.parametrize('status', [400, 429, 500, 'timeout'])
@communications_config(brand_orders_count_request_enabled=True)
async def test_screen_communications_informers_bad_stats_response(
        taxi_eats_communications, mockserver, experiments3, status,
):
    """
    Проверяет, что плохие ответы eats-orders-stats в ручке
    /internal/v1/screen/communications не приводят к 500,
    а поля retail_orders_count и brand_orders_count не прокидываются в экспы
    """
    recorder = experiments3.record_match_tries(EXP_NAME)

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        return utils.make_feeds()

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        if status == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=status)

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


@experiments.informers(EXP_NAME)
async def test_screen_communications_informers_filter(
        taxi_eats_communications, mockserver,
):
    """
    Проверяет логику фильтрации просмотренных информеров
    в ручке /internal/v1/screen/communications
    1) Если статус viewed и стратегия показа once, то информер не вернется
    2) Если статус viewed и стратегия показа low_priority, то информер
    вернется, но у него будет нулевой приоритет
    2) В остальных статусах и стратегиях или при их отсутствии информер
    вернется
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        return utils.make_fetch_informers_response(
            [
                # once и просмотрен -> не вернется в ответе
                {
                    'id': FEED_IDS[0],
                    'priority': 1,
                    'status': 'viewed',
                    'show_strategy': 'once',
                },
                # low_priority и просмотрен -> вернется в ответе последним
                {
                    'id': FEED_IDS[1],
                    'priority': 3,
                    'status': 'viewed',
                    'show_strategy': 'low_priority',
                },
                # вернутся в ответе
                {
                    'id': FEED_IDS[2],
                    'priority': 2,
                    'show_strategy': 'once',
                    'status': 'published',
                },
                {'id': FEED_IDS[3], 'priority': 5, 'status': 'viewed'},
                {'id': FEED_IDS[4], 'priority': 1, 'show_strategy': 'once'},
            ],
        )

    request_body = {'types': [TYPE], 'screen': SCREEN}

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

    assert [informer['id'] for informer in payload['informers']] == [
        FEED_IDS[3],
        FEED_IDS[2],
        FEED_IDS[4],
        FEED_IDS[1],
    ]
    assert payload['stories'] == []
