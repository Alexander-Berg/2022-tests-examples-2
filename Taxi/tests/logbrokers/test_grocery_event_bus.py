import datetime

import pytest

import tests.dataset as dt
from libstall.util import time2time
from stall.logbroker import LogbrokerMessage
from stall.logbrokers.constants import DEFAULT_EVENT_LAG
from stall.logbrokers.constants import DEFAULT_PAUSE_DURATION
from stall.logbrokers.grocery_event_bus import Daemon
from stall.model.event_cache import EventCache


async def test_unknown_courier(tap, dataset: dt, now, uuid):
    with tap.plan(1, 'Невалидный курьер'):
        store = await dataset.store()

        message = LogbrokerMessage(
            'grocery-performer-return-depot',
            data={
                'depot_id': store.external_id,
                'performer_id': uuid(),
                'timestamp': now()
            }
        )

        await Daemon.process_messages([message])
        tap.ok(True, 'Сообщение пропущено')


async def test_return_depot(tap, dataset: dt, now):
    with tap.plan(3, 'Первый чекин'):
        store = await dataset.store()
        courier = await dataset.courier()

        first_checkin = now()
        message = LogbrokerMessage(
            'grocery-performer-return-depot',
            data={
                'depot_id': store.external_id,
                'performer_id': courier.external_id,
                'timestamp': first_checkin
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.checkin_time, time2time(first_checkin),
               'Время чекина')
        tap.eq(courier.state.checkin_store_id, store.store_id, 'Лавка чекина')


async def test_shift_open_as_checkin(tap, dataset: dt, now, uuid):
    with tap.plan(3, 'Открытие смены аналогично чекину'):
        store = await dataset.store()
        courier = await dataset.courier()
        shift_id = uuid()

        shift_open = now()
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'depot_id': store.external_id,
                'shift_id': shift_id,
                'status': 'open',
                'timestamp': shift_open
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.checkin_time, time2time(shift_open),
               'Время чекина')
        tap.eq(courier.state.checkin_store_id, store.store_id, 'Лавка чекина')


async def test_return_depot_ignore(tap, dataset: dt, now):
    with tap.plan(3, 'Игнорируем чекин пришедший позже, предыдущего события'):
        store = await dataset.store()
        checkin_time = time2time(now())
        courier = await dataset.courier(
            state = {
                'checkin_time': checkin_time,
                'checkin_store_id': store.store_id,
            }
        )

        second_store = await dataset.store()
        second_checkin = now() - datetime.timedelta(hours=2)

        message = LogbrokerMessage(
            'grocery-performer-return-depot',
            data={
                'depot_id': second_store.external_id,
                'performer_id': courier.external_id,
                'timestamp': second_checkin
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.checkin_time, time2time(checkin_time),
               'Время чекина не изменилось')
        tap.eq(courier.state.checkin_store_id, store.store_id,
               'Лавка чекина не изменилась')


async def test_process_return_depot(tap, dataset: dt, now):
    with tap.plan(3, 'Новый чекин перезаписывает данные'):
        store = await dataset.store()
        courier = await dataset.courier(
            state = {
                'checkin_time': time2time(now()),
                'checkin_store_id': store.store_id,
            }
        )

        second_store = await dataset.store()
        second_checkin = now() + datetime.timedelta(hours=2)
        message = LogbrokerMessage(
            'grocery-performer-return-depot',
            data={
                'depot_id': second_store.external_id,
                'performer_id': courier.external_id,
                'timestamp': second_checkin
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.checkin_time, time2time(second_checkin),
               'Время чекина изменилось')
        tap.eq(courier.state.checkin_store_id, second_store.store_id,
               'Лавка чекина изменилась')


async def test_shift_update(tap, dataset: dt, now, uuid):
    with tap.plan(3, 'Первое изменение статуса смены'):
        courier = await dataset.courier()
        shift_id = uuid()

        first_update = now()
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'open',
                'timestamp': first_update
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status, 'open',
               'Статус смены изменен')
        tap.eq(courier.state.grocery_shift_status_time, time2time(first_update),
               'Время изменения сохранено')


async def test_shift_update_ignore(tap, dataset: dt, now, uuid):
    with tap.plan(3, 'Игнорируем опоздавшее событие, если есть новее'):
        shift_id = uuid()
        grocery_shift_status_time = time2time(now())
        courier = await dataset.courier(
            state = {
                'grocery_shift_status': 'open',
                'grocery_shift_status_time': grocery_shift_status_time,
                'open_shifts': {
                    shift_id: {
                        'grocery_shift_id': shift_id,
                        'grocery_shift_status': 'open',
                        'grocery_shift_time': grocery_shift_status_time,
                    }
                },
            }

        )

        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'close',
                'timestamp': now() - datetime.timedelta(hours=2)
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status, 'open',
               'Статус смены не изменен')
        tap.eq(courier.state.grocery_shift_status_time,
               grocery_shift_status_time,
               'Время изменения не изменилось')


