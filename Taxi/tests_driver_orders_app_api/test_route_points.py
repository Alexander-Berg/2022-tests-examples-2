import datetime
import json

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as redis
import tests_driver_orders_app_api.requestconfirm_helpers as rch

CONTENT_HEADER = {'Content-Type': 'application/json'}

DRIVER = 'driver_id_0'
WRONG_DRIVER = 'wrong_driver'
PARK = 'park_id_0'

YANDEX_PROVIDER = 2
SOME_PROVIDER = 1024

POINTS_DEFAULT = [{'order': 1, 'passed': True, 'type': 'manual'}]


def add_points_arrival_time(data):
    for point in data.get('points') or []:
        point['arrival_time'] = datetime.datetime.now(
            datetime.timezone.utc,
        ).isoformat()


async def make_route_points_request(
        taxi_driver_orders_app_api, user_agent, data, params, driver_id,
):
    add_points_arrival_time(data)
    return await taxi_driver_orders_app_api.put(
        'v1/route-points',
        headers={
            **CONTENT_HEADER,
            **rch.get_headers(user_agent, params['park_id'], driver_id),
        },
        data=json.dumps(data),
        params=params,
    )


@pytest.mark.parametrize(
    'user_agent', [auth.USER_AGENT_TAXIMETER, auth.USER_AGENT_UBER],
)
@pytest.mark.parametrize(
    'params,data,code',
    [
        (
            {'session': 'test_session', 'park_id': PARK},
            {'points': [{'order': 1, 'passed': False}]},
            400,
        ),
        (
            {'session': 'test_session', 'park_id': PARK},
            {'order_id': 'order_id_0'},
            400,
        ),
    ],
)
async def test_route_points_required_args(
        taxi_driver_orders_app_api, user_agent, params, data, code,
):
    response = await make_route_points_request(
        taxi_driver_orders_app_api, user_agent, data, params, '',
    )
    assert response.status_code == code


@pytest.mark.parametrize(
    'user_agent', [auth.USER_AGENT_TAXIMETER, auth.USER_AGENT_UBER],
)
@pytest.mark.parametrize(
    'driver_id,redis_driver,redis_provider,params,data,code',
    [
        (
            DRIVER,
            (PARK, 'order_id_0', DRIVER),
            (PARK, 'order_id_0', YANDEX_PROVIDER),
            {'session': 'test_session', 'park_id': PARK},
            {'order_id': 'order_id_0', 'points': POINTS_DEFAULT},
            200,
        ),
        (
            DRIVER,
            (),
            (PARK, 'order_id_0', YANDEX_PROVIDER),
            {'session': 'test_session', 'park_id': PARK},
            {'order_id': 'order_id_0', 'points': POINTS_DEFAULT},
            200,  # Missing driver is not an error in legacy /route_points
        ),
        (
            DRIVER,
            (PARK, 'order_id_0', DRIVER),
            (PARK, 'order_id_0', SOME_PROVIDER),
            {'session': 'test_session', 'park_id': PARK},
            {'order_id': 'order_id_0', 'points': POINTS_DEFAULT},
            200,  # Requests with non-Yandex provider are silently ignored
        ),
        (
            DRIVER,
            (PARK, 'order_id_0', DRIVER),
            (),
            {'session': 'test_session', 'park_id': PARK},
            {'order_id': 'order_id_0', 'points': POINTS_DEFAULT},
            200,  # Requests with missing provider are silently ignored
        ),
        (
            DRIVER,
            (PARK, 'order_id_0', WRONG_DRIVER),
            (PARK, 'order_id_0', YANDEX_PROVIDER),
            {'session': 'test_session', 'park_id': PARK},
            {'order_id': 'order_id_0', 'points': POINTS_DEFAULT},
            410,  # Driver mismatch
        ),
    ],
)
async def test_handle_route_points_responsive(
        taxi_driver_orders_app_api,
        redis_store,
        driver_authorizer,
        mock_fleet_parks_list,
        user_agent,
        driver_id,
        redis_driver,
        redis_provider,
        params,
        data,
        code,
):
    auth.create_session(
        driver_authorizer,
        user_agent,
        driver_id,
        params['park_id'],
        params['session'],
    )
    if redis_driver:
        redis.set_driver_for_order(redis_store, *redis_driver)
    if redis_provider:
        redis.set_provider_for_order(redis_store, *redis_provider)

    response = await make_route_points_request(
        taxi_driver_orders_app_api, user_agent, data, params, driver_id,
    )
    assert response.status_code == code
    assert not response.text


@pytest.mark.parametrize(
    'user_agent', [auth.USER_AGENT_TAXIMETER, auth.USER_AGENT_UBER],
)
@pytest.mark.parametrize(
    'order_id,park_id,code',
    [
        ('order_ok', PARK, 200),
        ('order_internal_not_found', PARK, 410),  # as in legacy C#
        ('order_internal_gone', PARK, 410),
        ('order_internal_error', PARK, 500),
        ('order_ok', 'park_id_wrong_apikey', 403),
        ('order_ok', 'park_id_no_apikey', 500),
        ('order_ok', 'park_id_no_clid', 500),
        ('order_ok', 'park_id_no_provider_config', 200),  # as in legacy C#
    ],
)
async def test_handle_route_points_internal(
        taxi_driver_orders_app_api,
        redis_store,
        driver_authorizer,
        mock_fleet_parks_list,
        user_agent,
        order_id,
        park_id,
        code,
):
    session = 'test_session'
    auth.create_session(
        driver_authorizer, user_agent, DRIVER, park_id, session,
    )
    redis.set_driver_for_order(redis_store, park_id, order_id, DRIVER)
    redis.set_provider_for_order(
        redis_store, park_id, order_id, YANDEX_PROVIDER,
    )
    data = {'order_id': order_id, 'points': POINTS_DEFAULT}
    params = {'park_id': park_id, 'session': session}

    response = await make_route_points_request(
        taxi_driver_orders_app_api, user_agent, data, params, DRIVER,
    )
    assert response.status_code == code
    assert not response.text
