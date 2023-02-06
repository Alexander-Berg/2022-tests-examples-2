from datetime import datetime

from libstall.timetable import TimeTable, TimeTableItem
from stall.model.gate_slot import GateSlot


async def test_everyday(tap, uuid):
    with tap.plan(9, 'Простое расписание на каджый день'):

        timetable = TimeTable([
            TimeTableItem({
                'type':     'everyday',
                'begin':    '08:00',
                'end':      '20:00',
            })
        ])

        slots = GateSlot.from_timetable(
            timetable,
            datetime(2020, 7, 1, 0, 0, 0),
            datetime(2020, 7, 3, 0, 0, 0),
            store_id=uuid(),
            gate_id=uuid(),
        )

        tap.eq(len(slots), 4, 'Слоты созданы')

        with slots[0] as slot:
            tap.note('Слот 0')
            tap.eq(slot.begin, datetime(2020, 7, 1, 0, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 1, 8, 0, 0), 'конец')

        with slots[1] as slot:
            tap.note('Слот 1')
            tap.eq(slot.begin, datetime(2020, 7, 1, 20, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 2, 0, 0, 0), 'конец')

        with slots[2] as slot:
            tap.note('Слот 2')
            tap.eq(slot.begin, datetime(2020, 7, 2, 0, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 2, 8, 0, 0), 'конец')

        with slots[3] as slot:
            tap.note('Слот 3')
            tap.eq(slot.begin, datetime(2020, 7, 2, 20, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 3, 0, 0, 0), 'конец')


async def test_everyday_alldays(tap, uuid):
    with tap.plan(1, '24/7'):

        timetable = TimeTable([
            TimeTableItem({
                'type':     'everyday',
                'begin':    '00:00',
                'end':      '00:00',
            })
        ])

        slots = GateSlot.from_timetable(
            timetable,
            datetime(2020, 7, 1, 0, 0, 0),
            datetime(2020, 7, 3, 0, 0, 0),
            store_id=uuid(),
            gate_id=uuid(),
        )

        tap.eq(len(slots), 0, 'Всегда работает')


async def test_begin(tap, uuid):
    with tap.plan(5, 'начало работы с 00:00'):

        timetable = TimeTable([
            TimeTableItem({
                'type':     'everyday',
                'begin':    '00:00',
                'end':      '21:00',
            })
        ])

        slots = GateSlot.from_timetable(
            timetable,
            datetime(2020, 7, 1, 0, 0, 0),
            datetime(2020, 7, 3, 0, 0, 0),
            store_id=uuid(),
            gate_id=uuid(),
        )

        tap.eq(len(slots), 2, 'Слоты созданы')

        with slots[0] as slot:
            tap.note('Слот 0')
            tap.eq(slot.begin, datetime(2020, 7, 1, 21, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 2, 0, 0, 0), 'конец')

        with slots[1] as slot:
            tap.note('Слот 1')
            tap.eq(slot.begin, datetime(2020, 7, 2, 21, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 3, 0, 0, 0), 'конец')


async def test_end(tap, uuid):
    with tap.plan(5, 'конец работы до 00:00'):

        timetable = TimeTable([
            TimeTableItem({
                'type':     'everyday',
                'begin':    '09:00',
                'end':      '00:00',
            })
        ])

        slots = GateSlot.from_timetable(
            timetable,
            datetime(2020, 7, 1, 0, 0, 0),
            datetime(2020, 7, 3, 0, 0, 0),
            store_id=uuid(),
            gate_id=uuid(),
        )

        tap.eq(len(slots), 2, 'Слоты созданы')

        with slots[0] as slot:
            tap.note('Слот 0')
            tap.eq(slot.begin, datetime(2020, 7, 1, 0, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 1, 9, 0, 0), 'конец')

        with slots[1] as slot:
            tap.note('Слот 1')
            tap.eq(slot.begin, datetime(2020, 7, 2, 0, 0, 0), 'начало')
            tap.eq(slot.end,   datetime(2020, 7, 2, 9, 0, 0), 'конец')
