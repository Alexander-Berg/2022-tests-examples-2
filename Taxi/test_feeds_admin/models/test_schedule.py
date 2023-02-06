# flake8: noqa: E501
import datetime

from feeds_admin import common
from feeds_admin import models

YEAR = datetime.timedelta(days=365)
DAY = datetime.timedelta(days=1)
HOUR = datetime.timedelta(hours=1)
MINUTE = datetime.timedelta(minutes=1)
START_AT = datetime.datetime(
    year=2020, month=2, day=24, hour=22, tzinfo=datetime.timezone.utc,
)  # last monday of month
NOW = datetime.datetime(
    year=2000, month=1, day=2, hour=4, minute=0, tzinfo=datetime.timezone.utc,
)
UTC = datetime.timezone.utc


def test_once():
    schedule = models.schedule.Once(
        start_at=START_AT, ttl=models.schedule.FixedTTL(DAY),
    )

    assert schedule.next_start_at(after=NOW) == START_AT
    assert schedule.next_start_at(after=START_AT + DAY) == START_AT + DAY


def test_interval_bad():
    try:
        schedule = models.schedule.Interval(
            start_at=START_AT, finish_at=START_AT - DAY,
        )

        assert False, f'Schedule creation must fail: {schedule}'
    except common.IncorrectSchedule:
        pass


def test_interval():
    schedule = models.schedule.Interval(
        start_at=START_AT, finish_at=START_AT + DAY,
    )

    assert schedule.next_start_at(after=NOW) == START_AT
    assert schedule.next_start_at(after=START_AT) == START_AT
    assert schedule.next_start_at(after=START_AT + DAY) is None


def test_periodic_bad():
    try:
        schedule = models.schedule.Periodic(
            start_at=START_AT,
            finish_at=START_AT - DAY,
            ttl=models.schedule.FixedTTL(DAY),
            repeat_period=datetime.timedelta(days=1),
        )

        assert False, f'Schedule creation must fail: {schedule}'
    except common.IncorrectSchedule:
        pass


def test_periodic_daily():
    schedule = models.schedule.Periodic(
        start_at=START_AT,
        finish_at=START_AT + 2 * DAY,
        ttl=models.schedule.FixedTTL(DAY),
        repeat_period=datetime.timedelta(days=1),
    )

    assert schedule.next_start_at(after=NOW) == START_AT
    assert schedule.next_start_at(after=START_AT) == START_AT + DAY
    assert schedule.next_start_at(after=START_AT + DAY) is None


def test_periodic_single_start():
    schedule = models.schedule.Periodic(
        start_at=START_AT,
        finish_at=START_AT,
        ttl=models.schedule.FixedTTL(DAY),
        repeat_period=datetime.timedelta(days=1),
    )

    assert schedule.next_start_at(after=NOW) == START_AT
    assert schedule.next_start_at(after=START_AT) is None


def test_weekly():
    schedule = models.schedule.Weekly(
        start_at=START_AT,
        finish_at=START_AT + 3 * DAY,
        ttl=models.schedule.FixedTTL(DAY),
        starts=[
            models.schedule.DayOfWeek(
                day=0, time=datetime.time(hour=22, minute=0, tzinfo=UTC),
            ),
            models.schedule.DayOfWeek(
                day=0, time=datetime.time(hour=23, minute=0, tzinfo=UTC),
            ),
            models.schedule.DayOfWeek(
                day=2, time=datetime.time(hour=23, minute=0, tzinfo=UTC),
            ),
        ],
    )

    assert schedule.next_start_at(after=NOW) == START_AT
    assert schedule.next_start_at(after=START_AT) == START_AT + HOUR
    assert schedule.next_start_at(after=START_AT + MINUTE) == START_AT + HOUR
    assert (
        schedule.next_start_at(after=START_AT + HOUR)
        == START_AT + 2 * DAY + HOUR
    )
    assert (
        schedule.next_start_at(after=START_AT + 2 * HOUR)
        == START_AT + 2 * DAY + HOUR
    )
    assert schedule.next_start_at(after=START_AT + 3 * DAY) is None


def test_weekly_nearest_start_on_next_week():
    schedule = models.schedule.Weekly(
        start_at=START_AT,
        finish_at=START_AT + 7 * DAY,
        ttl=models.schedule.FixedTTL(DAY),
        starts=[
            models.schedule.DayOfWeek(
                day=0, time=datetime.time(hour=21, minute=0, tzinfo=UTC),
            ),
        ],
    )

    assert schedule is not None
    assert schedule.next_start_at(after=START_AT) == START_AT + 7 * DAY - HOUR


def test_weekly_end_of_year():
    schedule = models.schedule.Weekly(
        start_at=START_AT,
        finish_at=START_AT + 2 * YEAR,
        ttl=models.schedule.FixedTTL(DAY),
        starts=[
            models.schedule.DayOfWeek(
                day=4, time=datetime.time(hour=12, minute=0, tzinfo=UTC),
            ),
        ],
    )

    end_of_year = START_AT.replace(month=12, day=31)
    expected = (end_of_year + DAY).replace(hour=12, minute=0)

    assert schedule.next_start_at(after=end_of_year) == expected


def test_monthly():
    schedule = models.schedule.Monthly(
        start_at=START_AT,
        finish_at=START_AT + 14 * DAY,
        ttl=models.schedule.FixedTTL(DAY),
        starts=[
            models.schedule.DayOfMonth(
                day=24, time=datetime.time(hour=22, minute=0, tzinfo=UTC),
            ),
            models.schedule.DayOfMonth(
                day=25, time=datetime.time(hour=23, minute=0, tzinfo=UTC),
            ),
            models.schedule.DayOfMonth(
                day=1, time=datetime.time(hour=12, minute=0, tzinfo=UTC),
            ),
            models.schedule.DayOfMonth(
                day=3, time=datetime.time(hour=10, minute=0, tzinfo=UTC),
            ),
        ],
    )

    assert schedule.next_start_at(after=NOW) == START_AT
    assert schedule.next_start_at(after=START_AT) == START_AT + DAY + HOUR
    assert (
        schedule.next_start_at(after=START_AT + HOUR) == START_AT + DAY + HOUR
    )
    assert (
        schedule.next_start_at(after=START_AT + 2 * DAY)
        == START_AT + 6 * DAY - 10 * HOUR
    )
    assert (
        schedule.next_start_at(after=START_AT + 7 * DAY)
        == START_AT + 8 * DAY - 12 * HOUR
    )
    assert schedule.next_start_at(after=START_AT + 8 * DAY) is None


def test_monthly_end_of_year():
    schedule = models.schedule.Monthly(
        start_at=START_AT,
        finish_at=START_AT + 2 * YEAR,
        ttl=models.schedule.FixedTTL(DAY),
        starts=[
            models.schedule.DayOfMonth(
                day=1, time=datetime.time(hour=12, minute=0, tzinfo=UTC),
            ),
        ],
    )

    end_of_year = START_AT.replace(month=12, day=31)
    expected = (end_of_year + DAY).replace(hour=12, minute=0)

    assert schedule.next_start_at(after=end_of_year) == expected
