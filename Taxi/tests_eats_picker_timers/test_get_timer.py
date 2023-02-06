import datetime

import dateutil.parser
import pytest


async def test_get_timer_200(taxi_eats_picker_timers, create_timer):
    eats_id = 'eats_id'
    timer_type = 'timer_type'
    create_timer(eats_id, timer_type=timer_type)

    response = await taxi_eats_picker_timers.get(
        f'/api/v1/timer?eats_id={eats_id}&timer_type={timer_type}',
    )
    assert response.status == 200

    timer = response.json()
    assert timer['eats_id'] == eats_id
    assert timer['timer_type'] == timer_type


@pytest.mark.parametrize(
    'eats_id, timer_type',
    [
        ('eats_id_0', 'timer_type_0'),
        ('eats_id_0', 'timer_type_1'),
        ('eats_id_1', 'timer_type_0'),
    ],
)
async def test_get_timer_multiple_200(
        taxi_eats_picker_timers, now_utc, create_timer, eats_id, timer_type,
):
    for eats_id_new, timer_type_new, started_at_new in [
            ('eats_id_0', 'timer_type_0', now_utc),
            (
                'eats_id_0',
                'timer_type_1',
                now_utc - datetime.timedelta(hours=2),
            ),
            (
                'eats_id_0',
                'timer_type_1',
                now_utc - datetime.timedelta(hours=1),
            ),
            ('eats_id_0', 'timer_type_1', now_utc),
            ('eats_id_1', 'timer_type_0', now_utc),
            (
                'eats_id_1',
                'timer_type_0',
                now_utc - datetime.timedelta(hours=1),
            ),
            (
                'eats_id_1',
                'timer_type_0',
                now_utc - datetime.timedelta(hours=2),
            ),
    ]:
        create_timer(
            eats_id_new, timer_type=timer_type_new, started_at=started_at_new,
        )

    response = await taxi_eats_picker_timers.get(
        f'/api/v1/timer?eats_id={eats_id}&timer_type={timer_type}',
    )
    assert response.status == 200

    timer = response.json()
    assert timer['eats_id'] == eats_id
    assert timer['timer_type'] == timer_type
    assert dateutil.parser.isoparse(timer['started_at']) == now_utc


async def test_get_timer_404(taxi_eats_picker_timers, create_timer):
    response = await taxi_eats_picker_timers.get(
        f'/api/v1/timer?eats_id=eats_id&timer_type=timer_type',
    )
    assert response.status == 404
    assert response.json()['code'] == 'TIMER_NOT_FOUND'
