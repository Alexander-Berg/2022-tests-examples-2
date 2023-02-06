import datetime as dt

import pytest

from replication_suite.casts import dates_casts


@pytest.mark.parametrize(
    'input_value, input_timezone, expected_value',
    (
        (dt.datetime(2020, 1, 1, 12, 0), 'UTC', '2020-01-01 12:00:00'),
        (
            dt.datetime(2020, 1, 1, 12, 0),
            'Europe/Moscow',
            '2020-01-01 09:00:00',
        ),
        (
            dt.datetime(2020, 1, 1, 0, 0),
            'Europe/Moscow',
            '2019-12-31 21:00:00',
        ),
        ('2020-02-03T04:05:06.000Z', 'UTC', '2020-02-03 04:05:06'),
        ('2020-02-03T04:05:06.000', 'UTC', '2020-02-03 04:05:06'),
        ('2020-02-03T04:05:06.000+0300', 'UTC', '2020-02-03 01:05:06'),
        ('2020-02-03T04:05:06.000Z', 'Europe/Moscow', '2020-02-03 04:05:06'),
        ('2020-02-03T04:05:06.000', 'Europe/Moscow', '2020-02-03 01:05:06'),
        (
            '2020-02-03T04:05:06.000+0300',
            'Europe/Moscow',
            '2020-02-03 01:05:06',
        ),
        (
            '2020-02-03T04:05:06.000+0200',
            'Europe/Moscow',
            '2020-02-03 02:05:06',
        ),
    ),
)
def test_naive_datetime_to_naive_utc_string(
        input_value, input_timezone, expected_value,
):
    assert (
        dates_casts.naive_datetime_to_naive_utc_string(
            input_value, input_timezone,
        )
        == expected_value
    )


@pytest.mark.parametrize(
    'input_value, expected_value',
    (
        ('2020-02-03T04:05:06.000Z', '2020-02-03 04:05:06'),
        ('2020-02-03T04:05:06.000000Z', '2020-02-03 04:05:06'),
    ),
)
def test_utc_isoformat_to_datetime_format(input_value, expected_value):
    assert (
        dates_casts.utc_isoformat_to_datetime_format(input_value)
        == expected_value
    )
