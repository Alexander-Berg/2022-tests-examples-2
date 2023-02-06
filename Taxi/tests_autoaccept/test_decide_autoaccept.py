import copy

import pytest


BODY = {
    'user_uid': 'uid0',
    'user_agent': 'user_agent0',
    'user_phone_id': 'phone_id0',
    'driver_profile_id': 'uuid0',
    'park_id': 'park_id0',
    'unique_driver_id': 'udid0',
    'order_id': 'order_id0',
    'tariff_zone': 'moscow',
    'tariff_class': 'econom',
    'payment_tech_type': 'corp',
    'surge_price': 1.0,
    'distance_to_a': 100,
    'time_to_a': 100,
    'source_point': [37.63, 55.74],
    'check_in_candidate': True,
    'combo_active': True,
}

OK_RESPONSE = {'autoaccept': {'enabled': True}}


@pytest.mark.parametrize(
    'request_override, expected_response, fallbacks',
    [
        (
            {'has_chain_parent': True, 'driver_tags': ['driver_fix']},
            {'autoaccept': {'enabled': True}},
            [],
        ),
        (
            {'has_chain_parent': True, 'driver_tags': ['driver_fix']},
            {},
            ['autoaccept.moscow.too_many_auto_accepted_orders'],
        ),
        (
            {
                'has_chain_parent': True,
                'passenger_comment': '',
                'driver_tags': ['driver_fix'],
            },
            {'autoaccept': {'enabled': True}},
            [],
        ),
        (
            {
                'has_chain_parent': True,
                'driver_tags': ['driver_fix'],
                'source_point': [55.74, 37.63],
            },
            {},
            [],
        ),
        (
            {
                'has_chain_parent': True,
                'driver_tags': ['driver_fix'],
                'source_point': [55.74, 37.63],
            },
            {},
            ['autoaccept.moscow.too_many_auto_accepted_orders'],
        ),
        (
            {
                'passenger_comment': 'comment0',
                'has_chain_parent': True,
                'driver_tags': ['driver_fix'],
            },
            {},
            [],
        ),
        ({'driver_tags': ['driver_fix']}, {}, []),
        ({'has_chain_parent': True}, {}, []),
    ],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_decide_autoaccept(
        taxi_autoaccept,
        request_override,
        expected_response,
        fallbacks,
        statistics,
):
    statistics.fallbacks = fallbacks
    request_body = copy.deepcopy(BODY)
    request_body.update(request_override)

    async with statistics.capture(taxi_autoaccept) as capture:
        response = await taxi_autoaccept.post(
            '/v1/decide-autoaccept', json=request_body,
        )

    assert capture.statistics['autoaccept.moscow.orders_total'] == 1
    if (
            'autoaccept' in expected_response
            and 'enabled' in expected_response
            and expected_response['autoaccept']['enabled']
    ):
        assert (
            capture.statistics['autoaccept.moscow.auto_accepted_orders'] == 1
        )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'handle_path',
    [
        'driver-metrics/v1/order/match_properties',
        'passenger-profile/passenger-profile/v1/profile',
        'driver-ui-profile/v1/mode',
    ],
)
async def test_autoaccept_command_control(
        taxi_autoaccept, taxi_config, mockserver, handle_path,
):
    taxi_config.set(
        AUTOACCEPT_COMMAND_CONTROL={
            '__default__': {'attempts': 1, 'timeout-ms': 100},
            handle_path: {'attempts': 3, 'timeout-ms': 100},
        },
    )

    attempts = 0

    @mockserver.json_handler(f'/{handle_path}')
    def _handle(request):
        nonlocal attempts
        attempts += 1
        return mockserver.make_response(status=500)

    await taxi_autoaccept.post('/v1/decide-autoaccept', json=BODY)
    assert attempts == 3


@pytest.mark.parametrize(
    'taximeter_platform, expected_response',
    [('android', {'autoaccept': {'enabled': True}}), ('ios', {})],
)
@pytest.mark.experiments3(filename='driver_app_profile_exp3.json')
async def test_autoaccept_driver_app_profile(
        taxi_autoaccept,
        driver_app_profile,
        taximeter_platform,
        expected_response,
):
    driver_app_profile(taximeter_platform=taximeter_platform)
    response = await taxi_autoaccept.post('/v1/decide-autoaccept', json=BODY)
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'handle_path, expected_response',
    [
        ('unused-handle-path', OK_RESPONSE),
        ('driver-metrics/v1/order/match_properties', OK_RESPONSE),
        ('passenger-profile/passenger-profile/v1/profile', OK_RESPONSE),
        ('driver-profiles/v1/driver/app/profiles/retrieve', {}),
        ('driver-ui-profile/v1/mode', {}),
    ],
)
@pytest.mark.experiments3(filename='driver_app_profile_exp3.json')
async def test_autoaccept_exceptions_handling(
        taxi_autoaccept, mockserver, testpoint, handle_path, expected_response,
):
    @testpoint('filling_kwargs_finished')
    def filling_kwargs_finished(_):
        pass

    @mockserver.json_handler(f'/{handle_path}')
    def _handle(request):
        return mockserver.make_response(status=500)

    response = await taxi_autoaccept.post('/v1/decide-autoaccept', json=BODY)
    assert filling_kwargs_finished.times_called == 1
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'request_override, expected_response',
    [
        (
            {
                'distance_to_a': 43,
                'time_to_a': 43,
                'route_distance': 2000,
                'route_time': 600,
            },
            OK_RESPONSE,
        ),
        (
            {
                'distance_to_a': 1500,
                'time_to_a': 400,
                'route_distance': 2000,
                'route_time': 600,
            },
            {},
        ),
        (
            {
                'distance_to_a': 43,
                'time_to_a': 43,
                'route_distance': 500,
                'route_time': 150,
            },
            {},
        ),
    ],
)
@pytest.mark.config(
    LONG_TRIP_CRITERIA={
        '__default__': {
            'econom': {'apply': 'both', 'distance': 1000, 'duration': 300},
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_driver_metrics_fallback(
        taxi_autoaccept, mockserver, request_override, expected_response,
):
    @mockserver.json_handler('driver-metrics/v1/order/match_properties')
    def _handle(request):
        return mockserver.make_response(status=500)

    @mockserver.handler('/driver-metrics/v1/config/rule/values/')
    def _driver_metrics_mock(request):
        data = {
            'items': [
                {
                    'name': 'CommonDispatchRule',
                    'zone': '__default__',
                    'actions': [
                        {
                            'action': [
                                {
                                    'distance': [1000, 2000],
                                    'time': [300, 600],
                                    'type': 'dispatch_length_thresholds',
                                },
                            ],
                        },
                    ],
                },
            ],
        }
        return mockserver.make_response(json=data, status=200)

    request_body = copy.deepcopy(BODY)
    request_body.update(request_override)
    response = await taxi_autoaccept.post(
        '/v1/decide-autoaccept', json=request_body,
    )
    assert response.json() == expected_response
