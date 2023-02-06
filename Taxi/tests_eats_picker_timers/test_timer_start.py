import pytest

from . import utils

TIMESTAMPTZ_NOW = '2021-01-19T15:00:27.010000+03:00'


@pytest.mark.now(TIMESTAMPTZ_NOW)
@pytest.mark.parametrize('is_unreliable', [None, False, True])
@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker-timers/api/v1/timer/start', '/api/v1/timer/start'],
)
async def test_start_new_timer(
        taxi_eats_picker_timers, get_timer, is_unreliable, handle,
):
    body = {
        'eats_id': '123',
        'timer_type': 'type1',
        'duration': 100,
        'is_unreliable': is_unreliable,
    }
    picker_id = '1'

    response = await taxi_eats_picker_timers.post(
        handle, headers=utils.da_headers(), json=body,
    )
    assert response.status == 200

    new_timer_id = response.json()['timer_id']
    result = get_timer(new_timer_id)

    body.update(
        {
            'started_at': TIMESTAMPTZ_NOW,
            'picker_id': picker_id,
            'finished_at': None,
            'spent_time': None,
        },
    )
    utils.compare_db_with_expected_data(result, body)
