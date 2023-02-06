import datetime

from libstall.util import pp_timedelta


async def test_pp_timedelta(tap):
    with tap:
        t = pp_timedelta(datetime.timedelta(days=6))
        tap.eq(t, {'days': 6}, 'Конверсия дней')

        t = pp_timedelta(datetime.timedelta(days=14))
        tap.eq(t, {'weeks': 2}, 'Конверсия недель')

        t = pp_timedelta(datetime.timedelta(days=13))
        tap.eq(t, {'weeks': 1, 'days': 6}, 'Конверсия дней и недель')

        t = pp_timedelta(datetime.timedelta(milliseconds=500))
        tap.eq(t, {'milliseconds': 500}, 'Конверсия милисекунд')

        t = pp_timedelta(datetime.timedelta(microseconds=100))
        tap.eq(t, {'milliseconds': 0.1}, 'Конверсия микросекунд')

        t = pp_timedelta(None)
        tap.is_ok(t, None, 'None')