async def test_shift_update_error(tap, dataset: dt, now, uuid):
    with tap.plan(2, 'Плохое сообщение нужно игнорировать'):
        shift_id = uuid()
        courier = await dataset.courier()

        good_message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'open',
                'timestamp': now()
            }
        )
        bad_message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'wrong status',
                'timestamp': now() + datetime.timedelta(hours=1)
            }
        )
        await Daemon.process_messages([good_message, bad_message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status,
               'open', 'Статус смены изменен')


async def test_shift_update_new(tap, dataset: dt, now, uuid):
    with tap.plan(3, 'Новое событие перезаписыает данные'):
        shift_id = uuid()
        grocery_shift_status_time = time2time(now())
        courier = await dataset.courier(
            state ={
                'grocery_shift_status': 'open',
                'grocery_shift_status_time': grocery_shift_status_time,
                'open_shifts': {
                    shift_id: {
                        'grocery_shift_id': shift_id,
                        'grocery_shift_status': 'open',
                        'grocery_shift_time': grocery_shift_status_time,
                    }
                },
            }
        )

        second_update = now() + datetime.timedelta(hours=2)
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'close',
                'timestamp': second_update
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status,
               'close', 'Статус смены изменен')
        tap.eq(courier.state.grocery_shift_status_time,
               time2time(second_update),
               'Время изменения поменялось')


async def test_close_after_checkin(tap, dataset: dt, now, uuid):
    # Сообщения из разных топиков могут приходить в разном порядке
    # Проверим, что сообщение close обрабатываются верно
    with tap.plan(5, 'Статус запоздавший close после чекина не обнуляет лавку'):
        shift_id = uuid()
        store = await dataset.store()
        checkin_time = time2time(now())
        courier = await dataset.courier(
            state = {
                'checkin_time': checkin_time,
                'checkin_store_id': store.store_id,
            }
        )

        missed_update = now() - datetime.timedelta(hours=1)
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'close',
                'timestamp': missed_update
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status,
               'close', 'Статус смены изменен')
        tap.eq(courier.state.grocery_shift_status_time,
               time2time(missed_update),
               'Время изменения поменялось')
        tap.eq(courier.state.checkin_time, checkin_time,
               'Время чекина не изменилось')
        tap.eq(courier.state.checkin_store_id, store.store_id,
               'Лавка чекина не изменилась')


