from datetime import datetime, timedelta, timezone

from libstall.model import coerces
from libstall.util import (
    time2time, time2iso, time2iso_utc, tzone, time_has_come, int2time,
)


def test_tzone(tap):
    with tap.plan(6, 'Парсинг временной зоны'):

        moscow = tzone(timezone(timedelta(hours=+3)))

        tap.ok(tzone(moscow), moscow, 'timezone')
        tap.eq(tzone(timedelta(hours=+3)), moscow, 'timedelta')
        tap.eq(tzone(+3), moscow, '+3')
        tap.eq(tzone('+03:00'), moscow, '+03:00')
        tap.eq(tzone('+0300'), moscow, '+0300')
        tap.eq(tzone('Europe/Moscow'), moscow, 'Europe/Moscow')


def test_tzone_dst(tap):
    with tap.plan(2, 'Летнее и зименее'):

        # Дата в летнем времени
        dst = datetime(2021, 10, 1, 0, 0, 0)
        # Дата в зименем времени
        std = datetime(2021, 11, 1, 0, 0, 0)

        tap.eq(
            tzone('Europe/Paris', dst),
            tzone(timezone(timedelta(hours=+2))),
            'dst'
        )
        tap.eq(
            tzone('Europe/Paris', std),
            tzone(timezone(timedelta(hours=+1))),
            'std'
        )


def test_time2time(tap):
    with tap.plan(9, 'Значение в объект datetime'):
        tap.eq(
            time2time('2020-06-25T12:15:21.501229+03:00'),
            datetime(
                2020, 6, 25, 12, 15, 21,
                tzinfo=timezone(timedelta(hours=+3))
            ),
            'Строка'
        )
        tap.eq(
            time2time('2020-06-25T12:15:21.501229'),
            datetime(
                2020, 6, 25, 12, 15, 21,
                tzinfo=timezone.utc,
            ),
            'Строка без часового пояса'
        )
        tap.eq(
            time2time('2012-11-12 23:32:11+0300'),
            datetime(
                2012, 11, 12, 23, 32, 11,
                tzinfo=timezone(timedelta(hours=+3))
            ),
            'SQL'
        )
        tap.eq(
            time2time('2020-01-01T20:00'),
            datetime(
                2020, 1, 1, 20, 0, 0,
                tzinfo=timezone.utc,
            ),
            'Еще один странный формат'
        )
        tap.eq(
            time2time('2020-01-01T20:11+00:00'),
            datetime(
                2020, 1, 1, 20, 11, 0,
                tzinfo=timezone.utc,
            ),
            'Еще один странный формат 2'
        )
        tap.eq(
            time2time('2020-01-01T20:22+0000'),
            datetime(
                2020, 1, 1, 20, 22, 0,
                tzinfo=timezone.utc,
            ),
            'Еще один странный формат 3'
        )
        tap.eq(
            time2time(1593076521.501229),
            datetime(2020, 6, 25, 9, 15, 21, tzinfo=timezone.utc),
            'Число не содержит tz'
        )
        tap.eq(
            time2time(datetime(2020, 6, 25, 12, 15, 21)),
            datetime(2020, 6, 25, 12, 15, 21, tzinfo=timezone.utc),
            'Без tz'
        )
        tap.eq(
            time2time(
                datetime(
                    2020, 6, 25, 12, 15, 21, 501229,
                    tzinfo=timezone(timedelta(hours=+3))
                )
            ),
            datetime(
                2020, 6, 25, 12, 15, 21,
                tzinfo=timezone(timedelta(hours=+3))
            ),
            'Объект'
        )


def test_time2time_fail(tap):
    with tap.plan(3, 'невалидные данные'):

        tap.eq(time2time(None), None, 'None')
        tap.eq(time2time(''), None, 'пустая строка')
        tap.eq(time2time('UNKNOWN'), None, 'невалидная строка')


def test_time2time_tz(tap):
    with tap.plan(7, 'Значение в объект datetime с передачей новой tz'):
        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                timezone(timedelta(hours=+2))
            ),
            datetime(
                2020, 6, 25, 11, 15, 21,
                tzinfo=timezone(timedelta(hours=+2))
            ),
            'Смена временной зоны'
        )

        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                -2,
            ),
            datetime(
                2020, 6, 25, 7, 15, 21,
                tzinfo=timezone(timedelta(hours=-2))
            ),
            'tz число'
        )

        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                '-02:30',
            ),
            datetime(
                2020, 6, 25, 6, 45, 21,
                tzinfo=timezone(timedelta(hours=-2, minutes=-30))
            ),
            'tz строка с временем с ":"'
        )
        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                '-0230',
            ),
            datetime(
                2020, 6, 25, 6, 45, 21,
                tzinfo=timezone(timedelta(hours=-2, minutes=-30))
            ),
            'tz строка с временем без ":"'
        )
        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                '-02',
            ),
            datetime(
                2020, 6, 25, 7, 15, 21,
                tzinfo=timezone(timedelta(hours=-2))
            ),
            'tz строка с временем чтолько часы'
        )

        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                'UTC',
            ),
            datetime(2020, 6, 25, 9, 15, 21, tzinfo=timezone.utc),
            'tz строка UTC'
        )

        tap.eq(
            time2time(
                '2020-06-25T12:15:21.501229+03:00',
                'Europe/Amsterdam',
            ),
            datetime(
                2020, 6, 25, 11, 15, 21,
                tzinfo=timezone(timedelta(hours=2))
            ),
            'tz строка с именем зоны'
        )


