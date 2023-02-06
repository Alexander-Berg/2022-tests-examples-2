from datetime import datetime, time, timezone, timedelta

import pytest
import pytz

from libstall.model.coerces import time as coerce_time
from libstall.timetable import TimeTable, TimeTableItem
from libstall.util import tzone


def test_timetableitem(tap, now):
    with tap.plan(7, 'разные кейсы создания item'):
        item = TimeTableItem({
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        })
        tap.ok(item, 'Элемент расписания')

        with tap.raises(ValueError):
            TimeTableItem({
                'type': 'day_interval',
                'begin': '01:00',
                'end': '02:00',
                'start': now().date(),
            })

        with tap.raises(ValueError):
            TimeTableItem({
                'type': 'day_interval',
                'begin': '01:00',
                'end': '02:00',
                'repeat': 0,
                'start': now().date(),
            })
        with tap.raises(ValueError):
            TimeTableItem({
                'type': 'day_interval',
                'begin': '01:00',
                'end': '02:00',
                'repeat': 1,
            })

        item = TimeTableItem({
            'type': 'day_interval',
            'begin': '01:00',
            'end': '02:00',
            'repeat': 1,
            'start': str(now().date()),
        })
        tap.ok(item, 'создали item')

        item = TimeTableItem({
            'type': 'day_interval',
            'begin': '01:00',
            'end': '02:00',
            'repeat': 1,
            'start': '2222-12-22',
        })
        tap.ok(item, 'создали item')

        with tap.raises(ValueError):
            TimeTableItem({
                'type': 'day_interval',
                'begin': '01:00',
                'end': '02:00',
                'repeat': 1,
                'start': '2222-22-12',
            })


def test_timezones(tap, now):
    with tap.plan(3, 'тестируем равенство инстансов при разных таймзонах'):
        time_params = {'hour': 12, 'minute': 12, 'second': 0, 'microsecond': 0}
        item_usual = TimeTableItem({
            'type': 'everyday',
            'begin': '12:12',
            'end': '12:12',
        })

        cur_time_1 = (
            now(pytz.timezone('Europe/London')).replace(**time_params)
        )
        item_1 = TimeTableItem({
            'type': 'everyday',
            'begin': cur_time_1,
            'end': cur_time_1,
        })

        cur_time_2 = (
            now(pytz.timezone('America/New_York')).replace(**time_params)
        )
        item_2 = TimeTableItem({
            'type': 'everyday',
            'begin': cur_time_2,
            'end': cur_time_2,
        })

        tap.ok(cur_time_1 != cur_time_2, 'время различается')
        tap.ok(item_usual == item_1, 'а объекты нет #1')
        tap.ok(item_usual == item_2, 'а объекты нет #2')


def test_timetable(tap):
    with tap.plan(4):
        tt1 = TimeTable()
        tap.ok(tt1, 'Расписание работы по умолчанию')
        tap.eq(tt1.value, [], 'pure_python')

        tt2 = TimeTable([])
        tap.ok(tt2, 'Пустое расписание работы')
        tap.eq(tt1.value, [], 'pure_python')


def test_timetable_filled(tap):
    with tap.plan(7):

        time1 = TimeTableItem({
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        })
        time2 = TimeTableItem({
            'type':     'tuesday',
            'begin':    '08:00',
            'end':      '20:00',
        })

        tt = TimeTable([time1, time2])
        tap.ok(tt, 'Расписание работы')

        with tt.value[0] as item:
            tap.eq(item.type, 'monday', 'type')
            tap.eq(item.begin, time(7, 0), 'begin')
            tap.eq(item.end, time(19, 0), 'end')

        with tt.value[1] as item:
            tap.eq(item.type, 'tuesday', 'type')
            tap.eq(item.begin, time(8, 0), 'begin')
            tap.eq(item.end, time(20, 0), 'end')