@pytest.mark.parametrize('checkin_delta,close_delta', [
    (
        datetime.timedelta(seconds=0),
        datetime.timedelta(seconds=DEFAULT_EVENT_LAG.total_seconds() // 2),
    ),
    (
        datetime.timedelta(seconds=0),
        datetime.timedelta(seconds=-DEFAULT_EVENT_LAG.total_seconds() // 2),
    ),
])
async def test_shift_close_clean_checkin(tap, dataset: dt, now, uuid,
                                         checkin_delta, close_delta):
    # Сообщения из разных топиков могут приходить в разном порядке
    # Проверим, что сообщение close обрабатываются верно
    with tap.plan(5, 'Статус close после чекина обнуляет лавку'):
        shift_id = uuid()
        _now = time2time(now())
        store = await dataset.store()
        courier = await dataset.courier(
            state={
                'checkin_time': _now + checkin_delta,
                'checkin_store_id': store.store_id,
            }
        )

        close_update_time = _now + close_delta
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'close',
                'timestamp': close_update_time
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status,
               'close', 'Статус смены изменен')
        tap.eq(
            courier.state.grocery_shift_status_time,
            time2time(close_update_time),
            'Время изменения поменялось'
        )
        tap.eq(courier.state.checkin_time, None, 'Время чекина обнулилось')
        tap.eq(courier.state.checkin_store_id, None, 'Лавка чекина обнулилась')


@pytest.mark.parametrize('checkin_delta', [
    datetime.timedelta(seconds=-60),
    datetime.timedelta(seconds=DEFAULT_EVENT_LAG.total_seconds() // 2),
])
async def test_ignore_checkin_after_close(tap, dataset: dt, now,
                                          checkin_delta):
    # Сообщения из разных топиков могут приходить в разном порядке
    # Проверим, что сообщение close обрабатываются верно
    with tap.plan(
            3,
            'Пропустим чекин, который пришел чуть позже закрытия смены'
    ):
        store = await dataset.store()
        close_time = time2time(now())
        courier = await dataset.courier(
            state = {
                'grocery_shift_status': 'close',
                'grocery_shift_status_time': close_time,
                'open_shifts': {},
            }

        )
        checkin_time = close_time + checkin_delta
        message = LogbrokerMessage(
            'grocery-performer-return-depot',
            data={
                'depot_id': store.external_id,
                'performer_id': courier.external_id,
                'timestamp': checkin_time
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.checkin_time, None,
               'Время чекина так же пустое')
        tap.eq(courier.state.checkin_store_id,
               None, 'Лавка чекина так же пустая')


async def test_events_shift_update(tap, dataset: dt, now, uuid):
    with tap.plan(6, 'Открытие смены отправляет событие'):
        shift_id = uuid()
        store = await dataset.store()
        courier = await dataset.courier()

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        existed_events = len(cursor.list)
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'depot_id': store.external_id,
                'shift_id': shift_id,
                'status': 'open',
                'timestamp': now()
            }
        )
        await Daemon.process_messages([message])

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        tap.eq(len(cursor.list), existed_events + 1, 'Новый контейнер событий')
        with cursor.list[0] as wrapper:
            tap.eq(len(wrapper.events), 1, '1 событие в контейнере')
            event = wrapper.events[0]

            tap.eq(event['key'], ['courier', 'store', store.store_id],
                   'key')
            tap.eq(event['data']['courier_id'], courier.courier_id,
                   'data.courier_id')
            tap.eq(event['data']['store_id'], store.store_id,
                   'data.store_id')
            tap.ok('state' in event['data'],
                   'data.state')


async def test_events_checkin(tap, dataset: dt, now):
    with tap.plan(6, 'Чекин отправляет событие'):
        store = await dataset.store()
        courier = await dataset.courier()

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        existed_events = len(cursor.list)
        message = LogbrokerMessage(
            'grocery-performer-return-depot',
            data={
                'depot_id': store.external_id,
                'performer_id': courier.external_id,
                'timestamp': now() + datetime.timedelta(hours=1)
            }
        )
        await Daemon.process_messages([message])

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        tap.eq(len(cursor.list), existed_events + 1, 'Новый контейнер событий')
        with cursor.list[0] as wrapper:
            tap.eq(len(wrapper.events), 1, '1 событие в контейнере')
            event = wrapper.events[0]

            tap.eq(event['key'], ['courier', 'store', store.store_id],
                   'key')
            tap.eq(event['data']['courier_id'], courier.courier_id,
                   'data.courier_id')
            tap.eq(event['data']['store_id'], store.store_id,
                   'data.store_id')
            tap.ok('state' in event['data'],
                   'data.state')


async def test_events_checkin_shift(tap, dataset: dt, now, uuid):
    with tap.plan(5, 'Установка статуса смены после чекина отправляет событие'):
        shift_id = uuid()
        store = await dataset.store()
        courier = await dataset.courier(
            state={
                'checkin_time': now(),
                'checkin_store_id': store.store_id,
            }
        )

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        existed_events = len(cursor.list)
        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'open',
                'timestamp': now() + datetime.timedelta(hours=2)
            }
        )
        await Daemon.process_messages([message])

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', courier.courier_id),
            ),
            db={'shard': courier.shardno},
            direction='DESC',
        )
        tap.eq(len(cursor.list), existed_events + 1, 'Новый контейнер событий')
        with cursor.list[0] as wrapper:
            tap.eq(len(wrapper.events), 1, '1 событие в контейнере')
            event = wrapper.events[0]

            tap.eq(event['key'], ['courier', 'store', store.store_id], 'key')
            tap.eq(event['data']['courier_id'], courier.courier_id,
                    'data.courier_id')
            tap.eq(event['data']['store_id'], store.store_id, 'data.store_id')


