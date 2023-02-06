import datetime
import pytest
from libstall.util import time2time
from libstall.timetable import TimeTable, TimeTableItem
from stall.api.report_data.realtime_metrics.courier_metrics import (
    store_time_range
)
from stall.client.clickhouse import grocery_clickhouse_pool


async def test_empty(api, tap, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(9, 'Нет заказов, всё по нулям'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(role='admin', store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('metrics.full_cte', None)
        t.json_is('metrics.waiting_for_pickup', None)
        t.json_is('metrics.lateness', None)
        t.json_is('metrics.lateness_5_min', None)
        t.json_is('metrics.oph', None)
        t.json_is('metrics.shift_time', None)


async def test_waiting_for_pickup(api, tap, now, dataset, tzone, time_mock,
                                  clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            4,
            'Время от окончания сборки заказа до того, как его забрал курьер'
    ):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch'
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )

        await dataset.ch_wms_order_complete(
            timestamp=_now + datetime.timedelta(minutes=13),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=_now + datetime.timedelta(minutes=17),
            order=order,
            store=store,
        )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_order_pickup - wms_order_complete(')
        t.json_is('metrics.waiting_for_pickup', 240)


async def test_lateness(api, tap, now, dataset, tzone, time_mock,
                        clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(5, 'Считаем опоздание по событию "Прибыл к клиенту"'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch',
            max_eta=20,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=26),
            order=order,
            store=store,
        )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('ch_grocery_delivering_arrived '
                 '- ch_grocery_order_created '
                 '- max_eta')
        t.json_is('metrics.lateness', 360)
        t.json_is('metrics.lateness_5_min', 100)


async def test_lateness_miss_arrived(api, tap, now, dataset, tzone, time_mock,
                                     clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
        5,
        'Считаем опоздание по событию "Заказ доставлен", если не было "Прибыл"'
    ):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch',
            max_eta=20,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )

        tap.note(
            'Если не было события "Прибыл к клиенту", '
            'то используем событие "Доставлено"'
        )
        await dataset.ch_grocery_order_delivered(
            timestamp=_now + datetime.timedelta(minutes=27),
            order=order,
            store=store,
        )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('ch_grocery_order_delivered '
                 '- ch_grocery_order_created '
                 '- max_eta')
        t.json_is('metrics.lateness', 420)
        t.json_is('metrics.lateness_5_min', 100)


async def test_lateness_and_intime(api, tap, now, dataset, tzone, time_mock,
                                   clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(5, 'Вовремя доставленные заказы учитываются как 0'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        order2 = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch',
            max_eta=20,
        )
        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order2,
            store=store,
            delivery_type='dispatch',
            max_eta=20,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )
        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order2,
            store=store,
            delivery_type='courier'
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=28),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=17),
            order=order2,
            store=store,
        )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('ch_grocery_delivering_arrived '
                 '- ch_grocery_order_created '
                 '- max_eta')
        t.json_is('metrics.lateness', 240)
        t.json_is('metrics.lateness_5_min', 50)


