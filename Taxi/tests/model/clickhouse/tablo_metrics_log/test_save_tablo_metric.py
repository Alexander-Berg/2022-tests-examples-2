import datetime
from stall.model.analytics.tablo_metrics import TabloMetric
from stall.model.analytics.tablo_metrics_log import TabloMetricLog


async def test_saving(tap, dataset, uuid, now):
    with tap.plan(10, 'При сохранении метрики отправляются в лог'):
        _slice = uuid()
        _now = now().replace(microsecond=0)
        store = await dataset.store()

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
                ('entity', 'store'),
                ('entity_id', store.store_id)
            )
        )
        tap.eq(log_cursor.list, [], 'Лога нет')

        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=_now,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            metrics={
                'some_metric': 2
            }
        ).save()

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
                ('entity', 'store'),
                ('entity_id', store.store_id),
            )
        )
        tap.eq(len(log_cursor.list), 1, 'Лог появился')
        with log_cursor.list[0] as log:
            tap.eq(log.slice, _slice, 'slice')
            tap.eq(log.entity, 'store', 'entity')
            tap.eq(log.entity_id, store.store_id, 'store_id')
            tap.eq(log.calculated, _now, 'calculated')
            tap.eq(log.company_id, store.company_id, 'company_id')
            tap.eq(log.cluster_id, store.cluster_id, 'cluster_id')
            tap.eq(log.store_id, store.store_id, 'store_id')
            tap.eq(log.metrics, {'some_metric': 2}, 'metrics')


async def test_save_twice(tap, dataset, uuid, now):
    with tap.plan(10, 'При пересохранении обновляются данные'):
        _slice = uuid()
        _now = now().replace(microsecond=0)
        store = await dataset.store()

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
                ('entity', 'store'),
                ('entity_id', store.store_id)
            )
        )
        tap.eq(log_cursor.list, [], 'Лога нет')

        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=_now,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            metrics={
                'some_metric': 3
            }
        ).save()

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
                ('entity', 'store'),
                ('entity_id', store.store_id),
            )
        )
        tap.eq(len(log_cursor.list), 1, 'Лог появился')
        with log_cursor.list[0] as log:
            old_lsn = log.lsn
            tap.eq(log.calculated, _now, 'calculated')
            tap.eq(log.supervisor_id, None, 'supervisor_id')
            tap.eq(log.metrics, {'some_metric': 3}, 'metrics')

        tap.note('Сохраним на ту же дату но другую метрику')
        supervisor_id = uuid()
        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=_now,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            supervisor_id=supervisor_id,
            store_id=store.store_id,
            metrics={
                'another_metric': 5
            }
        ).save()

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
                ('entity', 'store'),
                ('entity_id', store.store_id),
            )
        )
        tap.eq(len(log_cursor.list), 1, 'Лог есть')
        with log_cursor.list[0] as log:
            tap.eq(log.calculated, _now, 'тот же calculated')
            tap.eq(log.supervisor_id, supervisor_id, 'новый supervisor_id')
            tap.eq(
                log.metrics, {'another_metric': 5}, 'новое значение metrics'
            )
            tap.ne_ok(log.lsn, old_lsn, 'lsn изменился')


async def test_save_two(tap, dataset, uuid, now):
    with tap.plan(5, '2 сохранения 2 лога'):
        _slice = uuid()
        timestamp_1 = now().replace(microsecond=0)
        timestamp_2 = timestamp_1 + datetime.timedelta(minutes=1)
        store = await dataset.store()

        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=timestamp_1,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            metrics={
                'some_metric': 3
            }
        ).save()

        await TabloMetric(
            slice=_slice,
            entity='store',
            entity_id=store.store_id,
            calculated=timestamp_2,
            company_id=store.company_id,
            cluster_id=store.cluster_id,
            store_id=store.store_id,
            metrics={
                'some_metric': 5
            }
        ).save()

        log_cursor = await TabloMetricLog.list(
            by='walk',
            conditions=(
                ('slice', _slice),
                ('entity', 'store'),
                ('entity_id', store.store_id),
            ),
            sort=(
                ('calculated', 'ASC'),
            )
        )
        tap.eq(len(log_cursor.list), 2, '2 записи в логе')
        with log_cursor.list[0] as log:
            tap.eq(log.calculated, timestamp_1, '1.calculated')
            tap.eq(log.metrics, {'some_metric': 3}, '1.metrics')
        with log_cursor.list[1] as log:
            tap.eq(log.calculated, timestamp_2, '2.calculated')
            tap.eq(log.metrics, {'some_metric': 5}, '2.metrics')
