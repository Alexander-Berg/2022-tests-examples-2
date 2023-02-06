from datetime import timedelta

import pytest

from stall.model.check_project import CheckProject, CheckProjectSchedule


async def test_check_schedule(tap, uuid, now):
    with tap.plan(7, 'тестируем корректность CheckSchedule'):
        now1 = now()
        now2 = now()

        cps1 = {
            'timetable': [
                {'type': 'everyday', 'begin': now1.time(), 'end': now2.time()}
            ],
            'begin': now1,
            'end': now2,
        }
        cps2 = {'begin': now1}
        cps3 = {'begin': now1, 'end': now2}
        cps4 = {'begin': now1, 'end': now1}
        cps5 = {
            'timetable': [
                {'type': 'everyday', 'begin': now1.time(), 'end': now1.time()}
            ],
            'begin': now1,
            'end': now2,
        }

        with tap.raises(ValueError):
            CheckProject({'title': uuid(), 'schedule': cps1})
        with tap.raises(ValueError):
            CheckProject(title=uuid(), schedule=cps1)
        with tap.raises(ValueError):
            CheckProject({'title': uuid(), 'schedule': cps2})
        with tap.raises(ValueError):
            CheckProject({'title': uuid(), 'schedule': cps3})

        cp1 = CheckProject({'title': uuid(), 'schedule': cps4})
        cp2 = CheckProject({'title': uuid(), 'schedule': cps5})

        tap.ok(await cp1.save(), 'первое cp сохранено')
        tap.ok(await cp2.save(), 'второе cp сохранено')

        with tap.raises(ValueError):
            cp1.schedule.end = None
            cp1.rehash(schedule=cp1.schedule)
            await cp1.save()


# лондон +1 нью-йорк -4
@pytest.mark.parametrize(
    'tz,td,ans',
    [
        ('Europe/London', timedelta(minutes=-21), False),
        ('Europe/London', timedelta(minutes=-20), True),
        ('Europe/London', timedelta(minutes=-19), True),
        ('Europe/London', timedelta(minutes=39), True),
        ('Europe/London', timedelta(minutes=40), False),
        ('Europe/London', timedelta(minutes=41), False),
        ('Europe/London', timedelta(days=1), False),
        ('Europe/London', timedelta(days=-1), False),
        ('America/New_york', timedelta(hours=6), False),
        ('America/New_york', timedelta(hours=5), True),
        ('America/New_york', timedelta(hours=4), False),
    ]
)
def test_schedule_iswrk_solo(tap, now, tzone, tz, td, ans):
    with tap.plan(1, 'тестим корректность разового запуска'):
        london_tz = tzone('Europe/London')

        _now = now(london_tz).replace(
            hour=4, minute=20, second=0, microsecond=0
        )

        cps_ok = CheckProjectSchedule(begin=_now, end=_now)
        _now_tz = _now.astimezone(tzone(tz)) + td
        res = cps_ok.is_working(_now_tz)
        tap.eq(
            res,
            ans,
            f'время {_now_tz.hour:02}:{_now_tz.minute:02} '
            f'в {tz} {"" if ans else "не "}подходит',
        )


# лондон +1 нью-йорк -4
@pytest.mark.parametrize(
    'tz,td,ans',
    [
        ('Europe/London', timedelta(minutes=-21), False),
        ('Europe/London', timedelta(minutes=-20), True),
        ('Europe/London', timedelta(minutes=-19), True),
        ('Europe/London', timedelta(minutes=39), True),
        ('Europe/London', timedelta(minutes=40), False),
        ('Europe/London', timedelta(minutes=41), False),
        ('Europe/London', timedelta(days=1, minutes=39), True),
        ('Europe/London', timedelta(days=-1), False),
        ('America/New_york', timedelta(hours=6), False),
        ('America/New_york', timedelta(hours=5), True),
        ('America/New_york', timedelta(hours=4), False),
        ('America/New_york', timedelta(hours=29), True),
        ('America/New_york', timedelta(hours=-19), False),
        ('America/New_york', timedelta(hours=29, minutes=40), False),
    ]
)
def test_schedule_iswrk_many(tap, now, tzone, tz, td, ans):
    with tap.plan(1, 'тестим корректность регулярного запуска'):
        london_tz = tzone('Europe/London')
        _now = now(london_tz).replace(
            hour=4, minute=20, second=0, microsecond=0
        )

        cps_ok = CheckProjectSchedule(
            timetable=[
                {
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }
            ],
            begin=_now,
            end=_now + timedelta(days=1),
        )
        _now_tz = _now.astimezone(tzone(tz)) + td
        res = cps_ok.is_working(_now_tz)
        tap.eq(
            res,
            ans,
            f'дата {_now_tz.day:02}:{_now_tz.month:02} и время '
            f'{_now_tz.hour:02}:{_now_tz.minute:02} '
            f'в {tz} {"" if ans else "не "}подходит',
        )


def test_schedule_iswrk_infty(tap, now):
    with tap.plan(8, 'тестируем корректность бесконечных локалок'):
        _now = now().replace(hour=4, minute=20, second=0, microsecond=0)

        cps_ok = CheckProjectSchedule(
            timetable=[
                {
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }
            ],
            begin=_now - timedelta(days=2),
        )

        tap.eq(
            cps_ok.is_working(_now - timedelta(days=3)),
            False,
            '3 дня назад не работало'
        )
        for i in range(-2, 5):
            tap.eq(
                cps_ok.is_working(_now + timedelta(days=i)),
                True,
                f'на {i} дней двигаем - работает',
            )
