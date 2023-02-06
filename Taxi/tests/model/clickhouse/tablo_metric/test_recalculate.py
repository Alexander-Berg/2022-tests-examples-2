import datetime
from libstall.util import time2time
from stall.model.analytics.tablo_metrics import TabloMetric


async def test_empty(tap, dataset, uuid, now):
    with tap.plan(8, 'Прорастим пустые метрики'):
        _slice = uuid()
        _now = now().replace(microsecond=0)
        store = await dataset.store()

        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=_now,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            metrics={}
        ).save()

        await TabloMetric.recalculate(
            company_ids=[store.company_id],
            cluster_ids=[store.cluster_id],
        )

        supervisor_metric = await TabloMetric.load(
            [
                _slice,
                'supervisor',
                f'EMPTY:{store.company_id}:{store.cluster_id}',
            ],
            by='conflict'
        )
        tap.eq(supervisor_metric.metrics.orders_count, 0, 'supervisor')
        tap.eq(supervisor_metric.calculated, _now, 'supervisor - calculated')

        cluster_metric = await TabloMetric.load(
            [_slice, 'cluster', store.cluster_id],
            by='conflict'
        )
        tap.eq(cluster_metric.metrics.orders_count, 0, 'cluster')
        tap.eq(cluster_metric.calculated, _now, 'cluster - calculated')

        company_metric = await TabloMetric.load(
            [_slice, 'company', store.company_id],
            by='conflict'
        )
        tap.eq(company_metric.metrics.orders_count, 0, 'compnay')
        tap.eq(company_metric.calculated, _now, 'company - calculated')

        total_metric = await TabloMetric.load(
            [_slice, 'total', 'total'],
            by='conflict'
        )
        tap.eq(total_metric.metrics.orders_count, 0, 'total')
        tap.eq(total_metric.calculated, _now, 'total - calculated')


async def test_data(tap, dataset, uuid, now):
    with tap.plan(4, 'Прорастим метрики'):
        _slice = uuid()
        store = await dataset.store()

        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=now(),
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            metrics={
                'orders_count': 3
            }
        ).save()

        await TabloMetric.recalculate(
            company_ids=[store.company_id],
            cluster_ids=[store.cluster_id],
        )

        supervisor_metric = await TabloMetric.load(
            [
                _slice,
                'supervisor',
                f'EMPTY:{store.company_id}:{store.cluster_id}',
            ],
            by='conflict'
        )
        tap.eq(supervisor_metric.metrics.orders_count, 3, 'supervisor')
        cluster_metric = await TabloMetric.load(
            [_slice, 'cluster', store.cluster_id],
            by='conflict'
        )
        tap.eq(cluster_metric.metrics.orders_count, 3, 'cluster')

        company_metric = await TabloMetric.load(
            [_slice, 'company', store.company_id],
            by='conflict'
        )
        tap.eq(company_metric.metrics.orders_count, 3, 'company')
        total_metric = await TabloMetric.load(
            [_slice, 'total', 'total'],
            by='conflict'
        )
        tap.eq(total_metric.metrics.orders_count, 3, 'total')


