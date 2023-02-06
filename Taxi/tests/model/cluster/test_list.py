from stall.model.cluster import Cluster


async def test_simple(dataset, tap):
    with tap.plan(9, 'Операция получения списка кластеров'):
        cluster = await dataset.cluster()
        tap.ok(cluster, 'курьер создан')

        cursor = await Cluster.list(
            by='full',
            conditions=('cluster_id', cluster.cluster_id),
        )

        with cursor:
            tap.ok(cursor.list, 'список получен')
            tap.eq(len(cursor.list), 1, 'в нем один элемент')

            loaded = cursor.list[0]

            tap.isa_ok(loaded, Cluster, 'курьер')
            tap.eq(loaded.cluster_id, cluster.cluster_id, 'идентификатор')
            tap.eq(loaded.external_id, cluster.external_id, 'external_id')
            tap.eq(loaded.eda_region_id, cluster.eda_region_id, 'eda_region_id')
            tap.eq(loaded.tanker_id, cluster.tanker_id, 'tanker_id')
            tap.eq(loaded.title, cluster.title, 'название')


async def test_eda(dataset, tap, uuid):
    with tap.plan(6, 'Операция получения списка кластеров по eda_region_id'):
        cluster = await dataset.cluster(eda_region_id=uuid())
        tap.ok(cluster, 'курьер создан')

        cursor = await Cluster.list(
            by='full',
            conditions=('eda_region_id', cluster.eda_region_id),
            sort=(),
        )

        with cursor:
            tap.ok(cursor.list, 'список получен')
            tap.eq(len(cursor.list), 1, 'в нем один элемент')

            loaded = cursor.list[0]

            tap.isa_ok(loaded, Cluster, 'курьер')
            tap.eq(loaded.cluster_id, cluster.cluster_id, 'идентификатор')
            tap.eq(loaded.eda_region_id, cluster.eda_region_id, 'eda_region_id')
