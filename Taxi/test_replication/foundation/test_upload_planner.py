# pylint: disable=protected-access
import datetime

import pytest
import pytz

from replication.foundation import upload_planner


TZ_MSK = pytz.timezone('Europe/Moscow')
NOW = TZ_MSK.localize(datetime.datetime(2020, 4, 30, 12, 2, 10))
ROUNDED_NOW = NOW.replace(second=0)


@pytest.mark.nofilldb
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'input_data, expected_object, expected_error, expected_next_run',
    [
        (None, upload_planner.AlwaysSchedule(60), None, ROUNDED_NOW),
        (
            {'cron': '*/2 * * * *'},
            upload_planner.CronSchedule(cron='*/2 * * * *'),
            None,
            ROUNDED_NOW,
        ),
        (
            {'cron': '0 */4 * * *'},
            upload_planner.CronSchedule(cron='0 */4 * * *'),
            None,
            ROUNDED_NOW + datetime.timedelta(hours=3, minutes=58),
        ),
        (
            {'cron': '0 0 * * *'},
            upload_planner.CronSchedule(cron='0 0 * * *'),
            None,
            TZ_MSK.localize(datetime.datetime(2020, 5, 1, 0)),
        ),
        (
            {'period': 60},
            upload_planner.PeriodSchedule(period=60),
            None,
            ROUNDED_NOW,
        ),
        (
            {'period': 600},
            upload_planner.PeriodSchedule(period=600),
            None,
            ROUNDED_NOW + datetime.timedelta(minutes=8),
        ),
        (
            {'period': 86400},
            upload_planner.PeriodSchedule(period=86400),
            None,
            TZ_MSK.localize(datetime.datetime(2020, 5, 1, 0)),
        ),
        ({'period': 65}, None, TypeError, None),
        ({'cron': '*/2 * * * 3000'}, None, TypeError, None),
        ({'cron': '* * * * *', 'period': 600}, None, TypeError, None),
        (
            {'period': {'unittests': 600, 'production': 1200}},
            upload_planner.PeriodSchedule(period=600),
            None,
            ROUNDED_NOW + datetime.timedelta(minutes=8),
        ),
        (
            {'period': {'production': 900, 'testing': 600}},
            upload_planner.PeriodSchedule(period=600),
            None,
            ROUNDED_NOW + datetime.timedelta(minutes=8),
        ),
        ({'cron': {'unittests': 600}}, None, TypeError, None),
    ],
)
def test_schedule(
        input_data, expected_object, expected_error, expected_next_run,
):
    if expected_error is not None:
        with pytest.raises(expected_error):
            upload_planner._convert_schedule(input_data)
    else:
        schedule = upload_planner._convert_schedule(input_data)
        assert schedule == expected_object
        assert schedule.get_next_run() == expected_next_run


NOW_MIDNIGHT = TZ_MSK.localize(datetime.datetime(2020, 4, 30, 0, 0, 0))


@pytest.mark.nofilldb
@pytest.mark.now(NOW_MIDNIGHT.isoformat())
@pytest.mark.parametrize(
    'input_data, previous_run, expected_next_run',
    [
        ({'period': 600}, None, NOW_MIDNIGHT),
        ({'period': 86400}, None, NOW_MIDNIGHT),
        (
            {'period': 600},
            NOW_MIDNIGHT - datetime.timedelta(seconds=3),
            NOW_MIDNIGHT,
        ),
        (
            {'period': 86400},
            NOW_MIDNIGHT - datetime.timedelta(seconds=3),
            NOW_MIDNIGHT,
        ),
        # current behavior: ignore previous_run if previous_run >= now
        ({'period': 600}, NOW_MIDNIGHT, NOW_MIDNIGHT),
        ({'period': 86400}, NOW_MIDNIGHT, NOW_MIDNIGHT),
    ],
)
def test_schedule_midnight(input_data, previous_run, expected_next_run):
    schedule = upload_planner._convert_schedule(input_data)
    assert (
        schedule.get_next_run(previous_run=previous_run) == expected_next_run
    )


@pytest.mark.nofilldb
@pytest.mark.now((NOW_MIDNIGHT + datetime.timedelta(minutes=2)).isoformat())
@pytest.mark.parametrize(
    'input_data, previous_run, expected_next_run',
    [
        (
            {'period': 600},
            None,
            NOW_MIDNIGHT + datetime.timedelta(seconds=600),
        ),
        (
            {'period': 86400},
            None,
            NOW_MIDNIGHT + datetime.timedelta(seconds=86400),
        ),
        (
            {'period': 600},
            NOW_MIDNIGHT,
            NOW_MIDNIGHT + datetime.timedelta(seconds=600),
        ),
        (
            {'period': 86400},
            NOW_MIDNIGHT,
            NOW_MIDNIGHT + datetime.timedelta(seconds=86400),
        ),
        # no successful launches found at last period time, so run now
        (
            {'period': 600},
            NOW_MIDNIGHT - datetime.timedelta(seconds=3),
            NOW_MIDNIGHT + datetime.timedelta(minutes=2),
        ),
        (
            {'period': 86400},
            NOW_MIDNIGHT - datetime.timedelta(seconds=3),
            NOW_MIDNIGHT + datetime.timedelta(minutes=2),
        ),
    ],
)
def test_schedule_midnight2(input_data, previous_run, expected_next_run):
    schedule = upload_planner._convert_schedule(input_data)
    assert (
        schedule.get_next_run(previous_run=previous_run) == expected_next_run
    )
