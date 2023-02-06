from stall.model.store import Store


async def test_cluster_stat(tap, dataset, uuid):
    with tap.plan(4, 'Статистика по складам по кластерам'):
        store = await dataset.store(cluster=uuid())
        tap.ok(store, 'Один склад создан')

        stat = await Store.cluster_stat()

        tap.isa_ok(stat, dict, 'Статистика получена')

        tap.in_ok((store.cluster, store.status),
                  stat,
                  'В статистике есть склад')
        tap.eq(stat[(store.cluster, store.status)], 1, 'один')


async def test_cluster_stat_filter(tap, dataset, uuid):
    with tap.plan(5, 'Статистика по складам по кластерам'):
        store = await dataset.store(cluster=uuid())
        tap.ok(store, 'Один склад создан')

        stat = await Store.cluster_stat(cluster=store.cluster)

        tap.isa_ok(stat, dict, 'Статистика получена')

        tap.in_ok((store.cluster, store.status),
                  stat,
                  'В статистике есть склад')
        tap.eq(stat[(store.cluster, store.status)], 1, 'один')
        tap.eq(len(stat.keys()), 1, 'Только одна запись в статистике')
