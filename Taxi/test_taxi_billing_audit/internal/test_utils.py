import datetime

import pytest
import pytz

from taxi_billing_audit.internal import types
from taxi_billing_audit.internal import utils


MOSCOW_TZ = pytz.timezone('Europe/Moscow')


@pytest.mark.parametrize(
    'begin, end, expected_dates',
    [
        (
            {
                'day': 27,
                'month': 2,
                'year': 2019,
                'hour': 12,
                'minute': 14,
                'second': 0,
                'microsecond': 0,
            },
            {
                'day': 3,
                'month': 3,
                'year': 2019,
                'hour': 12,
                'minute': 55,
                'second': 0,
                'microsecond': 0,
            },
            [
                {
                    'day': 27,
                    'month': 2,
                    'year': 2019,
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                },
                {
                    'day': 28,
                    'month': 2,
                    'year': 2019,
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                },
                {
                    'day': 1,
                    'month': 3,
                    'year': 2019,
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                },
                {
                    'day': 2,
                    'month': 3,
                    'year': 2019,
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                },
                {
                    'day': 3,
                    'month': 3,
                    'year': 2019,
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                    'microsecond': 0,
                },
            ],
        ),
    ],
)
def test_iterage_over_intervals(begin, end, expected_dates):
    begin = datetime.datetime(**begin)
    end = datetime.datetime(**end)
    expected = []
    for interval_number in range(len(expected_dates) - 1):
        expected.append(
            types.IntervalDescription(
                begin=utils.to_msec(
                    datetime.datetime(**expected_dates[interval_number]),
                ),
                end=utils.to_msec(
                    datetime.datetime(**expected_dates[interval_number + 1]),
                ),
            ),
        )

    assert list(utils.get_intervals_from_range(begin, end)) == expected


@pytest.mark.parametrize(
    'time, expected_start',
    [
        (
            datetime.datetime(
                2020, 9, 15, 15, 13, 48, 479809, tzinfo=MOSCOW_TZ,
            ),
            datetime.datetime(2020, 9, 14, 0, 0, 0, 0, tzinfo=MOSCOW_TZ),
        ),
        (
            datetime.datetime(2020, 9, 14, 0, 0, 0, 0, tzinfo=MOSCOW_TZ),
            datetime.datetime(2020, 9, 14, 0, 0, 0, 0, tzinfo=MOSCOW_TZ),
        ),
        (
            datetime.datetime(
                2020, 9, 20, 23, 59, 59, 999999, tzinfo=MOSCOW_TZ,
            ),
            datetime.datetime(2020, 9, 14, 0, 0, 0, 0, tzinfo=MOSCOW_TZ),
        ),
    ],
)
def test_start_of_week(time, expected_start):
    assert utils.start_of_week(time) == expected_start


def test_start_of_week_requires_tz():
    with pytest.raises(AssertionError):
        utils.start_of_week(datetime.datetime.utcnow())