def test_timetable_today(tap):
    with tap.plan(3, 'Приоритетный интервал на указанную дату'):

        time1 = TimeTableItem({
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        })
        time2 = TimeTableItem({
            'type':     'tuesday',
            'begin':    '08:00',
            'end':      '20:00',
        })
        time3 = TimeTableItem({
            'type':     'everyday',
            'begin':    '08:00',
            'end':      '20:00',
        })
        time4 = TimeTableItem({
            'type':     'workday',
            'begin':    '08:00',
            'end':      '20:00',
        })

        tt = TimeTable([time1, time2, time3, time4])
        tap.ok(tt, 'Расписание работы')

        today = tt.today(datetime(2020, 1, 6, 10, 15))
        tap.eq(len(today.value), 1, 'Список получен')

        with today.value[0] as item:
            tap.eq(item.type, 'monday', 'Самый приоритетный')


def test_timetable_today_many(tap):
    with tap.plan(8, 'Список интервалов одного типа'):

        time1 = TimeTableItem({
            'type':     'monday',
            'begin':    '12:00',
            'end':      '15:00',
        })
        time2 = TimeTableItem({
            'type':     'monday',
            'begin':    '17:00',
            'end':      '23:00',
        })
        time3 = TimeTableItem({
            'type':     'everyday',
            'begin':    '08:00',
            'end':      '20:00',
        })
        time4 = TimeTableItem({
            'type':     'monday',
            'begin':    '08:00',
            'end':      '11:00',
        })

        tt = TimeTable([time1, time2, time3, time4])
        tap.ok(tt, 'Расписание работы')

        today = tt.today(datetime(2020, 1, 6, 10, 15))
        tap.eq(len(today.value), 3, 'Список получен')

        with today.value[0] as item:
            tap.eq(item.type, 'monday', 'Тип')
            tap.eq(item.end, time(11, 0), 'первый')

        with today.value[1] as item:
            tap.eq(item.type, 'monday', 'Тип')
            tap.eq(item.end, time(15, 0), 'второй')

        with today.value[2] as item:
            tap.eq(item.type, 'monday', 'Тип')
            tap.eq(item.end, time(23, 0), 'третий')


def test_timetable_today_ended(tap):
    with tap.plan(7, 'today_ended - завершенные на сегодня интервалы'):

        time3 = TimeTableItem({
            'type':     'monday',
            'begin':    '08:00',
            'end':      '20:00',
        })
        time1 = TimeTableItem({
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        })
        time2 = TimeTableItem({
            'type':     'everyday',
            'begin':    '08:00',
            'end':      '20:00',
        })

        tt = TimeTable([time1, time2, time3])
        tap.ok(tt, 'Расписание работы')

        with tt.today_ended(datetime(2020, 1, 6, 18, 0)) as today:
            tap.eq(len(today.value), 0, 'Список пуст')

        with tt.today_ended(datetime(2020, 1, 6, 19, 30)) as today:
            tap.eq(len(today.value), 1, 'Список получен')
            with today.value[0] as item:
                tap.eq(item.type, 'monday', 'Тип')

        with tt.today_ended(datetime(2020, 1, 6, 20, 30)) as today:
            tap.eq(len(today.value), 2, 'Список получен')
            with today.value[0] as item:
                tap.eq(item.type, 'monday', 'Тип')
            with today.value[1] as item:
                tap.eq(item.type, 'monday', 'Тип')


def test_timetable_is_active(tap):
    with tap.plan(4, 'is_active - есть не прошедшие интервалы'):

        tt1 = TimeTable([])
        tap.eq(tt1.is_active(), False, 'Интервалов нет')

        tt2 = TimeTable([{
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        }])
        tap.eq(
            tt2.is_active(datetime(2020, 1, 6, 1, 0)),
            True,
            'Будущий интервал'
        )

        tt3 = TimeTable([{
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        }])
        tap.eq(
            tt3.is_active(datetime(2020, 1, 6, 9, 0)),
            True,
            'Текущий интервал'
        )

        tt4 = TimeTable([{
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        }])
        tap.eq(
            tt4.is_active(datetime(2020, 1, 6, 22, 0)),
            False,
            'Прошедший интервал'
        )