def test_time2time_other(tap):
    with tap.plan(4, 'Другие объекты'):

        tap.eq(
            time2time('2020-06-25'),
            datetime(2020, 6, 25, 0, 0, 0, 0, tzinfo=timezone.utc),
            'Дата'
        )
        tap.eq(
            time2time('2020-06-03'),
            datetime(2020, 6, 3, 0, 0, 0, 0, tzinfo=timezone.utc),
            'Дата'
        )

        now = datetime.utcnow()
        tap.eq(
            time2time('12:15:21.501229'),
            datetime(
                now.year, now.month, now.day,
                12, 15, 21, 0,
                tzinfo=timezone.utc
            ),
            'Время'
        )

        now = datetime.now().astimezone(timezone(timedelta(hours=+5)))
        tap.eq(
            time2time('23:15:21.501229+05:00'),
            datetime(
                now.year, now.month, now.day,
                23, 15, 21, 0,
                tzinfo=timezone(timedelta(hours=+5))
            ),
            'Время с часовым поясом'
        )


def test_time2time_ru(tap):
    with tap.plan(5, 'Даты в локале RU'):

        tap.eq(
            time2time('3.6.2020 12:15:21+03:00'),
            datetime(
                2020, 6, 3, 12, 15, 21,
                tzinfo=timezone(timedelta(hours=+3))
            ),
            'Строка RU'
        )
        tap.eq(
            time2time('3.6.2020 12:15:21+0300'),
            datetime(
                2020, 6, 3, 12, 15, 21,
                tzinfo=timezone(timedelta(hours=+3))
            ),
            'Строка RU, таймзона без разделителя'
        )

        tap.eq(
            time2time('25.6.2020'),
            datetime(2020, 6, 25, 0, 0, 0, 0, tzinfo=timezone.utc),
            'Дата RU'
        )

        # Без локали тут 3 станет месяцем а 6 днем
        tap.eq(
            time2time('3.6.2020'),
            datetime(2020, 6, 3, 0, 0, 0, 0, tzinfo=timezone.utc),
            'Дата RU'
        )
        tap.eq(
            time2time('01.12.2020'),
            datetime(2020, 12, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
            'Дата RU'
        )


def test_time2time_dst(tap):
    with tap.plan(2, 'Летнее и зименее время'):

        dst = time2time('2021-10-01T00:00:00', tz='Europe/Paris')
        tap.eq(
            dst,
            datetime(
                2021, 10, 1, 2, 0, 0, 0,
                tzinfo=timezone(timedelta(hours=+2))
            ),
            'dst'
        )

        std = time2time('2021-11-01T00:00:00', tz='Europe/Paris')
        tap.eq(
            std,
            datetime(
                2021, 11, 1, 1, 0, 0, 0,
                tzinfo=timezone(timedelta(hours=+1))
            ),
            'std'
        )


def test_time2iso(tap):
    with tap.plan(5, 'Значение в строку ISO'):
        tap.eq(time2time(None), None, 'None')

        tap.eq(
            time2iso('2020-06-25T12:15:21.501229+03:00'),
            '2020-06-25T12:15:21+03:00',
            'Строка'
        )
        tap.eq(
            time2iso(1593076521.501229),
            '2020-06-25T09:15:21+00:00',
            'Число не содержит tz'
        )
        tap.eq(
            time2iso(datetime(2020, 6, 25, 12, 15, 21)),
            '2020-06-25T12:15:21+00:00',
            'Без tz'
        )
        tap.eq(
            time2iso(
                datetime(
                    2020, 6, 25, 12, 15, 21, 501229,
                    tzinfo=timezone(timedelta(hours=+3))
                )
            ),
            '2020-06-25T12:15:21+03:00',
            'Объект'
        )
#         tap.eq(
#             time2iso(
#                 datetime(2020, 6, 25, 12, 15, 21),
#                 'Europe/Amsterdam',
#             ),
#             '2020-06-25T14:15:21+02:00',
#             'без tz, но с приведением tz строка с именем зоны'
#         )


def test_time2iso_utc(tap):
    with tap.plan(5, 'Значение в строку ISO в UTC'):
        tap.eq(time2time(None), None, 'None')

        tap.eq(
            time2iso_utc('2020-06-25T12:15:21.501229+03:00'),
            '2020-06-25T09:15:21+00:00',
            'Строка'
        )
        tap.eq(
            time2iso_utc(1593076521.501229),
            '2020-06-25T09:15:21+00:00',
            'Число'
        )
        tap.eq(
            time2iso_utc(datetime(2020, 6, 25, 12, 15, 21)),
            '2020-06-25T12:15:21+00:00',
            'Без tz'
        )
        tap.eq(
            time2iso_utc(
                datetime(
                    2020, 6, 25, 12, 15, 21, 501229,
                    tzinfo=timezone(timedelta(hours=+3))
                )
            ),
            '2020-06-25T09:15:21+00:00',
            'Объект'
        )


async def test_time2time_perf(tap, perfomance):
    with tap.plan(1, 'Скорость работы со временем'):

        async def _test():
            time2time('2020-06-25T12:15:21.501229+03:00')

        count, total_time = await perfomance(_test)

        tap.ok(count > 1000, f'RPS: {count / total_time}')


async def test_time2time_ru_perf(tap, perfomance):
    with tap.plan(1, 'Скорость работы со временем RU'):

        async def _test():
            time2time('3.6.2020 12:15:21.501229+03:00')

        count, total_time = await perfomance(_test)

        tap.ok(count > 100, f'RPS: {count / total_time}')


async def test_time_has_come(tap):
    with tap:
        time = coerces.date_time('2020-01-01T21:00+00:00')
        now = coerces.date_time('2020-01-01T22:00+00:00')
        tap.ok(time_has_come(time, now), 'at 2020-01-01T21:00 (>)')

        time = coerces.date_time('2020-01-01T21:00+00:00')
        now = coerces.date_time('2020-01-01T21:00+00:00')
        tap.ok(time_has_come(time, now), 'at 2020-01-01T21:00 (=)')

        time = coerces.date_time('2020-01-01T21:00+00:00')
        now = coerces.date_time('2020-01-01T20:30+00:00')
        tap.ok(not time_has_come(time, now), 'at 2020-01-01T21:00 (<)')

        time = coerces.date_time('2020-01-01T21:00+00:00')
        now = coerces.date_time('2020-01-01T21:20+00:00')
        tap.ok(
            not time_has_come(time, now, timedelta(minutes=10)),
            'tolerance exceeded'
        )

        time = coerces.date_time('2020-01-01T21:00+00:00')
        now = coerces.date_time('2020-01-01T21:10+00:00')
        tap.ok(
            time_has_come(time, now, timedelta(minutes=10)),
            'tolerance ok'
        )

        time = coerces.date_time('2020-01-01T21:00+00:00')
        now = None
        tap.ok(time_has_come(time, now), 'real time ok')


def test_int2time(tap):
    with tap.plan(5, 'Конвертация секунд в форматированное время'):
        tap.eq(int2time(0), '00:00:00', '0 → 00:00:00')
        tap.eq(int2time(1), '00:00:01', '1 → 00:00:01')
        tap.eq(int2time(60), '00:01:00', '60 → 00:01:00')
        tap.eq(int2time(3600), '01:00:00', '3600 → 01:00:00')
        tap.eq(int2time(45296), '12:34:56', '45296 → 12:34:56')


def test_dst(tap):
    with tap.plan(6, 'Учет зимнего/летнего времени'):

        tap.eq(
            time2time(
                '2021-10-01T00:00:00+00:00',
                'Europe/Paris'
            ),
            datetime(
                2021, 10, 1, 2, 0, 0,
                tzinfo=timezone(timedelta(hours=+2))
            ),
            'Летнее время +2'
        )

        tap.eq(
            time2time(
                '2021-12-01T00:00:00+00:00',
                'Europe/Paris'
            ),
            datetime(
                2021, 12, 1, 1, 0, 0,
                tzinfo=timezone(timedelta(hours=+1))
            ),
            'Зимнее время +1'
        )

        tap.eq(
            time2time(
                '2021-10-31T01:59:00+01:00',
                'Europe/Paris'
            ),
            datetime(
                2021, 10, 31, 2, 59, 0,
                tzinfo=timezone(timedelta(hours=+2))
            ),
            'перевод часов, за минуту до'
        )
        tap.eq(
            time2time(
                '2021-10-31T03:00:00+02:00',
                'Europe/Paris'
            ),
            datetime(
                2021, 10, 31, 2, 0, 0,
                tzinfo=timezone(timedelta(hours=+1))
            ),
            'перевод часов, надо переводить'
        )
        tap.eq(
            time2time(
                '2021-10-31T03:01:00+02:00',
                'Europe/Paris'
            ),
            datetime(
                2021, 10, 31, 2, 1, 0,
                tzinfo=timezone(timedelta(hours=+1))
            ),
            'перевод часов, после перевода на час назад'
        )

        tap.eq(
            time2time(
                '2021-10-31T02:01:00+01:00',
                'Europe/Paris'
            ),
            datetime(
                2021, 10, 31, 2, 1, 0,
                tzinfo=timezone(timedelta(hours=+1))
            ),
            'время, которое не существует: AmbiguousTimeError. '
            'должно было быть переведено на час вперед'
        )
