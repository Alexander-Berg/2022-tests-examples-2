from stall.model.analytics.tablo_metrics import TabloMetric
from stall.model.analytics.tablo_metrics_log import TabloMetricLog


async def test_recalculate(tap, dataset, uuid, now):
    with tap.plan(17, 'При проращивании метрик всё логи на месте'):
        _slice = uuid()
        _now = now().replace(microsecond=0)
        store = await dataset.store()

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
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
                'orders_count': 2
            }
        ).save()


        await TabloMetric.recalculate(
            company_ids=[store.company_id],
            cluster_ids=[store.cluster_id],
        )

        log_cursor = await TabloMetricLog.list(
            by='full',
            conditions=(
                ('slice', _slice),
            )
        )
        tap.eq(len(log_cursor.list), 5, 'Все логи на месте')
        logs = {
            log.entity: log for log in log_cursor.list
        }

        tap.eq(logs['store'].entity_id, store.store_id, 'store: entity_id')
        tap.eq(logs['store'].calculated, _now, 'store: calculated')
        tap.eq(
            logs['store'].metrics['orders_count'],
            2,
            'store: metrics.orders_count'
        )

        tap.eq(
            logs['supervisor'].entity_id,
            f'EMPTY:{store.company_id}:{store.cluster_id}',
            'supervisor: entity_id'
        )
        tap.eq(logs['supervisor'].calculated, _now, 'supervisor: calculated')
        tap.eq(
            logs['supervisor'].metrics['orders_count'],
            2,
            'supervisor: metrics.orders_count'
        )

        tap.eq(
            logs['cluster'].entity_id, store.cluster_id, 'cluster: entity_id'
        )
        tap.eq(logs['cluster'].calculated, _now, 'cluster: calculated')
        tap.eq(
            logs['cluster'].metrics['orders_count'],
            2,
            'cluster: metrics.orders_count'
        )

        tap.eq(
            logs['company'].entity_id, store.company_id, 'company: entity_id'
        )
        tap.eq(logs['company'].calculated, _now, 'company: calculated')
        tap.eq(
            logs['company'].metrics['orders_count'],
            2,
            'company: metrics.orders_count'
        )

        tap.eq(logs['total'].entity_id, 'total', 'total: entity_id')
        tap.eq(logs['total'].calculated, _now, 'total: calculated')
        tap.eq(
            logs['total'].metrics['orders_count'],
            2,
            'total: metrics.orders_count'
        )