def test_is_working(tap):
    with tap.plan(6, 'Функция проверки интревала внутри рабочих часов.'):

        now = datetime(2020, 1, 6, 12, 0, 0, tzinfo=tzone('Europe/Moscow'))

        tt = TimeTable([{
            'type':     'everyday',
            'begin':    '07:00',
            'end':      '19:00',
        }])
        tap.eq(
            tt.is_working(
                datetime(2020, 1, 6, 12, 0, 0, tzinfo=now.tzinfo),
                datetime(2020, 1, 6, 13, 0, 0, tzinfo=now.tzinfo),
                now,
            ),
            True,
            'Интервал внутри'
        )

        tap.eq(
            tt.is_working(
                datetime(2020, 1, 6, 7, 0, 0, tzinfo=now.tzinfo),
                datetime(2020, 1, 6, 19, 0, 0, tzinfo=now.tzinfo),
                now,
            ),
            True,
            'Весь интервал'
        )

        tap.eq(
            tt.is_working(
                datetime(2020, 1, 6, 4, 0, 0, tzinfo=now.tzinfo),
                datetime(2020, 1, 6, 5, 0, 0, tzinfo=now.tzinfo),
                now,
            ),
            False,
            'Интервал раньше'
        )

        tap.eq(
            tt.is_working(
                datetime(2020, 1, 6, 22, 0, 0, tzinfo=now.tzinfo),
                datetime(2020, 1, 6, 23, 0, 0, tzinfo=now.tzinfo),
                now,
            ),
            False,
            'Интервал позже'
        )

        tap.eq(
            tt.is_working(
                datetime(2020, 1, 6, 6, 0, 0, tzinfo=now.tzinfo),
                datetime(2020, 1, 6, 10, 0, 0, tzinfo=now.tzinfo),
                now,
            ),
            False,
            'Интервал не целиком раньше'
        )

        tap.eq(
            tt.is_working(
                datetime(2020, 1, 6, 18, 0, 0, tzinfo=now.tzinfo),
                datetime(2020, 1, 6, 22, 0, 0, tzinfo=now.tzinfo),
                now,
            ),
            False,
            'Интервал не целиком позже'
        )


async def test_is_working_around_midnight(tap):
    with tap.plan(8, 'Работа с интеравалами около полуночи'):
        tzinfo = tzone('Europe/Moscow')

        right_after_midnight = datetime(2018, 2, 2, 0, 40, 0, tzinfo=tzinfo)
        before_midnight = datetime(2018, 2, 1, 23, 40, 0, tzinfo=tzinfo)

        tt = TimeTable([{
            'type':     'everyday',
            'begin':    '22:00',
            'end':      '02:00',
        }])
        tap.eq(
            tt.is_working(
                right_after_midnight,
                right_after_midnight,
                right_after_midnight
            ),
            True,
            'Дата внутри интервала'
        )

        tap.eq(
            tt.is_working(
                before_midnight,
                before_midnight,
                before_midnight,
            ),
            True,
            'Дата внутри интервала'
        )
        tap.eq(
            tt.is_working(
                datetime(2018, 2, 1, 23, 40, 0, tzinfo=tzinfo),
                datetime(2018, 2, 2, 1, 10, 0, tzinfo=tzinfo),
                right_after_midnight
            ),
            True,
            'Интервал внутри'
        )
        tap.eq(
            tt.is_working(
                datetime(2018, 2, 1, 23, 40, 0, tzinfo=tzinfo),
                datetime(2018, 2, 2, 1, 10, 0, tzinfo=tzinfo),
                before_midnight,
            ),
            True,
            'Интервал внутри'
        )

        tt = TimeTable([{
            'type': 'thursday',
            'begin': '22:00',
            'end': '02:00',
        }])
        tap.eq(
            tt.is_working(
                right_after_midnight,
                right_after_midnight,
                right_after_midnight
            ),
            False,
            'Уже пятница, не попал'
        )

        tap.eq(
            tt.is_working(
                before_midnight,
                before_midnight,
                before_midnight,
            ),
            True,
            'Четверг, еще попал'
        )
        tap.eq(
            tt.is_working(
                datetime(2018, 2, 1, 23, 40, 0, tzinfo=tzinfo),
                datetime(2018, 2, 1, 23, 55, 0, tzinfo=tzinfo),
                before_midnight,
            ),
            True,
            'Интервал попал'
        )
        tap.eq(
            tt.is_working(
                datetime(2018, 2, 2, 0, 40, 0, tzinfo=tzinfo),
                datetime(2018, 2, 2, 1, 10, 0, tzinfo=tzinfo),
                before_midnight,
            ),
            False,
            'Интервал не попал'
        )


