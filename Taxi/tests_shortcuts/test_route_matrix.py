# pylint: disable=import-error
import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary

URL = 'v1/route-matrix'
USE_TOLL_ROADS_EXPERIMENT = 'use_toll_roads'
ROUTE_MATRIX_CONSUMER = 'shortcuts/route_matrix'


def get_headers(locale='ru', app_name=None):
    if app_name is None:
        app_name = 'android'
    return {
        'X-Yandex-Uid': '4003514353',
        'X-Remote-IP': '127.0.0.1',
        'X-Request-Language': locale,
        'X-Request-Application': f'app_name={app_name}',
    }


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


@pytest.mark.config(SHORTCUTS_SUBTITLE_ETA_FORMAT='like-routestats')
@pytest.mark.translations(
    client_messages={
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.tens_minutes': {
            'ru': '%(value).0f мин',
            'en': '%(value).0f min',
        },
    },
)
@pytest.mark.parametrize(
    'input_routes,locale,expected_response_body',
    [
        (
            [
                {
                    'id': 'alpha',
                    'route': [[37.0, 55.0], [37.01, 55.01]],
                    'type': 'auto',
                },
                {
                    'id': 'beta',
                    'route': [[37.0, 55.0], [38.02, 55.02]],
                    'type': 'auto',
                },
            ],
            'ru',
            {
                'routes': [
                    {
                        'eta': {
                            'display': '4 мин',
                            'distance': 1281,
                            'time': 184,
                        },
                        'id': 'alpha',
                    },
                    {
                        'eta': {
                            'display': '2 ч 40 мин',
                            'distance': 65075,
                            'time': 9370,
                        },
                        'id': 'beta',
                    },
                ],
            },
        ),
        (
            [
                {
                    'id': 'alpha',
                    'route': [[37.0, 55.0], [37.01, 55.01]],
                    'type': 'auto',
                },
            ],
            'en',
            {
                'routes': [
                    {
                        'eta': {
                            'display': '4 min',
                            'distance': 1281,
                            'time': 184,
                        },
                        'id': 'alpha',
                    },
                ],
            },
        ),
        ([], 'ru', {'routes': []}),
    ],
)
async def test_routestats_formatting(
        taxi_shortcuts, input_routes, locale, expected_response_body,
):
    payload = {'user_context': 'shortcuts', 'routes': input_routes}
    response = await taxi_shortcuts.post(
        URL, payload, headers=get_headers(locale),
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_response_body


@pytest.mark.config(SHORTCUTS_ROUTE_MATRIX_LIMIT=0)
async def test_config_limit(taxi_shortcuts):
    payload = {
        'user_context': 'shortcuts',
        'routes': [
            {'id': 'alpha', 'route': [[0, 0], [0, 0]], 'type': 'auto'},
            {'id': 'beta', 'route': [[1, 1], [1, 1]], 'type': 'auto'},
        ],
    }
    response = await taxi_shortcuts.post(URL, payload, headers=get_headers())
    assert response.status_code == 200
    data = response.json()
    assert data == {'routes': []}


@pytest.mark.config(
    SHORTCUTS_SUBTITLE_ETA_FORMAT='minutes',
    APPLICATION_MAP_TRANSLATIONS={
        'yango_android': {
            'client_messages': 'client_messages_yango',
            'notify': 'notify_yango',
            'tariff': 'tariff_yango',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s минуточек',
            'en': '%(delivery_time)s minnies',
        },
    },
    client_messages_yango={
        'shortcuts_eats_delivery_time_template': {
            # no override for "ru", should use client_messages
            'en': '%(delivery_time)s yango_minutes',
        },
    },
)
@pytest.mark.parametrize(
    'locale,app_name,expected_display',
    [
        ('en', 'android', '27 minnies'),
        ('ru', 'android', '27 минуточек'),
        ('en', 'yango_android', '27 yango_minutes'),
        ('ru', 'yango_android', '27 минуточек'),
    ],
)
async def test_minutes_formatting(
        taxi_shortcuts, locale, app_name, expected_display,
):
    payload = {
        'user_context': 'shortcuts',
        'routes': [
            {'id': 'alpha', 'route': [[0, 0], [0.1, 0]], 'type': 'auto'},
        ],
    }
    response = await taxi_shortcuts.post(
        URL, payload, headers=get_headers(locale, app_name),
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'routes': [
            {
                'eta': {
                    'display': expected_display,
                    'distance': 11119,
                    'time': 1601,
                },
                'id': 'alpha',
            },
        ],
    }


@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s мин',
        },
    },
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': []}, {'ids': ['spb'], 'routers': ['yamaps']}],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_zone_name(taxi_shortcuts, mockserver):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(time=100, distance=200),
            status=200,
            content_type='application/x-protobuf',
        )

    payload = {
        'user_context': 'shortcuts',
        'routes': [
            {
                'id': 'alpha',
                'route': [[37.1, 55.4], [37.2, 55.5]],
                'type': 'auto',
            },
        ],
    }

    response = await taxi_shortcuts.post(URL, payload, headers=get_headers())
    assert response.status_code == 200
    assert response.json() == {
        'routes': [
            {
                'eta': {'display': '2 мин', 'distance': 200, 'time': 100},
                'id': 'alpha',
            },
        ],
    }


@pytest.mark.translations(
    client_messages={
        'shortcuts_eats_delivery_time_template': {
            'ru': '%(delivery_time)s мин',
        },
    },
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': []}, {'ids': ['spb'], 'routers': ['yamaps']}],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize('use_toll_roads', [True, False])
async def test_yamaps_toll_roads(
        taxi_shortcuts, mockserver, use_toll_roads, add_experiment,
):
    add_experiment(
        USE_TOLL_ROADS_EXPERIMENT,
        {'enabled': use_toll_roads},
        consumers=[ROUTE_MATRIX_CONSUMER],
    )
    router_called = False

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        nonlocal router_called
        router_called = True
        assert (request.args.get('avoid') == 'tolls') != use_toll_roads
        return mockserver.make_response(
            response=_proto_driving_summary(time=100, distance=200),
            status=200,
            content_type='application/x-protobuf',
        )

    payload = {
        'user_context': 'shortcuts',
        'routes': [
            {
                'id': 'alpha',
                'route': [[37.1, 55.4], [37.2, 55.5]],
                'type': 'auto',
            },
        ],
    }

    response = await taxi_shortcuts.post(URL, payload, headers=get_headers())
    assert response.status_code == 200
    assert router_called
