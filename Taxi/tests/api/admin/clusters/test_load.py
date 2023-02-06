import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4, 'Неизвестный идентификатор'):
        t = await api(role='admin')

        await t.post_ok('api_admin_clusters_load',
                        json={'cluster_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(5, 'Успешная загрузка'):

        cluster = await dataset.cluster()

        t = await api(role='admin')

        await t.post_ok('api_admin_clusters_load',
                        json={'cluster_id': cluster.cluster_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'получен')

        t.json_is('cluster.cluster_id', cluster.cluster_id)
        t.json_is('cluster.title', cluster.title)


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Успешная загрузка списка'):
        t = await api(role=role)
        cluster1 = await dataset.cluster()
        cluster2 = await dataset.cluster()
        await t.post_ok(
            'api_admin_clusters_load',
            json={'cluster_id': [cluster1.cluster_id,
                                 cluster2.cluster_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('cluster', 'есть в выдаче')
        res = t.res['json']['cluster']
        tap.eq_ok(
            sorted([res[0]['cluster_id'], res[1]['cluster_id']]),
            sorted([cluster1.cluster_id,
                    cluster2.cluster_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2, 'Неизвестные идентификаторы в списке'):
        t = await api(role=role)
        cluster1 = await dataset.cluster()
        await t.post_ok(
            'api_admin_clusters_load',
            json={'cluster_id': [cluster1.cluster_id,
                                 uuid()]})
        t.status_is(403, diag=True)


@pytest.mark.parametrize('role', ['admin'])
async def test_load_setup(tap, api, dataset, role):
    with tap.plan(19, 'Получение форматированных настроек кластера'):
        cluster = await dataset.cluster(courier_shift_setup={
            'slot_min_size': 0,
            'slot_max_size': 36000,
            'pause_duration': 3000,
            'shift_end_restriction': 45296,
            'started_before_time': 3661,
            'started_after_time': 36610,
            'stopped_leave_before_time': 1,
            'timeout_template': 60,
            'timeout_request': 900,
            'duration_between_stores': 615,
            'auto_start_max_lag': 300,
            'store_shifts_create_day_limit': 0,
            'store_shifts_save_day_limit': 1,
            'store_shifts_percent_limit': 50,
        })

        t = await api(role=role)

        await t.post_ok(
            'api_admin_clusters_load',
            json={'cluster_id': cluster.cluster_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Получен')
        t.json_is('cluster.courier_shift_setup.slot_min_size', '00:00:00')
        t.json_is('cluster.courier_shift_setup.slot_max_size', '10:00:00')
        t.json_is('cluster.courier_shift_setup.pause_duration', '00:50:00')
        t.json_is(
            'cluster.courier_shift_setup.shift_end_restriction',
            '12:34:56'
        )
        t.json_is('cluster.courier_shift_setup.started_before_time', '01:01:01')
        t.json_is('cluster.courier_shift_setup.started_after_time', '10:10:10')
        t.json_is(
            'cluster.courier_shift_setup.stopped_leave_before_time',
            '00:00:01'
        )
        t.json_is('cluster.courier_shift_setup.timeout_template', '00:01:00')
        t.json_is('cluster.courier_shift_setup.timeout_request', '00:15:00')
        t.json_is(
            'cluster.courier_shift_setup.duration_between_stores',
            '00:10:15'
        )
        t.json_is('cluster.courier_shift_setup.auto_start_max_lag', '00:05:00')
        t.json_is(
            'cluster.courier_shift_setup.store_admin_create_shifts',
            True
        )
        t.json_is(
            'cluster.courier_shift_setup.store_shifts_create_day_limit',
            0
        )
        t.json_is('cluster.courier_shift_setup.store_shifts_save_enable', True)
        t.json_is('cluster.courier_shift_setup.store_shifts_save_day_limit', 1)
        t.json_is('cluster.courier_shift_setup.store_shifts_percent_limit', 50)
