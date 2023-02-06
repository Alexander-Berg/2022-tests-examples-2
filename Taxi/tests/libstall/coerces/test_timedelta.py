import datetime

from libstall.model import coerces


async def test_timedelta(tap):
    with tap:
        t = coerces.timedelta({'weeks': 2})
        tap.eq(t, datetime.timedelta(weeks=2), 'Конверсия недель')

        t = coerces.timedelta({'days': 14})
        tap.eq(t, datetime.timedelta(days=14), 'Конверсия дней')
        tap.eq(t, datetime.timedelta(weeks=2), 'Конверсия дней в недели')

        t = coerces.timedelta({'hours': 1, 'minutes': 30})
        tap.eq(t, datetime.timedelta(hours=1, minutes=30), 'Конверсия времени')

        t = coerces.timedelta({'hours': 1, 'minutes': 60})
        tap.eq(t, datetime.timedelta(hours=2), 'Конверсия времени в часы')

        t = coerces.timedelta({'milliseconds': 1.234})
        tap.eq(t, datetime.timedelta(microseconds=1234), 'Конверсия милисекунд')

        t = coerces.timedelta(None)
        tap.is_ok(t, None, 'None')