@pytest.mark.parametrize('tt_begin, tt_end, cases', [
    (
        (23, 00),
        (00, 00),
        {
            (22, 59): False,
            (23, 00): True,
            (23, 30): True,
            (23, 59): True,
            (0, 0): False,
            (0, 1): False,
        },
    ),
    (
        (00, 00),
        (00, 00),
        {
            (23, 59): True,
            (0, 0): True,
            (0, 1): True,
        }
    ),
])
def test_is_working_at_midnight(tap, tt_begin, tt_end, cases):
    with tap.plan(2 + len(cases), 'тестим интервалы заканчивающиеся в 00:00'):
        tt = TimeTable([{
            'type': 'everyday',
            'begin': time(tt_begin[0], tt_begin[1]),
            'end': time(tt_end[0], tt_end[1]),
        }])

        now = datetime(2022, 2, 22, 16, 20)
        today = tt.today(now)
        tap.eq(len(today.value), 1, 'не разбивали')

        tap.eq(
            (today.value[0].begin, today.value[0].end),
            (
                time(tt_begin[0], tt_begin[1]),
                time(tt_end[0], tt_end[1]),
            ),
            f'интервал {tt_begin[0]:02}ч-{tt_end[0]:02}ч',
        )

        for t, res in cases.items():
            tap.eq(
                tt.is_working(
                    now.replace(hour=t[0], minute=t[1]),
                    now.replace(hour=t[0], minute=t[1]),
                    now,
                ),
                res,
                f'в {t[0]:02}:{t[1]:02} {"" if res else "не"}активно',
            )


@pytest.mark.parametrize('value', [
    {
        'type':     'monday',
        'begin':    '07:00',
        'end':      '19:00',
    },
    {
        'type':     'tuesday',
        'begin':    '08:00',
        'end':      '20:00',
    },
    {
        'type':     'everyday',
        'begin':    '08:00',
        'end':      '20:00',
    },
])
def test_timetable_item_eq(tap, value):
    with tap.plan(3):
        t1 = TimeTableItem(value)
        t2 = TimeTableItem(value)
        tap.eq_ok(t1, t2, 'Equal')
        t3 = TimeTableItem({
            'type': 'monday',
            'begin': '07:01',
            'end': '19:00',
        })
        tap.ok(t1 != t3, 'Not equal')
        tap.ok(t2 != t3, 'Not equal')


@pytest.mark.parametrize('value', [
    [
        {
            'type':     'monday',
            'begin':    '07:00',
            'end':      '19:00',
        },
        {
            'type':     'tuesday',
            'begin':    '08:00',
            'end':      '20:00',
        }
    ],
    [
        {
            'type':     'everyday',
            'begin':    '08:00',
            'end':      '20:00',
        }
    ],
])
def test_timetable_eq(tap, value):
    with tap.plan(3):
        t1 = TimeTable(value)
        t2 = TimeTable(value)
        tap.eq_ok(t1, t2, 'Equal')
        t3 = TimeTable([{
            'type': 'monday',
            'begin': '07:01',
            'end': '19:00',
        }])
        tap.ok(t1 != t3, 'Not equal')
        tap.ok(t2 != t3, 'Not equal')


