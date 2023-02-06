import logging

from datetime import timedelta
from contextlib import contextmanager

from libstall.log import metrics_log
from scripts.cron.courier_shift_monitoring import process


@contextmanager
def propagate_log(logger: logging.Logger):
    propagate_backup = logger.propagate
    logger.propagate = True
    try:
        yield
    finally:
        logger.propagate = propagate_backup


async def test_simple(tap, dataset, caplog, now):
    with tap.plan(6, 'Метрики отправляются'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift_processing = await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        await dataset.order(
            store_id=store.store_id,
            courier_shift=shift_processing,
            status='processing',
            estatus='waiting',
        )
        await dataset.courier_shift(
            store=store,
            status='absent',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 2, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 1, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 1, 'с заказами')


async def test_processing_shifts(tap, dataset, caplog, now):
    with tap.plan(6, 'Метрики использования смен (заказы + processing)'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        # 5 заказов на 1 смену и началась 1 час раньше положенного
        shift_processing_1 = await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now + timedelta(hours=1),   # курьер пришел заранее
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        for _ in range(5):
            await dataset.order(
                store_id=store.store_id,
                courier_shift=shift_processing_1,
                courier_id=shift_processing_1.courier_id,
                status='processing',
                estatus='waiting',
            )

        # пока ни одного заказа
        await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        # 40 заказов, но уже закрыты
        shift_processing_3 = await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=8),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        for _ in range(40):
            await dataset.order(
                store_id=store.store_id,
                courier_shift=shift_processing_3,
                courier_id=shift_processing_3.courier_id,
                status='complete',
                estatus='done',
            )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 2, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 3, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 1, 'с заказами')


async def test_occupancy_300_percents(tap, dataset, caplog, now):
    with tap.plan(6, 'Метрика наполняемости смен, 300%'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()
        cluster = await dataset.cluster()

        store = await dataset.store(cluster=cluster)

        # обычная
        await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        # созданная вручную (вне плана)
        await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned-extra',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        # начата произвольно, "свободная" (вне плана)
        await dataset.courier_shift(
            store=store,
            status='processing',
            placement='unplanned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 1, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 3, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 0, 'с заказами')


async def test_occupancy_early_or_late(tap, dataset, caplog, now):
    with tap.plan(6, 'Метрика наполняемости смен, начата раньше/позже'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        # обычные, 10шт
        for _ in range(10):
            await dataset.courier_shift(
                store=store,
                status='processing',
                placement='planned',
                started_at=_now - timedelta(hours=1),
                closes_at=_now + timedelta(hours=2),
                shift_events=[{
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                }],
            )
        # началась раньше положенного
        await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=10),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        # должна была уже закончится
        await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=10),
            closes_at=_now - timedelta(hours=1),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 10, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 12, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 0, 'с заказами')


async def test_occupancy_ignore_reissue(tap, dataset, caplog, now):
    with tap.plan(6, 'Метрика наполняемости смен, только оригиналы'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        # обычные, 10шт
        for _ in range(10):
            await dataset.courier_shift(
                store=store,
                status='processing',
                placement='planned',
                started_at=_now - timedelta(hours=1),
                closes_at=_now + timedelta(hours=2),
                shift_events=[{
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                }],
            )
        # будет отменена
        target = await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(minutes=10),
            closes_at=_now + timedelta(hours=10),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        # отменяем и переиздаем
        await target.close_and_reissue(
            close_status='cancelled',
            setup=cluster.get_setup(),
            placement='replacement',
            # Смена уменьшена на час, т.е. начнется в будущем
            time_offset=3600,
            log_type='courier_shift.job_courier_cancel_all',
            detail={
                'reason': 'reason',
                'source': 'source',
            },
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 11, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 10, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 0, 'с заказами')


async def test_several_stores(tap, dataset, caplog, now):
    with tap.plan(9, 'Метрики отправляются сразу по нескольким лавкам'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()

        # лавка №1 (1/2 исполняется и на 1/1 есть заказ)
        cluster = await dataset.cluster()
        store_1 = await dataset.store(cluster=cluster)
        shift_processing = await dataset.courier_shift(
            store=store_1,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        await dataset.order(
            store_id=store_1.store_id,
            courier_shift=shift_processing,
            status='processing',
            estatus='waiting',
        )
        await dataset.courier_shift(
            store=store_1,
            status='absent',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
        )

        # лавка №2 (1/1 исполняется и на 0/1 есть заказ)
        cluster_2 = await dataset.cluster()
        store_2 = await dataset.store(cluster=cluster_2)
        shift_processing = await dataset.courier_shift(
            store=store_2,
            status='processing',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=[store_1.store_id, store_2.store_id])

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 2, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 2, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 2, 'и одна лавка на третью')

        # лавка №1
        tap.eq(planned_shifts[store_1.external_id], 2, 'смены по плану')
        tap.eq(processing_shifts[store_1.external_id], 1, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store_1.external_id], 1, 'с заказами')

        # лавка №2
        tap.eq(planned_shifts[store_2.external_id], 1, 'смены по плану')
        tap.eq(processing_shifts[store_2.external_id], 1, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store_2.external_id], 0, 'с заказами')


async def test_err_no_plan(tap, dataset, caplog, now):
    with tap.plan(6, 'Ошибка. По плану не должно быть, но есть'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()

        # лавка №1 (1/0 исполняется и на 1/1 есть заказ)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift_processing = await dataset.courier_shift(
            store=store,
            status='processing',
            placement='planned-extra',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        await dataset.order(
            store_id=store.store_id,
            courier_shift=shift_processing,
            status='processing',
            estatus='waiting',
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 0, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 1, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 1, 'с заказами')


async def test_err_no_processing(tap, dataset, caplog, now):
    with tap.plan(6, 'Ошибка. Курьер успел закрыть смену,'
                     'но получил заказ из-за лага'), \
            propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        _now = now()

        # лавка №1 (0/1 исполняется и на 1/0 есть заказ)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift_processing = await dataset.courier_shift(
            store=store,
            status='leave',
            placement='planned',
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        await dataset.order(
            store_id=store.store_id,
            courier_shift=shift_processing,
            status='processing',
            estatus='waiting',
        )

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(_store_id=store.store_id)

        _target = 'courier_shift_monitoring.planned_shifts'
        planned_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.processing_shifts'
        processing_shifts = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        _target = 'courier_shift_monitoring.shifts_with_orders'
        shifts_with_orders = {
            rec.ctx['depot_id']: rec.ctx['value']
            for rec in caplog.records
            if rec.ctx['name'] == _target
        }

        tap.eq(len(planned_shifts), 1, 'одна лавка на первую метрику')
        tap.eq(len(processing_shifts), 1, 'одна лавка на вторую метрику')
        tap.eq(len(shifts_with_orders), 1, 'и одна лавка на третью')
        tap.eq(planned_shifts[store.external_id], 1, 'смены по плану')
        tap.eq(processing_shifts[store.external_id], 0, 'исполняются сейчас')
        tap.eq(shifts_with_orders[store.external_id], 1, 'с заказами')
