import datetime

from libstall.model import coerces
from libstall.util import week_range_by_datetime, day_range_by_datetime


async def test_week_range_by_datetime(tap):
    with tap.plan(3, 'неделя с указанием первого дня недели'):
        wednesday = coerces.date_time('2022-06-22T00:00:00+00:00')

        monday = coerces.date_time('2022-06-20T00:00:00+00:00')
        mon_week = (monday, monday + datetime.timedelta(weeks=1))
        tap.eq(week_range_by_datetime(wednesday),
               mon_week, 'correct mon_week check')

        sunday = coerces.date_time('2022-06-19T00:00:00+00:00')
        sun_week = (sunday, sunday + datetime.timedelta(weeks=1))
        tap.eq(week_range_by_datetime(wednesday, week_from_sunday=True),
               sun_week, 'correct sun_week check')

        next_wednesday = wednesday + datetime.timedelta(weeks=1)
        next_mon_week = (
            monday + datetime.timedelta(weeks=1),
            monday + datetime.timedelta(weeks=2),
        )
        tap.eq(week_range_by_datetime(next_wednesday),
               next_mon_week, 'correct next mon_week check')


async def test_day_range_by_datetime(tap):
    with tap.plan(2, 'день по указанному времени'):
        dt = coerces.date_time('2022-06-22T12:30:00+00:00')

        day_start = coerces.date_time('2022-06-22T00:00:00+00:00')
        day = (day_start, day_start + datetime.timedelta(days=1))
        tap.eq(day_range_by_datetime(dt), day,
               'correct day check')

        next_dt = dt + datetime.timedelta(days=1)
        next_day = (
            day_start + datetime.timedelta(days=1),
            day_start + datetime.timedelta(days=2),
        )
        tap.eq(day_range_by_datetime(next_dt), next_day,
               'correct next day check')
