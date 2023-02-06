from datetime import datetime, timedelta, date, time

import pytest
import pytz

from sandbox.projects.yabs.qa.utils.datetime_interval import DatetimeInterval, split_datetime_interval, round_ab_time_interval


def test_datetime_interval_repr():
    start = datetime(year=2019, month=4, day=20, hour=23, minute=59, second=59, tzinfo=pytz.utc)
    end = datetime(year=2019, month=4, day=21, hour=17, minute=39, second=9, tzinfo=pytz.utc)
    datetime_interval = DatetimeInterval(start, end)
    assert str(datetime_interval) == '2019-04-20T23:59:59+00:00 / 2019-04-21T17:39:09+00:00'


day_start = time(hour=4, tzinfo=pytz.utc)
day_end = time(hour=18, tzinfo=pytz.utc)
today_start = datetime.combine(date(2019, 4, 20), day_start)
today_end = datetime.combine(date(2019, 4, 20), day_end)
one_minute = timedelta(minutes=1)


@pytest.mark.parametrize(['start_dt', 'duration', 'expected_intervals'], [
    (
        today_start - timedelta(hours=2),
        timedelta(hours=6),
        [DatetimeInterval(start=today_start, end=today_start + timedelta(hours=6))]
    ),
    (
        today_start - timedelta(hours=6),
        timedelta(hours=5),
        [DatetimeInterval(start=today_start, end=today_start + timedelta(hours=5))]
    ),
    (
        today_start,
        timedelta(hours=2),
        [DatetimeInterval(start=today_start, end=today_start + timedelta(hours=2))]
    ),
    (
        today_start,
        today_end - today_start,
        [DatetimeInterval(start=today_start, end=today_end)]
    ),
    (
        today_end - timedelta(hours=3),
        timedelta(hours=6),
        [
            DatetimeInterval(start=today_end - timedelta(hours=3), end=today_end),
            DatetimeInterval(start=today_start + timedelta(days=1), end=today_start + timedelta(days=1, hours=3)),
        ]
    ),
    (
        today_end - timedelta(hours=3),
        timedelta(hours=3, minutes=10),
        [DatetimeInterval(start=today_end - timedelta(hours=3), end=today_end + timedelta(minutes=10))]
    ),
    (
        today_start - timedelta(hours=1),
        datetime.combine(date.today(), day_end) - datetime.combine(date.today(), day_start) + timedelta(hours=2),
        [
            DatetimeInterval(start=today_start, end=today_end),
            DatetimeInterval(start=today_start + timedelta(days=1), end=today_start + timedelta(days=1, hours=2))
        ]
    ),
    (
        today_end - timedelta(hours=4),
        timedelta(hours=30),
        [
            DatetimeInterval(start=today_end - timedelta(hours=4), end=today_end),
            DatetimeInterval(start=today_start + timedelta(days=1), end=today_end + timedelta(days=1)),
            DatetimeInterval(start=today_start + timedelta(days=2), end=today_start + timedelta(days=2, hours=12)),
        ]
    ),
    (
        today_start,
        timedelta(),
        [DatetimeInterval(start=today_start, end=today_start)],
    ),
])
def test_split_datetime_interval(start_dt, duration, expected_intervals):
    assert split_datetime_interval(start_dt, duration, day_start, day_end) == expected_intervals


@pytest.mark.parametrize(['start_dt', 'duration', 'day_start', 'day_end'], [
    (today_start.replace(tzinfo=pytz.timezone('Europe/Moscow')), one_minute, day_start, day_end),
    (today_start, one_minute, day_start.replace(tzinfo=pytz.timezone('Europe/Moscow')), day_end),
    (today_start, one_minute, day_start, day_end.replace(tzinfo=pytz.timezone('Europe/Moscow'))),
])
def test_split_datetime_interval_different_timezone(start_dt, duration, day_start, day_end):
    with pytest.raises(ValueError):
        split_datetime_interval(start_dt, duration, day_start, day_end)


@pytest.mark.parametrize(['start_dt', 'duration', 'day_start', 'day_end'], [
    (today_start.replace(tzinfo=None), one_minute, day_start, day_end),
    (today_start, one_minute, day_start.replace(tzinfo=None), day_end),
    (today_start, one_minute, day_start, day_end.replace(tzinfo=None)),
])
def test_split_datetime_interval_naive_datetime(start_dt, duration, day_start, day_end):
    with pytest.raises(ValueError):
        split_datetime_interval(start_dt, duration, day_start, day_end)


def test_split_datetime_interval_zero_duration():
    with pytest.raises(ValueError):
        split_datetime_interval(today_start, one_minute, day_start, day_start)


def test_split_datetime_interval_day_start_more_than_day_end():
    with pytest.raises(ValueError):
        split_datetime_interval(today_start, one_minute, day_end, day_start)


def test_split_datetime_interval_negative_duration():
    with pytest.raises(ValueError):
        split_datetime_interval(today_start, timedelta(minutes=-1), day_start, day_end)


@pytest.mark.parametrize(['start_dt', 'duration', 'expected_intervals'], [
    (
        today_start,
        timedelta(hours=4, minutes=15),
        DatetimeInterval(start=today_start, end=today_start + timedelta(hours=4))
    ),
    (
        today_start,
        timedelta(hours=4),
        DatetimeInterval(start=today_start, end=today_start + timedelta(hours=4))
    ),
    (
        today_start,
        timedelta(hours=4, minutes=30),
        DatetimeInterval(start=today_start, end=today_start + timedelta(hours=4, minutes=30))
    ),
    (
        today_start + timedelta(seconds=30),
        timedelta(hours=4, minutes=15),
        DatetimeInterval(start=today_start, end=today_start + timedelta(hours=4))
    ),
    (
        today_start + timedelta(seconds=30),
        timedelta(hours=4, minutes=29, seconds=30),
        DatetimeInterval(start=today_start, end=today_start + timedelta(hours=4, minutes=30))
    ),
])
def test_round_ab_time_interval(start_dt, duration, expected_intervals):
    time_interval = split_datetime_interval(start_dt, duration, day_start, day_end)
    assert round_ab_time_interval(time_interval[0]) == expected_intervals
