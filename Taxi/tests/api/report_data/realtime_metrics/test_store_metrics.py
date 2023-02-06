import datetime
import pytest
from libstall.util import time2time
from libstall.timetable import TimeTable, TimeTableItem
from stall.api.report_data.realtime_metrics.store_metrics import (
    store_time_range,
    shift_of_start_day,
)
from stall.client.clickhouse import grocery_clickhouse_pool


async def test_empty(api, tap, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(6, 'Нет заказов, всё по нулям'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(role='admin', store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.orders_count', 0)
        t.json_is('metrics.assemble_time', None)
        t.json_is('metrics.assemble_wait_time', None)


async def test_only_created(api, tap, now, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(6, 'Заказу недостаточно быть созданным'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(role='admin', store=store)

        await dataset.ch_grocery_order_created(
            timestamp=now(),
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.orders_count', 0)
        t.json_is('metrics.assemble_time', None)
        t.json_is('metrics.assemble_wait_time', None)


async def test_orders_count(api, tap, now, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Метрика: Всего заказов'):
        _now = now()
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_assemble_ready(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.orders_count', 1)


async def test_assemble_time(api, tap, now, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Метрика: Всего заказов'):
        _now = now()
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
        )

        await dataset.ch_wms_order_processing(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
        )

        await dataset.ch_wms_order_complete(
            timestamp=_now + datetime.timedelta(minutes=11),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.assemble_time', 360)

async def test_assemble_wait_time(api, tap, now, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Метрика: Всего заказов'):
        _now = now()
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_assemble_ready(
            timestamp=_now + datetime.timedelta(minutes=1),
            order=order,
            store=store,
        )

        await dataset.ch_wms_order_processing(
            timestamp=_now + datetime.timedelta(minutes=4),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.assemble_wait_time', 180)


async def test_store_time_range(tap):
    with tap.plan(3, ''):
        start, end = store_time_range(
            datetime.date(2022, 1, 1),
            'Asia/Omsk', # UTC+06:00
            )
        tap.eq(start.tzname(), 'UTC', 'timezone name')
        tap.eq(start.isoformat(), '2021-12-31T18:00:00+00:00', 'Время начала')
        tap.eq(end.isoformat(), '2022-01-01T18:00:00+00:00', 'Время окончания')


@pytest.mark.parametrize(
    'note, table_items, expected',
    (
        (
            'From 00:00 to 00:00 - day begin is 00:00',
            [
                TimeTableItem(type='everyday', begin='00:00', end='00:00')
            ],
            datetime.timedelta(hours=0)
        ),
        (
            'No midnight. From 07:00 to 23:00 - day begin is 00:00',
            [
                TimeTableItem(type='everyday', begin='07:00', end='00:00')
            ],
            datetime.timedelta(hours=0)
        ),
        (
            'From 07:00 to 01:00 - day begin is 01:00',
            [
                TimeTableItem(type='everyday', begin='07:00', end='01:00')
            ],
            datetime.timedelta(hours=1)
        ),
        (
            'Skip all timetables except \'everyday\'',
            [
                TimeTableItem(type='holiday', begin='07:00', end='01:00')
            ],
            datetime.timedelta(hours=0)
        ),
        (
            'Skip holiday. From 07:00 to 02:00 - day begin is 02:00',
            [
                TimeTableItem(type='holiday', begin='07:00', end='01:00'),
                TimeTableItem(type='everyday', begin='07:00', end='02:00')

            ],
            datetime.timedelta(hours=2)
        ),
        (
            'Midnight has priority. From 07:00 to 03:00 - day begin is 03:00',
            [
                TimeTableItem(type='everyday', begin='03:00', end='04:00'),
                TimeTableItem(type='everyday', begin='07:00', end='03:00')

            ],
            datetime.timedelta(hours=3)
        ),
    )
)
async def test_shift_of_start_day(tap, dataset, note, table_items,
                                        expected):
    store = await dataset.store(
        timetable=TimeTable(table_items)
    )
    result = shift_of_start_day(store)
    tap.eq(result, expected, note)


@pytest.mark.parametrize(
    'note,tz,created_delta,delivered_delta,expected',
    (
        (
            '+06:00 Заказ создан и собран "завтра"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=19, minutes=0),
            datetime.timedelta(hours=19, minutes=5),
            None,
        ),
        (
            '+03:00 Заказ создан и собран "сегодня"',
            'Europe/Moscow', # UTC+03:00
            datetime.timedelta(hours=19, minutes=0),
            datetime.timedelta(hours=19, minutes=5),
            300, # 5 минут
        ),
        (
            'Заказ создан "вчера" и собран "сегодня"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=-7, minutes=0),
            datetime.timedelta(hours=-5, minutes=55),
            None,
        ),
        (
            'Заказ создан и собран "сегодня"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=-6, minutes=5),
            datetime.timedelta(hours=-6, minutes=15),
            600, # 10 минут
        ),
        (
            'Заказ создан "сегодня" и собран "завтра"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=17, minutes=55),
            datetime.timedelta(hours=18, minutes=15),
            1200, # 20 минут
        ),
    )
)
async def test_timezone(api, tap, now, tzone, dataset,
                        clickhouse_client, note, tz,
                        created_delta, delivered_delta, expected):
    # pylint: disable=unused-argument,too-many-arguments,too-many-locals
    with tap.plan(4, 'По умолчанию, данные за сегодня с учетом таймзоны'):
        store = await dataset.store(tz=tz)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())

        tap.note(note)
        tap.note(f'Дата: {today}')

        created = today_at_0 + created_delta
        tap.note(f'Заказ создан: {time2time(created, tz=store.tz)}')
        await dataset.ch_grocery_order_created(
            timestamp=created,
            order=order,
            store=store,
        )
        await dataset.ch_wms_order_processing(
            timestamp=created,
            order=order,
            store=store,
        )

        delivered = today_at_0 + delivered_delta
        tap.note(f'Заказа собран: {time2time(delivered, tz=store.tz)}')
        await dataset.ch_wms_order_complete(
            timestamp=delivered,
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.assemble_time', expected)


@pytest.mark.parametrize(
    'note,created_delta,delivered_delta,expected',
    (
        (
            '"Завтра" - 2 = "сегодня". '
            'Заказ создан "сегодня" и собран "сегодня"',
            datetime.timedelta(hours=19, minutes=0),
            datetime.timedelta(hours=19, minutes=5),
            300,
        ),
        (
            '"Сегодня" - 2 = "вчера". '
            'Заказ создан "вчера" и собран "вчера"',
            datetime.timedelta(hours=-6, minutes=5),
            datetime.timedelta(hours=-6, minutes=15),
            None,
        ),
        (
            'Заказ создан "сегодня" и доставлен "сегодня"',
            datetime.timedelta(hours=-4, minutes=5),
            datetime.timedelta(hours=-4, minutes=15),
            600, # 10 минут
        ),
    )
)
async def test_midnight_timetable(api, tap, now, tzone, dataset,
                                  clickhouse_client, note,
                                  created_delta, delivered_delta, expected):
    # pylint: disable=unused-argument,too-many-arguments,too-many-locals
    with tap.plan(
        4,
        'Ночной интеравал до 02:00 сдвигает границы суток как таймзона -02:00'
    ):
        store = await dataset.store(
            tz='Asia/Omsk', # UTC+06:00
            timetable=TimeTable([
                TimeTableItem({
                    'type': 'everyday',
                    'begin': '07:00',
                    'end': '02:00'
                })
            ])
        )
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())

        tap.note(note)
        tap.note(f'Дата: {today}')

        created = today_at_0 + created_delta
        tap.note('Лавка работает до 02:00')
        tap.note(f'Заказ создан: {time2time(created, tz=store.tz)}')
        await dataset.ch_grocery_order_created(
            timestamp=created,
            order=order,
            store=store,
        )
        await dataset.ch_wms_order_processing(
            timestamp=created,
            order=order,
            store=store,
        )

        delivered = today_at_0 + delivered_delta
        tap.note(f'Заказа собран: {time2time(delivered, tz=store.tz)}')
        await dataset.ch_wms_order_complete(
            timestamp=delivered,
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.assemble_time', expected)


async def test_with_date(api, tap, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Данные на конкретный день'):
        store = await dataset.store(tz='Asia/Omsk') # UTC+06:00
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        day = time2time('2021-01-12').date()
        day_at_0 = time2time(day.isoformat())

        await dataset.ch_grocery_order_created(
            timestamp=day_at_0 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_assemble_ready(
            timestamp=day_at_0 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_store_metrics',
            json={
                'store_id': store.store_id,
                'date': day.isoformat()
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.orders_count', 1)


async def test_fail_request(api, ext_api, tap, dataset, clickhouse_client):
    # pylint: disable=unused-argument,redefined-outer-name
    with tap.plan(3, 'Данные на конкретный день'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(role='admin', store=store)

        async def handler(response):
            return 503, {}

        async with await ext_api(grocery_clickhouse_pool.clients[0], handler):
            t = await api(user=user)
            await t.post_ok(
                'api_report_data_realtime_metrics_store_metrics',
                json={
                    'store_id': store.store_id,
                }
            )

            t.status_is(502, diag=True)
            t.json_is('code', 'ER_BAD_GATEWAY')
