import pytest

from . import utils

TIMESTAMPTZ_NOW = '2021-01-19T15:00:27.010000+03:00'


@pytest.mark.now(TIMESTAMPTZ_NOW)
@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/finish', '/api/v1/timer/finish'],
)
async def test_timer_finish_200(
        taxi_eats_picker_timers, create_timer, get_timer, handle,
):
    eats_id = '123'
    picker_id = '1'
    timer_id = create_timer(
        eats_id=eats_id, picker_id=picker_id, finished_at=None,
    )

    spent_time = 10
    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={
            'eats_id': eats_id,
            'timer_id': timer_id,
            'spent_time': spent_time,
        },
    )

    assert response.status == 200
    timer = get_timer(timer_id)
    assert timer['finished_at'].isoformat() == TIMESTAMPTZ_NOW
    assert timer['spent_time'] == spent_time


@pytest.mark.now(TIMESTAMPTZ_NOW)
@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/finish', '/api/v1/timer/finish'],
)
async def test_timer_finish_empty_spent_time_200(
        taxi_eats_picker_timers, create_timer, get_timer, handle,
):
    eats_id = '123'
    picker_id = '1'
    timer_id = create_timer(
        eats_id=eats_id, picker_id=picker_id, finished_at=None,
    )

    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={'eats_id': eats_id, 'timer_id': timer_id},
    )

    assert response.status == 200
    timer = get_timer(timer_id)
    assert timer['finished_at'].isoformat() == TIMESTAMPTZ_NOW
    assert timer['spent_time'] is None


@pytest.mark.now(TIMESTAMPTZ_NOW)
@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/finish', '/api/v1/timer/finish'],
)
async def test_timer_finish_204(
        taxi_eats_picker_timers, create_timer, get_timer, handle,
):
    eats_id = '123'
    picker_id = '1'
    timer_finished_at = '2021-01-19T15:00:10.010000+03:00'
    initial_spent_time = 10
    timer_id = create_timer(
        eats_id=eats_id,
        picker_id=picker_id,
        finished_at=timer_finished_at,
        spent_time=initial_spent_time,
    )

    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={'eats_id': eats_id, 'timer_id': timer_id, 'spent_time': 20},
    )

    assert response.status == 204
    timer = get_timer(timer_id)
    assert timer['finished_at'].isoformat() == timer_finished_at
    assert timer['spent_time'] == initial_spent_time


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/finish', '/api/v1/timer/finish'],
)
async def test_timer_finish_no_timer_404(taxi_eats_picker_timers, handle):
    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(),
        json={'eats_id': '123', 'timer_id': 1, 'spent_time': 10},
    )

    assert response.status == 404
    assert response.json()['code'] == 'TIMER_NOT_FOUND'


@pytest.mark.parametrize(
    'request_eats_id, request_picker_id', [['123', '-'], ['-', '1122']],
)
@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/finish', '/api/v1/timer/finish'],
)
async def test_timer_finish_wrong_ids_404(
        taxi_eats_picker_timers,
        create_timer,
        get_timer,
        request_eats_id,
        request_picker_id,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    timer_id = create_timer(
        eats_id=eats_id, picker_id=picker_id, finished_at=None,
    )

    response = await taxi_eats_picker_timers.post(
        handle,
        headers=utils.da_headers(picker_id=request_picker_id),
        json={
            'eats_id': request_eats_id,
            'timer_id': timer_id,
            'spent_time': 10,
        },
    )

    assert response.status == 404
    assert response.json()['code'] == 'TIMER_NOT_FOUND'
    assert get_timer(timer_id)['finished_at'] is None
