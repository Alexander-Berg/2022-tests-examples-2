import datetime

from dateutil.tz import tzlocal

from libstall import json_pp
from libstall.model import coerces
from libstall.util import tzone


async def test_datetime(tap):
    with tap.plan(4, 'date_time'):
        tap.eq(
            coerces.date_time('2012-11-12'),
            datetime.datetime(
                2012, 11, 12, 0, 0, 0, tzinfo=tzone('UTC'),
            ),
            'Конверсия даты'
        )

        tap.eq(
            coerces.date_time('2012-11-12 23:32:11'),
            datetime.datetime(
                2012, 11, 12, 23, 32, 11,
                tzinfo=tzone('UTC'),
            ),
            'Конверсия даты и времени'
        )

        tap.eq(
            coerces.date_time('2012-11-12 23:32:11+0300'),
            datetime.datetime(
                2012, 11, 12, 23, 32, 11,
                tzinfo=tzone('+0300'),
            ),
            'Конверсия даты, времени и зоны'
        )

        tap.eq(
            coerces.date_time(1644942702),
            datetime.datetime(
                2022, 2, 15, 19, 31, 42,
                tzinfo=tzlocal(),
            ),
            'Конверсия даты, времени и зоны'
        )


def test_coerce_json_pp(tap):
    with tap.plan(7):
        d = coerces.date_time(json_pp.loads(json_pp.dumps('2012-11-12')))
        tap.isa_ok(d, datetime.datetime, 'Конверсия даты')

        dt = coerces.date_time('2012-11-12 23:32:11')
        tap.isa_ok(dt, datetime.datetime, 'Конверсия даты и времени')

        dt2 = coerces.date_time(json_pp.loads(json_pp.dumps(dt)))
        tap.isa_ok(dt2, datetime.datetime, 'Конверсия даты и времени из json')
        tap.eq(dt2.timestamp(), dt.timestamp(), 'время соответствует')

        dtz = coerces.date_time('2012-11-12 23:32:11+0300')
        tap.isa_ok(dtz, datetime.datetime, 'Конверсия даты, времени и зоны')

        dtz2 = coerces.date_time(json_pp.loads(json_pp.dumps(dtz)))
        tap.isa_ok(dtz2,
                   datetime.datetime,
                   'Конверсия даты, времени и зоны из json')
        tap.eq(dtz2.timestamp(), dtz.timestamp(), 'время соответствует')