async def test_all_metrics(tap, dataset, now, tzone, clickhouse_client):
    # pylint: disable=unused-argument, too-many-statements
    with tap.plan(40, 'Метрики по стору. Проверяем, что они вообще считаются'):
        store = await dataset.store()
        courier = await dataset.courier(store=store)
        shift = await dataset.courier_shift(courier=courier, store=store)
        order = await dataset.order(store=store)

        today = now(tz=tzone(store.tz)).date()
        today_at_12 = (
            time2time(today.isoformat()) + datetime.timedelta(hours=12)
        )

        await dataset.ch_grocery_shift_update(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            courier=courier,
            store=store,
            shift_id=shift.courier_shift_id,
            status='open',
        )

        await dataset.ch_grocery_order_created(
            timestamp=today_at_12 + datetime.timedelta(minutes=0),
            order=order,
            store=store,
            delivery_type='dispatch',
            max_eta=10,
        )
        await dataset.ch_grocery_order_assemble_ready(
            timestamp=today_at_12 + datetime.timedelta(minutes=1),
            order=order,
            store=store,
        )

        await dataset.ch_wms_order_processing(
            timestamp=today_at_12 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_matched(
            timestamp=today_at_12 + datetime.timedelta(minutes=5),
            order=order,
            store=store,
            courier=courier,
            delivery_type='courier',
        )

        await dataset.ch_wms_order_complete(
            timestamp=today_at_12 + datetime.timedelta(minutes=11),
            order=order,
            store=store,
        )

        await dataset.ch_grocery_order_pickup(
            timestamp=today_at_12 + datetime.timedelta(minutes=13),
            order=order,
            courier=courier,
            store=store,
        )

        await dataset.ch_grocery_delivering_arrived(
            timestamp=today_at_12 + datetime.timedelta(minutes=20),
            order=order,
            courier=courier,
            store=store,
        )

        await dataset.ch_grocery_order_delivered(
            timestamp=today_at_12 + datetime.timedelta(minutes=23),
            order=order,
            courier=courier,
            store=store,
        )


        await TabloMetric.refresh_metrics(
            stores=[store],
            now_time=today_at_12 + datetime.timedelta(minutes=60),
        )

        day_metric = await TabloMetric.load(
            ['day', 'store', store.store_id],
            by='conflict'
        )
        with day_metric.metrics as m:
            tap.eq(m.orders_count, 1, 'orders_count')

            tap.eq(m.assemble_wait_time_count, 1, 'assemble_wait_time_count')
            tap.eq(m.assemble_wait_time_sum, 240, 'assemble_wait_time_sum')
            tap.eq(m.assemble_wait_time, 240, 'assemble_wait_time')

            tap.eq(m.assemble_time_count, 1, 'assemble_time_count')
            tap.eq(m.assemble_time_sum, 360, 'assemble_time_sum')

            tap.eq(m.waiting_for_pickup_count, 1, 'waiting_for_pickup_count')
            tap.eq(m.waiting_for_pickup_sum, 120, 'waiting_for_pickup_sum')
            tap.eq(m.waiting_for_pickup, 120, 'waiting_for_pickup')

            tap.eq(m.to_client_time_count, 1, 'to_client_time_count')
            tap.eq(m.to_client_time_sum, 420, 'to_client_time_sum')
            tap.eq(m.to_client_time, 420, 'to_client_time')

            tap.eq(m.full_cte_count, 1, 'full_cte_count')
            tap.eq(m.full_cte_sum, 1140, 'full_cte_sum')
            tap.eq(m.full_cte, 1140, 'full_cte')

            tap.eq(m.lateness_5_min_count, 1, 'lateness_5_min_count')
            tap.eq(m.lateness_5_min, 100, 'lateness_5_min')

            tap.eq(m.pickup_count, 1, 'pickup_count')
            tap.eq(m.shift_time_sum, 3600, 'shift_time_sum')
            tap.eq(m.oph, 1, 'oph')

        tap.note('Прорастим метрики до компании')
        await TabloMetric.recalculate(
            company_ids=[store.company_id],
            cluster_ids=[store.cluster_id],
        )

        company_metric = await TabloMetric.load(
            ['day', 'company', store.company_id],
            by='conflict'
        )

        with company_metric.metrics as m:
            tap.eq(m.orders_count, 1, 'orders_count')

            tap.eq(m.assemble_wait_time_count, 1, 'assemble_wait_time_count')
            tap.eq(m.assemble_wait_time_sum, 240, 'assemble_wait_time_sum')
            tap.eq(m.assemble_wait_time, 240, 'assemble_wait_time')

            tap.eq(m.assemble_time_count, 1, 'assemble_time_count')
            tap.eq(m.assemble_time_sum, 360, 'assemble_time_sum')

            tap.eq(m.waiting_for_pickup_count, 1, 'waiting_for_pickup_count')
            tap.eq(m.waiting_for_pickup_sum, 120, 'waiting_for_pickup_sum')
            tap.eq(m.waiting_for_pickup, 120, 'waiting_for_pickup')

            tap.eq(m.to_client_time_count, 1, 'to_client_time_count')
            tap.eq(m.to_client_time_sum, 420, 'to_client_time_sum')
            tap.eq(m.to_client_time, 420, 'to_client_time')

            tap.eq(m.full_cte_count, 1, 'full_cte_count')
            tap.eq(m.full_cte_sum, 1140, 'full_cte_sum')
            tap.eq(m.full_cte, 1140, 'full_cte')

            tap.eq(m.lateness_5_min_count, 1, 'lateness_5_min_count')
            tap.eq(m.lateness_5_min, 100, 'lateness_5_min')

            tap.eq(m.pickup_count, 1, 'pickup_count')
            tap.eq(m.shift_time_sum, 3600, 'shift_time_sum')
            tap.eq(m.oph, 1, 'oph')
