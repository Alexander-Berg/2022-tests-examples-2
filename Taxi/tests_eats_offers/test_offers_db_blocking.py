import asyncio

import pytest

import tests_eats_offers.utils as utils

TIME_DELTA = 150


@pytest.mark.parametrize(
    'users, sessions, expect_time_ranges',
    [
        pytest.param(
            ['user-id-1', 'user-id-1'],
            ['session-id-1', 'session-id-2'],
            [(0, TIME_DELTA), (1000 - TIME_DELTA, 1000 + TIME_DELTA)],
            id='same users -> wait',
        ),
        pytest.param(
            ['user-id-1', 'user-id-2'],
            ['session-id-1', 'session-id-2'],
            [(0, TIME_DELTA), (0, TIME_DELTA)],
            id='different users -> don\'t wait',
        ),
        pytest.param(
            [None, None],
            ['session-id-1', 'session-id-2'],
            [(0, TIME_DELTA), (0, TIME_DELTA)],
            id='no users (only session) -> don\'t wait',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.skip(reason='not stable - for local usage')
async def test_loginned_offer_set(
        taxi_eats_offers,
        testpoint,
        users,
        sessions,
        expect_time_ranges,
        taxi_config,
):
    times = []

    @testpoint('testpoint_execution_time')
    def testpoint_execution_time(data):
        times.append(data['time'])

    @testpoint('testpoint_sleep_for')
    def testpoint_sleep_for(data):
        return {'sleep_for': 1000}

    taxi_config.set_values(
        {'EATS_OFFERS_FEATURE_FLAGS': {'use_auth_in_search': True}},
    )
    await taxi_eats_offers.invalidate_caches()

    task1 = asyncio.create_task(
        test_task(taxi_eats_offers, sessions[0], users[0]),
    )
    task2 = asyncio.create_task(
        test_task(taxi_eats_offers, sessions[1], users[1]),
    )
    await task1
    await task2

    assert len(times) == 2
    assert times[0] > expect_time_ranges[0][0]
    assert times[0] < expect_time_ranges[0][1]
    assert times[1] > expect_time_ranges[1][0]
    assert times[1] < expect_time_ranges[1][1]

    assert testpoint_sleep_for.times_called == 2
    assert testpoint_execution_time.times_called == 2


@pytest.mark.skip(reason='just helper func - not a test')
async def test_task(taxi_eats_offers, session_id, user_id):
    request_json = {
        'session_id': session_id,
        'parameters': {
            'location': [2, 2],
            'delivery_time': '2019-10-31T12:00:00+00:00',
        },
        'payload': {'extra-data': 'value'},
    }
    if user_id is None:
        response = await taxi_eats_offers.post(
            '/v1/offer/set', json=request_json,
        )
    else:
        response = await taxi_eats_offers.post(
            '/v1/offer/set',
            json=request_json,
            headers=utils.get_headers_with_user_id(user_id),
        )
    assert response.status_code == 200
