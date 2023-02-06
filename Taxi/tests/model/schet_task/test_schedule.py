import datetime

from mouse.exception import ErFieldUndefined
import pytest

from libstall.model import coerces
from stall.model.schedule import Schedule


@pytest.mark.parametrize('start_time', [
    '2020-01-01T20:00+00:00',
    datetime.datetime(2020, 1, 1, 20, tzinfo=datetime.timezone.utc),
])
@pytest.mark.parametrize('interval', [
    {'hours': 1},
    datetime.timedelta(hours=1),
])
async def test_schedule(tap, interval, start_time):
    with tap.plan(4, 'сериализация/десериализация'):
        s = Schedule({
            'start_time': start_time,
            'interval': interval
        })
        tap.ok(s, 'Schedule')
        tap.isa(s.start_time, datetime.datetime, 'start_time is datetime')
        tap.isa(s.interval, datetime.timedelta, 'interval is timedelta')

        tap.eq(s.pure_python(), {
            'start_time': datetime.datetime(
                2020, 1, 1, 20, tzinfo=datetime.timezone.utc),
            'interval': datetime.timedelta(hours=1)
        }, 'pure_python')


async def test_coerce(tap):
    with tap.plan(8, 'проверка coerce'):
        s = Schedule.coerce({
            'start_time': '2020-01-01T20:00+00:00',
            'interval': {'hours': 1}
        })
        tap.isa(s, Schedule, 'Schedule from dict')

        s1 = Schedule.coerce(s)
        tap.isa(s1, Schedule, 'Schedule from Schedule')
        tap.ok(s1 is not s, 'Not link')
        tap.ok(s1 == s, 'But copy')

        s2 = Schedule.coerce(None)
        tap.is_ok(s2, None, 'None')

        with tap.raises(ErFieldUndefined):
            Schedule.coerce({
                'start_time': '2020-01-01T20:00+00:00',
            })

        s3 = Schedule.coerce({
            'interval': {'hours': 1}
        })
        tap.isa(s3, Schedule, 'Schedule with default start_time')

        with tap.raises(ErFieldUndefined):
            Schedule.coerce({})


@pytest.mark.parametrize('test_data', [
    dict(
        start_time='2020-01-01T21:00+0000',
        prev_run  ='2020-01-01T22:00+0000',
        now       ='2020-01-01T22:00+0000',
        next_run  ='2020-01-01T23:00+0000'
    ),
    dict(
        start_time='2020-01-01T21:00+0000',
        prev_run  ='2020-01-01T21:00+0000',
        now       ='2020-01-01T21:00+0000',
        next_run  ='2020-01-01T22:00+0000'
    ),
    dict(
        start_time='2020-01-01T21:00+0000',
        prev_run  ='2020-01-01T22:00+0000',
        now       ='2020-01-01T23:00+0000',
        next_run  ='2020-01-02T00:00+0000'
    ),
    dict(
        start_time='2020-01-01T21:00+0000',
        prev_run  ='2020-01-01T22:00+0000',
        now       ='2020-01-02T19:30+0000',
        next_run  ='2020-01-02T20:00+0000'
    ),
    dict(
        start_time='2020-01-01T21:00+00:00',
        prev_run  =None,
        now       ='2020-01-01T10:00+00:00',
        next_run  ='2020-01-01T21:00+00:00'
    ),
])
async def test_get_next_run(tap, test_data):
    with tap.plan(1, 'ближайший следующий запуск'):
        s = Schedule({
            'start_time': test_data['start_time'],
            'interval': {'hours': 1},
        })
        next_run = s.get_next_run(
            coerces.date_time(test_data['prev_run']),
            coerces.date_time(test_data['now']),
        )
        tap.eq(next_run, coerces.date_time(test_data['next_run']), 'ok')