async def test_to_client_time(api, tap, now, dataset, tzone, time_mock,
                                  clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(
            4,
            'Время от момента, как курьер забрал заказ, до прибытия к клиенту'
    ):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch'
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=_now + datetime.timedelta(minutes=17),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=23),
            order=order,
            store=store,
        )

        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_delivering_arrived - grocery_order_pickup')
        t.json_is('metrics.to_client_time', 360)


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
    'note,tz,created_delta,delivered_delta,expected',
    (
        (
            '+06:00 Заказ создан и доставлен "завтра"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=19, minutes=0),
            datetime.timedelta(hours=19, minutes=5),
            None
        ),
        (
            '+03:00 Заказ создан и доставлен "сегодня"',
            'Europe/Moscow', # UTC+03:00
            datetime.timedelta(hours=19, minutes=0),
            datetime.timedelta(hours=19, minutes=5),
            300, # 5 минут
        ),
        (
            '+06:00 Заказ создан "вчера" и доставлен "сегодня"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=-7, minutes=0),
            datetime.timedelta(hours=-5, minutes=55),
            None
        ),
        (
            '+06:00 Заказ создан и доставлен "сегодня"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=-6, minutes=5),
            datetime.timedelta(hours=-6, minutes=15),
            600, # 10 минут
        ),
        (
            '+06:00 Заказ создан "сегодня" и доставлен "завтра"',
            'Asia/Omsk', # UTC+06:00
            datetime.timedelta(hours=17, minutes=55),
            datetime.timedelta(hours=18, minutes=15),
            1200, # 20 минут
        ),
    )
)
async def test_timezone(api, tap, now, tzone, dataset,
                        clickhouse_client, note, tz, time_mock,
                        created_delta, delivered_delta, expected):
    # pylint: disable=unused-argument,too-many-arguments,too-many-locals
    with tap.plan(4, 'По умолчанию, данные за сегодня с учетом таймзоны'):
        store = await dataset.store(tz=tz)
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        today = now(tz=tzone(store.tz)).date()
        today_at_0 = time2time(today.isoformat())
        time_mock.set(today_at_0 + datetime.timedelta(hours=48))

        tap.note(note)
        tap.note(f'Дата: {today}')

        created = today_at_0 + created_delta
        tap.note(f'Заказ создан: {time2time(created, tz=store.tz)}')
        await dataset.ch_grocery_order_created(
            timestamp=created,
            order=order,
            store=store,
            delivery_type='dispatch'
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=created,
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=created,
            order=order,
            store=store,
            delivery_type='courier'
        )

        delivered = today_at_0 + delivered_delta
        tap.note(f'Заказа доставлен: {time2time(delivered, tz=store.tz)}')
        await dataset.ch_grocery_delivering_arrived(
            timestamp=delivered,
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_delivered(
            timestamp=delivered,
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
                'date': today.isoformat(),
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_delivering_arrived - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', expected)


@pytest.mark.parametrize(
    'note,created_delta,delivered_delta,expected',
    (
        (
            '"Завтра" - 2 = "сегодня". '
            'Заказ создан "сегодня" и доставлен "сегодня"',
            datetime.timedelta(hours=19, minutes=0),
            datetime.timedelta(hours=19, minutes=5),
            300,
        ),
        (
            '"Сегодня" - 2 = "вчера". '
            'Заказ создан "вчера" и доставлен "вчера"',
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
async def test_midnight_timetable(api, tap, now, tzone, time_mock, dataset,
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
        time_mock.set(today_at_0 + datetime.timedelta(hours=48))

        tap.note(note)
        tap.note(f'Дата: {today}')

        created = today_at_0 + created_delta
        tap.note(f'Заказ создан: {time2time(created, tz=store.tz)}')
        await dataset.ch_grocery_order_created(
            timestamp=created,
            order=order,
            store=store,
            delivery_type='dispatch'
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=created,
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=created,
            order=order,
            store=store,
            delivery_type='courier'
        )

        delivered = today_at_0 + delivered_delta
        tap.note(f'Заказа доставлен: {time2time(delivered, tz=store.tz)}')
        await dataset.ch_grocery_delivering_arrived(
            timestamp=delivered,
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_delivered(
            timestamp=delivered,
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
                'date': today.isoformat(),
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_delivering_arrived - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', expected)


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
            timestamp=day_at_0 + datetime.timedelta(minutes=2),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=day_at_0 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )
        await dataset.ch_grocery_delivering_arrived(
            timestamp=day_at_0 + datetime.timedelta(minutes=10),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_delivered(
            timestamp=day_at_0 + datetime.timedelta(minutes=15),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
                'date': day.isoformat()
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_delivering_arrived - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', (10 - 2) * 60)


async def test_fail_request(api, ext_api, tap, dataset, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(3, 'Данные на конкретный день'):
        store = await dataset.store(tz='UTC')
        user = await dataset.user(role='admin', store=store)

        async def handler(response):
            return 503, {}

        async with await ext_api(grocery_clickhouse_pool.clients[0], handler):
            t = await api(user=user)
            await t.post_ok(
                'api_report_data_realtime_metrics_courier_metrics',
                json={
                    'store_id': store.store_id,
                }
            )

            t.status_is(502, diag=True)
            t.json_is('code', 'ER_BAD_GATEWAY')