async def test_process_unpause(tap, dataset: dt, now, uuid):
    with tap.plan(3, 'Переход из pause в unpause'):
        shift_id = uuid()
        pause_time = now()
        courier = await dataset.courier(
            state={
                'grocery_shift_status': 'pause',
                'grocery_shift_status_time': time2time(pause_time),
                'open_shifts': {
                    shift_id: {
                        'grocery_shift_id': shift_id,
                        'grocery_shift_status': 'pause',
                        'grocery_shift_time': time2time(pause_time),
                    }
                },
            }
        )

        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'unpause',
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status,
               'unpause', 'Статус смены изменен')
        tap.eq(courier.state.grocery_shift_status_time,
               time2time(pause_time) + DEFAULT_PAUSE_DURATION,
               'Время изменения не поменялось')


@pytest.mark.parametrize('begin_status', [
    'open',
    'close',
    'unpause'
])
async def test_process_unpause_ignore(
        tap, dataset: dt, now, uuid, begin_status
):
    with tap.plan(3, f'Переход из {begin_status} в unpause игнорируется'):
        shift_id = uuid()
        pause_time = now()
        courier = await dataset.courier(
            state = {
                'grocery_shift_status': begin_status,
                'grocery_shift_status_time': time2time(pause_time),
                'open_shifts': {
                    shift_id: {
                        'grocery_shift_id': shift_id,
                        'grocery_shift_status': begin_status,
                        'grocery_shift_time': time2time(pause_time),
                    }
                },
            }
        )

        message = LogbrokerMessage(
            'grocery-performer-shift-update',
            data={
                'performer_id': courier.external_id,
                'shift_id': shift_id,
                'status': 'unpause',
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.grocery_shift_status, begin_status,
               'Статус смены не поменялся')
        tap.eq(courier.state.grocery_shift_status_time, time2time(pause_time),
               'Время изменения не поменялось')


async def test_open_close_order(tap, dataset: dt, now, uuid):
    # pylint: disable=too-many-statements, too-many-locals
    with tap.plan(4, 'Новая смена открылась, потом старая смена закрылась'):
        store = await dataset.store()
        first_shift_id = uuid()
        first_open_time = time2time(now() + datetime.timedelta(hours=-2))
        first_close_time = time2time(now() + datetime.timedelta(minutes=3))
        second_shift_id = uuid()
        second_open_time = time2time(now() + datetime.timedelta(minutes=2))
        second_close_time = time2time(now() + datetime.timedelta(hours=2))
        courier = await dataset.courier()

        with tap.subtest(9, 'Открыли первую смену') as taps:
            message = LogbrokerMessage(
                'grocery-performer-shift-update',
                data={
                    'timestamp': first_open_time,
                    'shift_id': first_shift_id,
                    'performer_id': courier.external_id,
                    'status': 'open',
                    'depot_id': store.external_id,
                }
            )
            await Daemon.process_messages([message])

            taps.ok(await courier.reload(), 'Перегружен')
            taps.eq(len(courier.state.open_shifts), 1, '1 открытая смена')
            with courier.state.open_shifts.get(first_shift_id) as shift:
                taps.eq(
                    shift.grocery_shift_id,
                    first_shift_id,
                    'state.first.shift_id'
                )
                taps.eq(
                    shift.grocery_shift_status,
                    'open',
                    'state.first.shift_status'
                )
                taps.eq(
                    shift.grocery_shift_time,
                    first_open_time,
                    'state.first.shift_time'
                )
            with courier.state as state:
                taps.eq(
                    state.checkin_store_id, store.store_id, 'checkin_store_id'
                )
                taps.eq(
                    state.checkin_time, first_open_time, 'checkin_time'
                )
                taps.eq(
                    state.grocery_shift_status, 'open', 'grocery_shift_status'
                )
                taps.eq(
                    state.grocery_shift_status_time,
                    first_open_time,
                    'grocery_shift_status_time'
                )

        with tap.subtest(12, 'Открыли вторую смену') as taps:
            message = LogbrokerMessage(
                'grocery-performer-shift-update',
                data={
                    'timestamp': second_open_time,
                    'shift_id': second_shift_id,
                    'performer_id': courier.external_id,
                    'status': 'open',
                    'depot_id': store.external_id,
                }
            )
            await Daemon.process_messages([message])

            taps.ok(await courier.reload(), 'Перегружен')
            taps.eq(len(courier.state.open_shifts), 2, '1 открытая смена')
            with courier.state.open_shifts.get(first_shift_id) as shift:
                taps.eq(
                    shift.grocery_shift_id,
                    first_shift_id,
                    'state.first.shift_id'
                )
                taps.eq(
                    shift.grocery_shift_status,
                    'open',
                    'state.first.shift_status'
                )
                taps.eq(
                    shift.grocery_shift_time,
                    first_open_time,
                    'state.first.shift_time'
                )
            with courier.state.open_shifts.get(second_shift_id) as shift:
                taps.eq(
                    shift.grocery_shift_id,
                    second_shift_id,
                    'state.second.shift_id'
                )
                taps.eq(
                    shift.grocery_shift_status,
                    'open',
                    'state.second.shift_status'
                )
                taps.eq(
                    shift.grocery_shift_time,
                    second_open_time,
                    'state.second.shift_time'
                )

            with courier.state as state:
                taps.eq(
                    state.checkin_store_id, store.store_id, 'checkin_store_id'
                )
                taps.eq(
                    state.checkin_time, second_open_time, 'checkin_time'
                )
                taps.eq(
                    state.grocery_shift_status, 'open', 'grocery_shift_status'
                )
                taps.eq(
                    state.grocery_shift_status_time,
                    second_open_time,
                    'grocery_shift_status_time'
                )

        with tap.subtest(10, 'Закрыли первую смену') as taps:
            message = LogbrokerMessage(
                'grocery-performer-shift-update',
                data={
                    'timestamp': first_close_time,
                    'shift_id': first_shift_id,
                    'performer_id': courier.external_id,
                    'status': 'close',
                }
            )
            await Daemon.process_messages([message])

            taps.ok(await courier.reload(), 'Перегружен')
            print('\n\n',courier.state.open_shifts, '\n\n')
            taps.eq(len(courier.state.open_shifts), 1, '1 открытая смена')
            taps.not_in_ok(
                first_shift_id,
                courier.state.open_shifts,
                'Первой смены больше нет'
            )
            with courier.state.open_shifts.get(second_shift_id) as shift:
                taps.eq(
                    shift.grocery_shift_id,
                    second_shift_id,
                    'state.second.shift_id'
                )
                taps.eq(
                    shift.grocery_shift_status,
                    'open',
                    'state.second.shift_status'
                )
                taps.eq(
                    shift.grocery_shift_time,
                    second_open_time,
                    'state.second.shift_time'
                )
            with courier.state as state:
                taps.eq(
                    state.checkin_store_id, store.store_id, 'checkin_store_id'
                )
                taps.eq(
                    state.checkin_time, second_open_time, 'checkin_time'
                )
                taps.eq(
                    state.grocery_shift_status, 'open', 'grocery_shift_status'
                )
                taps.eq(
                    state.grocery_shift_status_time,
                    second_open_time,
                    'grocery_shift_status_time'
                )

        with tap.subtest(8, 'Закрыли вторую смену') as taps:
            message = LogbrokerMessage(
                'grocery-performer-shift-update',
                data={
                    'timestamp': second_close_time,
                    'shift_id': second_shift_id,
                    'performer_id': courier.external_id,
                    'status': 'close',
                }
            )
            await Daemon.process_messages([message])

            taps.ok(await courier.reload(), 'Перегружен')
            taps.eq(len(courier.state.open_shifts), 0, '1 открытая смена')
            taps.not_in_ok(
                first_shift_id,
                courier.state.open_shifts,
                'Первой смены больше нет'
            )
            taps.not_in_ok(
                second_shift_id,
                courier.state.open_shifts,
                'Второй смены больше нет'
            )

            with courier.state as state:
                taps.eq(state.checkin_store_id, None, 'checkin_store_id')
                taps.eq(state.checkin_time, None, 'checkin_time')
                taps.eq(
                    state.grocery_shift_status,
                    'close',
                    'grocery_shift_status'
                )
                taps.eq(
                    state.grocery_shift_status_time,
                    second_close_time,
                    'grocery_shift_status_time'
                )
