from stall.model.cluster import Cluster


async def test_simple(tap):
    with tap.plan(12, 'Операции сохранения / загрузки'):
        cluster = Cluster(title='Тест')
        tap.ok(cluster, 'инстанцирован')

        tap.eq(cluster.cluster_id, None, 'идентификатора до сохранения нет')
        tap.ok(await cluster.save(), 'сохранен')
        tap.ok(cluster.cluster_id, 'идентификатор назначился')
        cluster_id = cluster.cluster_id
        tap.eq(cluster.title, 'Тест', 'название')

        tap.ok(await cluster.save(), 'сохранен еще раз')
        tap.eq(cluster.cluster_id, cluster_id, 'идентификатор не поменялся')

        loaded = await Cluster.load(cluster_id)
        tap.ok(loaded, 'загружено')
        tap.isa_ok(loaded, Cluster, 'тип')
        tap.eq(loaded.title, cluster.title, 'название')

        tap.ok(await cluster.rm(), 'удалён')
        tap.ok(not await Cluster.load(cluster_id), 'удалён в БД')

async def test_eda(tap, uuid):
    with tap.plan(9, 'Операции сохранения / загрузки'):
        eda_region_id = uuid()
        cluster = Cluster(title='Тест', eda_region_id=eda_region_id)

        tap.ok(await cluster.save(), 'сохранен')

        loaded = await Cluster.load(cluster.cluster_id)
        tap.ok(loaded, 'загружено')
        tap.eq(loaded.eda_region_id, eda_region_id, 'eda_region_id')

        tap.ok(await cluster.save(), 'сохранен еще раз')

        eda_region_id = uuid()
        cluster.eda_region_id = eda_region_id
        tap.ok(await cluster.save(), 'сохранен')

        loaded = await Cluster.load(cluster.cluster_id)
        tap.ok(loaded, 'загружено')
        tap.eq(loaded.eda_region_id, eda_region_id, 'eda_region_id')

        tap.ok(await cluster.rm(), 'удалён')
        tap.ok(not await Cluster.load(cluster.cluster_id), 'удалён в БД')

async def test_setup(tap):
    with tap.plan(8, 'Сохранение с настройками'):
        cluster = Cluster(
            title='Тест',
            courier_shift_setup={
                'pause_max_count': 1,
                'pause_duration': 2,
                'shift_end_restriction': 3,
            },
        )

        tap.ok(cluster, 'инстанцирован')
        tap.eq(cluster.cluster_id, None, 'идентификатора до сохранения нет')

        tap.ok(await cluster.save(), 'сохранен')

        loaded = await Cluster.load(cluster.cluster_id)
        tap.ok(loaded, 'загружено')
        tap.ok(loaded.cluster_id, 'идентификатор назначился')

        tap.eq(
            loaded.courier_shift_setup.pause_max_count,
            1,
            'pause_max_count',
        )
        tap.eq(
            loaded.courier_shift_setup.pause_duration,
            2,
            'pause_duration',
        )
        tap.eq(
            loaded.courier_shift_setup.shift_end_restriction,
            3,
            'shift_end_restriction',
        )
