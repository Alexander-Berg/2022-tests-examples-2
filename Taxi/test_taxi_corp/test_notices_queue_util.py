# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi_corp.notifier import notices_queue_util


# friday
NOW = datetime.datetime(2019, 2, 1, 15, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['offset_params', 'expected_send_at'],
    [
        pytest.param(
            {'days_offset': 2, 'on_workday': False},
            datetime.datetime(2019, 2, 3, 7, 0, 0),
            id='same_sunday',
        ),
        pytest.param(
            {'days_offset': 2, 'on_workday': True},
            datetime.datetime(2019, 2, 4, 7, 0, 0),
            id='next_monday',
        ),
        pytest.param(
            {'days_offset': 5, 'on_workday': True},
            datetime.datetime(2019, 2, 6, 7, 0, 0),
            id='next_wednesday',
        ),
        pytest.param(
            {'days_offset': 5, 'on_workday': False},
            datetime.datetime(2019, 2, 6, 7, 0, 0),
            id='next_wednesday',
        ),
        pytest.param(
            {'days_offset': 8, 'on_workday': False},
            datetime.datetime(2019, 2, 9, 7, 0, 0),
            id='next_saturday',
        ),
        pytest.param(
            {'days_offset': 8, 'on_workday': True},
            datetime.datetime(2019, 2, 11, 7, 0, 0),
            id='monday_after_next',
        ),
        pytest.param(
            {
                'days_offset': 180,
                'on_workday': True,
                'send_hour': 8,
                'send_minute': 30,
            },
            datetime.datetime(2019, 7, 31, 8, 30, 0),
            id='time_in_params',
        ),
        pytest.param(
            {
                'days_offset': 0,
                'hours_offset': 0,
                'minutes_offset': 17,
                'on_workday': False,
            },
            datetime.datetime(2019, 2, 1, 15, 17, 0),
            id='17 minutes offset',
        ),
        pytest.param(
            {
                'days_offset': 0,
                'hours_offset': 1,
                'minutes_offset': 30,
                'on_workday': False,
            },
            datetime.datetime(2019, 2, 1, 16, 30, 0),
            id='1.5 hour offset',
        ),
    ],
)
def test_calc_notice_send_at(offset_params, expected_send_at):
    send_at = notices_queue_util.calc_notice_send_at(**offset_params)
    assert send_at == expected_send_at
