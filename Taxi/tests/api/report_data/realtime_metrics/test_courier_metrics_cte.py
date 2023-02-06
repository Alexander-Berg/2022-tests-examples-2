import datetime
import pytest
from libstall.util import time2time

@pytest.mark.parametrize(
    'order_type,delivery_type',
    (
        ('dispatch', 'courier'),
        ('dispatch', None),
    )
)
async def test_cte(api, tap, now, dataset, tzone, time_mock,
                   clickhouse_client,
                   order_type, delivery_type):
    # pylint: disable=unused-argument, too-many-arguments
    with tap.plan(4, 'Полный CTE от подтвержден до статуса "Прибыл к клиенту"'):
        _now = now()
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
            delivery_type=order_type
        )

        await dataset.ch_grocery_order_assemble_ready(
            timestamp=_now + datetime.timedelta(minutes=2),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type=delivery_type
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=13),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=_now + datetime.timedelta(minutes=15),
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
        tap.note('grocery_delivering_arrived - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', 660)


async def test_cte_miss_arrived_event(api, tap, now, dataset, tzone, time_mock,
                                      clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Статуса "Прибыл к клиенту" может не быть. '
                     'Тогда используем "Доставлен"'):
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

        await dataset.ch_grocery_order_assemble_ready(
            timestamp=_now + datetime.timedelta(minutes=2),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=_now + datetime.timedelta(minutes=15),
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

        tap.note('grocery_order_delivered - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', 780)


@pytest.mark.parametrize(
    'skip_event',
    (
        'order_created',
        'order_assemble_ready',
        'order_matched',
        # 'delivering_arrived', Его может не быть
        'order_delivered',
    )
)
async def test_cte_skip_events(api, tap, now, dataset, tzone, time_mock,
                               clickhouse_client, skip_event):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Для расчета CTE важны все события'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        if skip_event != 'order_created':
            await dataset.ch_grocery_order_created(
                timestamp=_now + datetime.timedelta(minutes=0),
                order=order,
                store=store,
                delivery_type='dispatch'
            )
        if skip_event != 'order_assemble_ready':
            await dataset.ch_grocery_order_assemble_ready(
                timestamp=_now + datetime.timedelta(minutes=2),
                order=order,
                store=store,
            )
        if skip_event != 'order_matched':
            await dataset.ch_grocery_order_matched(
                timestamp=_now + datetime.timedelta(minutes=5),
                order=order,
                store=store,
                delivery_type='courier'
            )
        if skip_event != 'delivering_arrived':
            await dataset.ch_grocery_delivering_arrived(
                timestamp=_now + datetime.timedelta(minutes=13),
                order=order,
                store=store,
            )
        if skip_event != 'order_delivered':
            await dataset.ch_grocery_order_delivered(
                timestamp=_now + datetime.timedelta(minutes=15),
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
        t.json_is('metrics.full_cte', None)


async def test_cte_last_match(api, tap, now, dataset, tzone, time_mock,
                              clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Последний назначенный курьер должен быть лавочным'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

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
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=_now + datetime.timedelta(minutes=2),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=4),
            order=order,
            store=store,
            delivery_type='yandex_taxi'
        )
        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            delivery_type='courier'
        )
        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=10),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_delivered(
            timestamp=_now + datetime.timedelta(minutes=15),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_delivering_arrived - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', (10 - 2) * 60)


@pytest.mark.parametrize(
    'order_type,delivery_type',
    (
        ('dispatch', 'yandex_taxi'),
        ('pickup', 'courier'),
        ('rover', 'courier'),
    )
)
async def test_cte_invalid_delivery(api, tap, now, dataset, tzone, time_mock,
                                    clickhouse_client,
                                    order_type, delivery_type):
    # pylint: disable=unused-argument, too-many-arguments
    with tap.plan(4, 'Полный CTE от создания до статуса "Доставлен"'):
        store = await dataset.store(tz='UTC')
        order = await dataset.order(store=store)
        user = await dataset.user(role='admin', store=store)

        today = now(tz=tzone(store.tz)).date()
        _now = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )
        time_mock.set(_now + datetime.timedelta(hours=1))

        await dataset.ch_grocery_order_created(
            timestamp=_now + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type=order_type
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=_now + datetime.timedelta(minutes=2),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=_now + datetime.timedelta(minutes=4),
            order=order,
            store=store,
            delivery_type=delivery_type
        )
        await dataset.ch_grocery_delivering_arrived(
            timestamp=_now + datetime.timedelta(minutes=10),
            order=order,
            store=store,
        )
        await dataset.ch_grocery_order_delivered(
            timestamp=_now + datetime.timedelta(minutes=15),
            order=order,
            store=store,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_report_data_realtime_metrics_courier_metrics',
            json={
                'store_id': store.store_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.note('grocery_delivering_arrived - grocery_order_assemble_ready')
        t.json_is('metrics.full_cte', None)