def test_timetable_strip_seconds(tap):
    with tap.plan(8):
        t = TimeTable(
            [
                {
                    'type': 'everyday',
                    'begin': '08:00',
                    'end': '20:00',
                },
                {
                    'type': 'everyday',
                    'begin': '08:00:42',
                    'end': '20:00.42',
                },
            ]
        )

        for item in t.pure_python():
            tap.like(item['begin'], r'\d{2}:\d{2}:\d{2}', 'есть секунды')
            tap.like(item['end'], r'\d{2}:\d{2}:\d{2}', 'есть секунды')

        for item in t.pure_python(strip_seconds=True):
            tap.like(item['begin'], r'\d{2}:\d{2}', 'нет секунды')
            tap.like(item['end'], r'\d{2}:\d{2}', 'нет секунды')


def test_timetable_day_interval(tap):
    with tap.plan(4, 'тестируем работу day_interval'):
        t = TimeTable([
            {
                'type': 'day_interval',
                'begin': '23:00',
                'end': '01:00',
                'repeat': 1,
                'start': '2022-02-16',
            },
            {
                'type': 'day_interval',
                'begin': '12:00',
                'end': '12:00',
                'repeat': 2,
                'start': '2022-02-16',
            },
            {
                'type': 'day_interval',
                'begin': '20:00',
                'end': '20:00',
                'repeat': 3,
                'start': '2022-02-15',
            },
        ])

        tap.eq(
            len(t.today(datetime(2022, 2, 15, 0, 0, 0)).value),
            1,
            '15-го один интервал'
        )
        tap.eq(
            len(t.today(datetime(2022, 2, 16, 0, 0, 0)).value),
            3,
            '16-го три интервала'
        )
        tap.eq(
            len(t.today(datetime(2022, 2, 17, 0, 0, 0)).value),
            2,
            '17-го два интервала'
        )
        tap.eq(
            len(t.today(datetime(2022, 2, 18, 0, 0, 0)).value),
            4,
            '18-го четыре интервала'
        )


def test_day_interval_tz(tap, now):
    with tap.plan(16, 'тестим работу с таймзонами'):
        time_params = {
            'year': 2022, 'month': 2, 'day': 16,
            'hour': 12, 'minute': 12, 'second': 0, 'microsecond': 0,
        }
        t = TimeTable([
            {
                'type': 'day_interval',
                'begin': '12:00',
                'end': '13:00',
                'repeat': 1,
                'start': '2022-02-16',
            },
        ])

        cur_time1 = datetime(**time_params, tzinfo=timezone.utc)
        tap.ok(
            t.is_working(cur_time1, cur_time1, cur_time1),
            'точка входит в интервал 12-13'
        )

        cur_time2 = now(timezone.utc).replace(**time_params)
        tap.ok(
            t.is_working(cur_time2, cur_time2, cur_time2),
            'точка входит в интервал 12-13'
        )

        interval_sizes = [0,    10,   30,   47,   48,   49,    100]
        results =        [True, True, True, True, True, False, False]

        for i, isize in enumerate(interval_sizes):
            for ctime in [cur_time1, cur_time2]:
                tap.eq(
                    t.is_working(
                        ctime, ctime + timedelta(minutes=isize), ctime,
                    ),
                    results[i],
                    f'длина {isize} -> {results[i]}',
                )


def test_has_intersect_assert(tap):
    with tap.plan(4, 'проверяем ассерты в has_intersect'):
        t = TimeTable()
        tap.ok(
            not t.has_intersect(
                datetime(2022, 2, 21, 0, 0, 0),
                datetime(2022, 2, 21, 0, 0, 0),
            ),
            'нету ассерта',
        )
        tap.ok(
            not t.has_intersect(
                datetime(2022, 2, 21, 0, 0, 0),
                datetime(2022, 2, 21, 23, 0, 0),
            ),
            'нету ассерта',
        )
        tap.ok(
            not t.has_intersect(
                datetime(2022, 2, 21, 16, 20, 0),
                datetime(2022, 2, 22, 16, 20, 0),
            ),
            'нету ассерта'
        )
        with tap.raises(AssertionError):
            t.has_intersect(
                datetime(2022, 2, 21, 16, 20, 0),
                datetime(2022, 2, 21, 16, 19, 0),
            )


