from collections import namedtuple
from stall.model.analytics.courier_metric import CourierMetric
from scripts.dev.update_courier_id_in_analytics import main


async def test_simple(tap, dataset, now, unique_int):
    with tap.plan(6, 'Заполнение courier_id в аналитике'):
        external_store_id = unique_int()
        store = await dataset.store(external_id=str(external_store_id))

        external_courier_id = unique_int()
        courier = await dataset.courier(
            store=store,
            vars={'external_ids': {'eats': str(external_courier_id)}},
        )
        _now = now()
        init_metric = CourierMetric(
            date=_now.date(),
            time=_now.replace(minute=0, second=0, microsecond=0, tzinfo=None),
            processed=_now,
            external_courier_id=str(external_courier_id),
            courier_name=courier.fullname,
            store_id=store.store_id,
        )
        await init_metric.save()

        metrics = await CourierMetric.list(
            by='full',
            conditions=(
                'store_id', store.store_id
            ),
        )
        tap.ok(len(metrics.list), 1, '1 курьер')
        with metrics.list[0] as metric:
            tap.eq(metric.courier_id, None, 'courier_id')
            tap.eq(
                metric.external_courier_id,
                str(external_courier_id),
                'external_courier_id'
            )

        # Запуск скрипта
        args = namedtuple('args', 'store_id, apply')(store.store_id, True)
        await main(args)

        updated_metrics = await CourierMetric.list(
            by='full',
            conditions=(
                'store_id', store.store_id
            ),
        )
        tap.ok(len(updated_metrics.list), 1, '1 курьер')
        with updated_metrics.list[0] as metric:
            tap.eq(metric.courier_id, courier.courier_id, 'courier_id')
            tap.eq(
                metric.external_courier_id,
                str(external_courier_id),
                'external_courier_id'
            )


async def test_list(tap, dataset, now, cfg, unique_int):
    # pylint: disable=too-many-locals
    with tap.plan(11, 'Батчевое заполнение courier_id в аналитике'):
        cfg.set('cursor.limit', 3)
        external_store_id = unique_int()
        store = await dataset.store(external_id=str(external_store_id))

        couriers = {}
        for _ in range(5):
            external_courier_id = str(unique_int())
            couriers[external_courier_id] = await dataset.courier(
                store=store,
                vars={'external_ids': {'eats': external_courier_id}},
            )
            _now = now()
            init_metric = CourierMetric(
                date=_now.date(),
                time=_now.replace(
                    minute=0,
                    second=0,
                    microsecond=0,
                    tzinfo=None
                ),
                processed=_now,
                external_courier_id=external_courier_id,
                courier_name=couriers[external_courier_id].fullname,
                store_id=store.store_id,
            )
            await init_metric.save()

        # Запуск скрипта
        args = namedtuple('args', 'store_id, apply')(store.store_id, True)
        await main(args)

        metrics = await CourierMetric.list(
            by='full',
            conditions=(
                'store_id', store.store_id
            ),
        )
        tap.ok(len(metrics.list), 1, '1 курьер')
        for metric in metrics.list:
            courier = couriers[str(metric.external_courier_id)]
            tap.eq(metric.courier_id, courier.courier_id, 'courier_id')
            tap.eq(
                str(metric.external_courier_id),
                courier.vars('external_ids.eats'),
                'external_courier_id'
            )


