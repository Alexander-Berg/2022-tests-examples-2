import copy

import pytest

from . import utils


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/prepare', '/api/v1/timer/prepare'],
)
async def test_timer_order_not_found(
        taxi_eats_picker_timers, mockserver, handle,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _get_order(request):
        assert request.method == 'GET'
        assert request.query['eats_id'] == '123'
        return mockserver.make_response(
            status=404, json={'code': 'code', 'message': 'message'},
        )

    response = await taxi_eats_picker_timers.post(
        handle,
        json={'eats_id': '123', 'timer_type': 'test-timer'},
        headers=utils.da_headers(),
    )

    assert response.status == 404


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/prepare', '/api/v1/timer/prepare'],
)
async def test_timer_prepare(
        taxi_eats_picker_timers, order_get_json, mockserver, handle,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _get_order(request):
        assert request.method == 'GET'
        eats_id = request.query['eats_id']
        assert eats_id == '123'
        return mockserver.make_response(
            status=200, json=order_get_json(eats_id, 'picking', '1'),
        )

    @mockserver.json_handler(
        'eats-picking-time-estimator/api/v1/timer/calculate-duration',
    )
    def _calc_duration(request):
        assert request.json['timer_type'] == 'test-timer'
        order = request.json['order']
        assert len(order['items']) == 2
        assert order['picker_id'] == '1'
        return {'eta_seconds': 10}

    response = await taxi_eats_picker_timers.post(
        handle,
        json={'eats_id': '123', 'timer_type': 'test-timer'},
        headers=utils.da_headers(),
    )
    assert response.status == 200
    assert response.json()['eta_seconds'] == 10


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/prepare', '/api/v1/timer/prepare'],
)
async def test_timer_not_found(
        taxi_eats_picker_timers, order_get_json, mockserver, handle,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _get_order(request):
        assert request.method == 'GET'
        eats_id = request.query['eats_id']
        assert eats_id == '123'
        return mockserver.make_response(
            status=200, json=order_get_json(eats_id, 'picking', '1'),
        )

    @mockserver.json_handler(
        'eats-picking-time-estimator/api/v1/timer/calculate-duration',
    )
    def _calc_duration(request):
        return mockserver.make_response(
            status=404,
            json={
                'message': 'Timer type not found',
                'code': 'TIMER_TYPE_NOT_FOUND',
            },
        )

    response = await taxi_eats_picker_timers.post(
        handle,
        json={'eats_id': '123', 'timer_type': 'test-timer'},
        headers=utils.da_headers(),
    )
    assert response.status == 404
    assert response.json()['code'] == 'TIMER_TYPE_NOT_FOUND'


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/prepare', '/api/v1/timer/prepare'],
)
async def test_timer_order_get_fail(
        taxi_eats_picker_timers, mockserver, handle,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _get_order(request):
        return mockserver.make_response(
            status=500, json={'code': 'code', 'message': 'message'},
        )

    response = await taxi_eats_picker_timers.post(
        handle,
        json={'eats_id': '123', 'timer_type': 'test-timer'},
        headers=utils.da_headers(),
    )

    assert response.status == 500
    assert response.json()['code'] == 'ORDER_GET_FAIL'


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/prepare', '/api/v1/timer/prepare'],
)
async def test_timer_timer_calc_fail(
        taxi_eats_picker_timers, order_get_json, mockserver, handle,
):
    @mockserver.json_handler('/eats-picker-orders/api/v1/order')
    def _get_order(request):
        return mockserver.make_response(
            status=200, json=order_get_json('eats_id', 'picking', '1'),
        )

    @mockserver.json_handler(
        'eats-picking-time-estimator/api/v1/timer/calculate-duration',
    )
    def _calc_duration(request):
        return mockserver.make_response(
            status=500, json={'message': 'message', 'status': 'status'},
        )

    response = await taxi_eats_picker_timers.post(
        handle,
        json={'eats_id': '123', 'timer_type': 'test-timer'},
        headers=utils.da_headers(),
    )

    assert response.status == 500
    assert response.json()['code'] == 'TIMER_CALC_FAIL'


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/start', '/api/v1/timer/start'],
)
async def test_timers(taxi_eats_picker_timers, mocked_time, handle):
    eats_id = 'eats_id'
    picker_id = '1'

    # insert 2 timers
    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={'eats_id': eats_id, 'timer_type': 't1', 'duration': 10},
    )
    assert response.status == 200
    mocked_time.sleep(1)
    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={'eats_id': eats_id, 'timer_type': 't2', 'duration': 100},
    )
    assert response.status == 200

    # find timers
    response = await taxi_eats_picker_timers.get(
        f'/4.0/eats-picker-timers/api/v1/timers?eats_id={eats_id}',
        headers=utils.da_headers(),
    )
    assert response.status == 200
    timers = response.json()['timers']
    assert len(timers) == 2
    for timer in timers:
        assert timer['eats_id'] == eats_id
        assert timer['picker_id'] == picker_id
        assert 'finished_at' not in timer
    assert timers[0]['started_at'] > timers[1]['started_at']


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/start', '/api/v1/timer/start'],
)
@utils.timers_show_new_timers_config()
async def test_timers_autostart(taxi_eats_picker_timers, mocked_time, handle):
    eats_id = 'eats_id'

    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={
            'eats_id': eats_id,
            'timer_type': 'timer_order_autostart',
            'duration': 10,
        },
    )
    assert response.status == 200
    mocked_time.sleep(1)
    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={'eats_id': eats_id, 'timer_type': 'whatever', 'duration': 100},
    )
    assert response.status == 200

    response = await taxi_eats_picker_timers.get(
        f'/4.0/eats-picker-timers/api/v1/timers?eats_id={eats_id}',
        headers=utils.da_headers(),
    )
    assert response.status == 200

    timers = response.json()['timers']
    assert len(timers) == 1
    assert timers[0]['timer_type'] == 'whatever'

    headers = copy.deepcopy(utils.da_headers())
    headers['X-Request-Application'] = utils.AUTOSTART_APPLICATION
    headers['X-Request-Platform'] = utils.AUTOSTART_PLATFORM
    headers['X-Request-Application-Version'] = utils.AUTOSTART_VERSION
    response = await taxi_eats_picker_timers.get(
        f'/4.0/eats-picker-timers/api/v1/timers?eats_id={eats_id}',
        headers=headers,
    )
    assert response.status == 200

    timers = response.json()['timers']
    assert len(timers) == 2
    assert sorted([timer['timer_type'] for timer in timers]) == [
        'timer_order_autostart',
        'whatever',
    ]


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/start', '/api/v1/timer/start'],
)
async def test_timers_multiple_orders(taxi_eats_picker_timers, handle):
    eats_ids = ['order-1', 'order-2', 'order-3']
    for eats_id in eats_ids:
        response = await taxi_eats_picker_timers.post(
            handle,
            headers=utils.da_headers(),
            json={
                'eats_id': eats_id,
                'timer_type': 'some_timer_type',
                'duration': 10,
            },
        )

    response = await taxi_eats_picker_timers.get(
        f'/4.0/eats-picker-timers/api/v1/timers', headers=utils.da_headers(),
    )
    assert response.status == 200

    timers = response.json()['timers']
    assert len(timers) == 3
    assert set(timer['eats_id'] for timer in timers) == set(eats_ids)
