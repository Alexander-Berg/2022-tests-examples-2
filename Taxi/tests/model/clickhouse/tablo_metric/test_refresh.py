import datetime
from libstall.util import time2time
from stall.model.analytics.tablo_metrics import TabloMetric


async def test_empty(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(4, 'Метрики по стору'):
        store = await dataset.store()
        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await TabloMetric.refresh_metrics(
            stores=[store],
            now_time=today_at_12,
        )

        hour_metric = await TabloMetric.load(
            ['1h', 'store', store.store_id],
            by='conflict'
        )
        tap.ok(hour_metric.metrics, 'hour_metric.metrics')
        tap.eq(
            hour_metric.calculated, today_at_12, 'hour_metric.calculated'
        )

        day_metric = await TabloMetric.load(
            ['day', 'store', store.store_id],
            by='conflict'
        )
        tap.ok(day_metric.metrics, 'day_metric.metrics')
        tap.eq(day_metric.calculated, today_at_12, 'day_metric.calculated')


async def test_order_count(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(2, 'Метрики по стору'):
        store = await dataset.store()
        order_cur_hour = await dataset.order(store=store)
        order_cur_day = await dataset.order(store=store)
        order_priv_day = await dataset.order(store=store)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=-30),
            order=order_cur_hour,
            store=store,
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=today_at_12 + datetime.timedelta(minutes=-5),
            order=order_cur_hour,
            store=store,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(hours=-6),
            order=order_cur_day,
            store=store,
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=today_at_12 + datetime.timedelta(hours=-6, minutes=5),
            order=order_cur_day,
            store=store,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(hours=-18),
            order=order_priv_day,
            store=store,
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=today_at_12 + datetime.timedelta(hours=-18, minutes=5),
            order=order_priv_day,
            store=store,
        )

        await TabloMetric.refresh_metrics(
            stores=[store],
            now_time=today_at_12,
        )

        hour_metric = await TabloMetric.load(
            ['1h', 'store', store.store_id],
            by='conflict'
        )
        tap.eq(hour_metric.metrics.orders_count, 1, 'hour_metric.metrics')
        day_metric = await TabloMetric.load(
            ['day', 'store', store.store_id],
            by='conflict'
        )
        tap.eq(day_metric.metrics.orders_count, 2, 'day_metric.metrics')


async def test_pickup_count(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(2, 'Курьерская метрика тоже прорастает по стору'):
        store = await dataset.store()
        courier = await dataset.courier(store=store)
        order_cur_hour = await dataset.order(store=store)
        order_cur_day = await dataset.order(store=store)
        order_priv_day = await dataset.order(store=store)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=-30),
            order=order_cur_hour,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=-10),
            order=order_cur_hour,
            store=store,
            courier=courier,
            delivery_type='courier'
        )
        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=-5),
            order=order_cur_hour,
            store=store,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(hours=-6),
            order=order_cur_day,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(hours=-6, minutes=10),
            order=order_cur_day,
            store=store,
            courier=courier,
            delivery_type='courier'
        )
        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(hours=-6, minutes=5),
            order=order_cur_day,
            store=store,
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(hours=-18),
            order=order_priv_day,
            store=store,
        )
        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(hours=-18, minutes=10),
            order=order_priv_day,
            store=store,
            courier=courier,
            delivery_type='courier'
        )
        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(hours=-18, minutes=5),
            order=order_priv_day,
            store=store,
        )

        await TabloMetric.refresh_metrics(
            stores=[store],
            now_time=today_at_12,
        )

        hour_metric = await TabloMetric.load(
            ['1h', 'store', store.store_id],
            by='conflict'
        )
        tap.eq(hour_metric.metrics.pickup_count, 1, 'hour_metric.metrics')
        day_metric = await TabloMetric.load(
            ['day', 'store', store.store_id],
            by='conflict'
        )
        tap.eq(day_metric.metrics.pickup_count, 2, 'day_metric.metrics')


async def test_truncate_time(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument
    with tap.plan(2, 'Проверим, что метрики считаются на ровное время'):
        store = await dataset.store()
        order_fit_time = await dataset.order(store=store)
        order_late_time = await dataset.order(store=store)

        today = time2time(now(tz=tzone(store.tz)).date().isoformat())
        _now = (
            today + datetime.timedelta(hours=12, minutes=16, seconds=10)
        )

        # Попадает
        await dataset.ch_grocery_order_created(
            timestamp=(
                today + datetime.timedelta(hours=12, minutes=14, seconds=50)
            ),
            order=order_fit_time,
            store=store,
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=(
                today + datetime.timedelta(hours=12, minutes=17, seconds=50)
            ),
            order=order_fit_time,
            store=store,
        )

        # Не попадает
        await dataset.ch_grocery_order_created(
            timestamp=(
                today + datetime.timedelta(hours=12, minutes=15, seconds=10)
            ),
            order=order_late_time,
            store=store,
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=(
                today + datetime.timedelta(hours=12, minutes=17, seconds=50)
            ),
            order=order_late_time,
            store=store,
        )

        await TabloMetric.refresh_metrics(
            stores=[store],
            now_time=_now,
            period=5 * 60,
        )

        hour_metric = await TabloMetric.load(
            ['1h', 'store', store.store_id],
            by='conflict'
        )
        tap.eq(hour_metric.metrics.orders_count, 1, 'hour_metric.metrics')
        tap.eq(
            hour_metric.calculated,
            today + datetime.timedelta(hours=12, minutes=15, seconds=0),
            'hour_metric.calculated'
        )
