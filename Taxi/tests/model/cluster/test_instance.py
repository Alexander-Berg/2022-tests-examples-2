async def test_instance(tap, dataset):
    with tap.plan(6):

        cluster = dataset.Cluster({
            'title': 'A1',
            'courier_shift_setup': {
                'pause_max_count': 2,
            },
        })
        tap.ok(cluster, 'Объект создан')
        tap.ok(await cluster.save(), 'сохранение')
        tap.ok(await cluster.save(), 'обновление')

        tap.eq(cluster.title, 'A1', 'title')
        tap.eq(cluster.map_layer, 'yandex', 'default map layer')
        tap.eq(
            cluster.courier_shift_setup.pause_max_count,
            2,
            'pause_max_count'
        )


async def test_dataset(tap, dataset):
    with tap.plan(1):
        cluster = await dataset.cluster()
        tap.ok(cluster, 'Объект создан')


async def test_get_setup(tap, dataset, now):
    with tap.plan(11, 'получение сетапа для курьеров'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_week_hours': 40,
                'max_day_hours': 12,
                'tags': ['tag1'],
            },
            courier_shift_underage_setup={
                'max_day_hours': 4,
                'tags': ['tag2'],
            },
        )
        courier_1 = await dataset.courier(cluster=cluster)
        courier_2 = await dataset.courier(cluster=cluster,
                                          birthday=now().date())

        common_setup = cluster.get_setup()
        tap.eq(common_setup, cluster.courier_shift_setup, 'common ok')

        adult_setup = cluster.get_setup(courier_1)
        tap.eq(adult_setup.max_week_hours, 40, 'adult max_week_hours ok')
        tap.eq(adult_setup.max_day_hours, 12, 'adult max_day_hours ok')
        tap.eq(adult_setup.tags, ['tag1'], 'adult tags ok')

        underage_setup = cluster.get_setup(courier_2)
        tap.eq(underage_setup.max_week_hours, 40, 'underage max_week_hours ok')
        tap.eq(underage_setup.max_day_hours, 4, 'underage max_day_hours ok')
        tap.eq(underage_setup.tags, ['tag2'], 'underage tags ok')

        underage_setup.tags.append('tag3')

        tap.eq(cluster.courier_shift_setup.max_week_hours, 40,
               'source max_week_hours not changed')
        tap.eq(cluster.courier_shift_setup.max_day_hours, 12,
               'source max_day_hours not changed')
        tap.eq(cluster.courier_shift_setup.tags, ['tag1'],
               'source tags not changed')

        tap.eq(cluster.courier_shift_underage_setup.tags, ['tag2', 'tag3'],
               'underage source tags changed')