@pytest.mark.parametrize('tz', ['Europe/London', 'America/New_York'])
@pytest.mark.parametrize('tt_args, cases', [
    (
        ['13:00', '14:00'],
        {
            ('00:00', '12:59'): False,
            ('00:01', '12:59'): False,
            ('05:59', '12:01'): False,
            ('00:00', '12:01'): False,
            ('00:00', '13:00'): False,
            ('04:20', '13:00'): False,
            ('00:00', '13:01'): True,
            ('04:20', '13:01'): True,
            ('04:20', '14:00'): True,
            ('04:20', '14:01'): True,
            ('13:30', '13:30'): True,
            ('13:30', '14:01'): True,
            ('13:37', '00:00'): True,
            ('14:00', '00:00'): True,
            ('14:00', '14:00'): True,
            ('14:00', '14:01'): True,
            ('14:01', '14:01'): False,
            ('14:01', '00:00'): False,
            ('21:11', '00:00'): False,
            ('21:11', '23:23'): False,
        },
    ),
    (
        ['00:00', '01:00'],
        {
            ('00:00', '00:00'): False,
            ('00:00', '00:01'): True,
            ('00:31', '00:59'): True,
            ('00:31', '01:00'): True,
            ('00:31', '01:01'): True,
            ('01:00', '01:01'): True,
            ('01:01', '01:01'): False,
            ('01:01', '23:59'): False,
            ('01:01', '00:00'): False,
        },
    ),
    (
        ['23:00', '00:00'],
        {
            ('22:59', '22:59'): False,
            ('00:00', '00:00'): False,
            ('00:00', '22:59'): False,
            ('00:00', '23:00'): False,
            ('00:00', '23:01'): True,
            ('00:00', '23:59'): True,
            ('04:20', '13:37'): False,
            ('04:20', '04:20'): False,
            ('04:20', '13:37'): False,
            ('23:31', '23:31'): True,
            ('23:00', '00:00'): True,
            ('23:01', '00:00'): True,
            ('23:02', '23:59'): True,
        },
    ),
    (
        ['00:00', '00:00'],
        {
            ('00:00', '00:00'): False,
            ('00:00', '00:01'): True,
            ('00:01', '00:01'): True,
            ('00:01', '23:59'): True,
            ('00:01', '00:00'): True,
        },
    ),
    (
        ['13:37', '13:37'],
        {
            ('00:00', '13:00'): False,
            ('00:01', '13:36'): False,
            ('00:01', '13:37'): False,
            ('00:01', '13:38'): True,
            ('00:01', '00:00'): True,
            ('13:36', '00:00'): True,
            ('13:37', '00:00'): True,
            ('13:38', '00:00'): False,
            ('13:36', '23:59'): True,
            ('13:37', '23:59'): True,
            ('13:38', '23:59'): False,
        },
    ),
])
def test_has_intersect(tap, now, tz, tt_args, cases):
    with tap.plan(len(cases), 'тестим корректность пересечения'):
        def create_timetable(begin, end):
            return TimeTable([{
                'type': 'everyday',
                'begin': begin,
                'end': end,
            }])

        def create_args(begin, end):
            res = {
                'begin': datetime.combine(now, coerce_time(begin), now.tzinfo),
                'end': datetime.combine(now, coerce_time(end), now.tzinfo),
                'now': now,
            }
            if res['end'] < res['begin']:
                res['end'] += timedelta(days=1)
            return res

        now = now(tzone(tz))
        t = create_timetable(*tt_args)
        for interval_args, result in cases.items():
            tap.eq(
                t.has_intersect(**create_args(*interval_args)),
                result,
                f'интервал {interval_args[0]}-{interval_args[1]}'
                f'{"" if result else " не"} пересекается с '
                f'{tt_args[0]}-{tt_args[1]}'
            )
