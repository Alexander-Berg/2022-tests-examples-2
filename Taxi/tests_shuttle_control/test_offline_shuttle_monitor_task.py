# pylint: disable=import-only-modules
import datetime

import pytest

from tests_shuttle_control.utils import select_named

MOCK_NOW_DT = datetime.datetime(2020, 5, 28, 11, 40, 55)


@pytest.mark.now('2020-05-28T11:40:55+0000')
@pytest.mark.config(SHUTTLE_CONTROL_OFFLINE_SHUTTLE_TIME_THRESHOLD=20)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_remove_bookings(taxi_shuttle_control, pgsql):
    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': 'offline-shuttle-monitor'},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT shuttle_id, status FROM state.passengers '
        'ORDER BY booking_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {'shuttle_id': 1, 'status': 'driving'},
        {'shuttle_id': 2, 'status': 'cancelled'},
        {'shuttle_id': 2, 'status': 'cancelled'},
        {'shuttle_id': 3, 'status': 'driving'},
    ]

    rows = select_named(
        'SELECT shuttle_id, ended_at FROM state.shuttles '
        'ORDER BY shuttle_id',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {'shuttle_id': 1, 'ended_at': None},
        {'shuttle_id': 2, 'ended_at': MOCK_NOW_DT},
        {'shuttle_id': 3, 'ended_at': None},
        {'shuttle_id': 4, 'ended_at': MOCK_NOW_DT},
        {'shuttle_id': 5, 'ended_at': None},
    ]
