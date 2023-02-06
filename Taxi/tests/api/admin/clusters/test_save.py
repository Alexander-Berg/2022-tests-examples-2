import pytest

from stall.model.cluster import Cluster


async def test_save(tap, dataset, api, uuid):
    with tap.plan(19, 'Сохранение'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': external_id,
                'title': 'привет',
                'dispatch_setup': {
                    'delivery_fallback': 'taxi',
                    'delivery_max_weight': 10,
                },
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('cluster.updated')
        t.json_has('cluster.created')
        t.json_has('cluster.cluster_id')
        t.json_is('cluster.external_id', external_id)
        t.json_is('cluster.user_id', user.user_id)
        t.json_is('cluster.title', 'привет')
        t.json_is(
            'cluster.dispatch_setup',
            {
                'delivery_fallback': 'taxi',
                'delivery_max_weight': 10,
            }
        )

        cluster = await dataset.Cluster.load(
            t.res['json']['cluster']['cluster_id'])
        tap.ok(cluster, 'Объект создан')

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'cluster_id': cluster.cluster_id,
                'title': 'медвед',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('cluster.cluster_id', cluster.cluster_id)
        t.json_is('cluster.external_id', external_id)
        t.json_is('cluster.user_id', user.user_id)
        t.json_is('cluster.title', 'медвед')
        t.json_is('cluster.map_layer', 'yandex')


@pytest.mark.parametrize('setup', ({
    'slot_min_size': '00:00:00',
    'slot_max_size': '10:00:00',
    'pause_duration': '00:50:00',
    'shift_end_restriction': '12:34:56',
    'started_before_time': '01:01:01',
    'started_after_time': '10:10:10',
    'stopped_leave_before_time': '00:00:01',
    'timeout_template': '00:01:00',
    'timeout_request': '00:15:00',
    'timeout_processing': '01:00:00',
    'duration_between_stores': '00:10:15',
    'auto_start_max_lag': '00:05:00',
}, {
    'slot_min_size': 0,
    'slot_max_size': 36000,
    'pause_duration': 3000,
    'shift_end_restriction': 45296,
    'started_before_time': 3661,
    'started_after_time': 36610,
    'stopped_leave_before_time': 1,
    'timeout_template': 60,
    'timeout_request': 900,
    'timeout_processing': 3600,
    'duration_between_stores': 615,
    'auto_start_max_lag': 300,
}))
async def test_save_setup(tap, dataset, api, uuid, setup):
    with tap.plan(27, 'Сохранение настроек смен кластера'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': external_id,
                'title': 'Дикий первозданный кластер',
                'courier_shift_setup': setup,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        setup = t.res['json']['cluster']['courier_shift_setup']
        tap.eq(setup['slot_min_size'], '00:00:00', 'slot_min_size=00:00:00')
        tap.eq(setup['slot_max_size'], '10:00:00', 'slot_max_size=10:00:00')
        tap.eq(setup['pause_duration'], '00:50:00', 'pause_duration=00:50:00')
        tap.eq(
            setup['shift_end_restriction'],
            '12:34:56',
            'shift_end_restriction=12:34:56'
        )
        tap.eq(
            setup['started_before_time'],
            '01:01:01',
            'started_before_time=01:01:01'
        )
        tap.eq(
            setup['started_after_time'],
            '10:10:10',
            'started_after_time=10:10:10'
        )
        tap.eq(
            setup['stopped_leave_before_time'],
            '00:00:01',
            'stopped_leave_before_time=00:00:01'
        )
        tap.eq(
            setup['timeout_template'],
            '00:01:00',
            'timeout_template=00:01:00'
        )
        tap.eq(
            setup['timeout_request'],
            '00:15:00',
            'timeout_request=00:15:00'
        )
        tap.eq(
            setup['timeout_processing'],
            '01:00:00',
            'timeout_processing=01:00:00'
        )
        tap.eq(
            setup['duration_between_stores'],
            '00:10:15',
            'duration_between_stores=00:10:15'
        )
        tap.eq(
            setup['auto_start_max_lag'],
            '00:05:00',
            'auto_start_max_lag=00:05:00'
        )

        cluster = await Cluster.load(t.res['json']['cluster']['cluster_id'])
        setup = cluster.courier_shift_setup
        tap.eq(setup.slot_min_size, 0, 'slot_min_size=0')
        tap.eq(setup.slot_max_size, 36000, 'slot_max_size=36000')
        tap.eq(setup.pause_duration, 3000, 'pause_duration=3000')
        tap.eq(
            setup.shift_end_restriction,
            45296,
            'shift_end_restriction=45296'
        )
        tap.eq(setup.started_before_time, 3661, 'started_before_time=3661')
        tap.eq(setup.started_after_time, 36610, 'started_after_time=36610')
        tap.eq(
            setup.stopped_leave_before_time,
            1,
            'stopped_leave_before_time=1'
        )
        tap.eq(setup.timeout_template, 60, 'timeout_template=60')
        tap.eq(setup.timeout_request, 900, 'timeout_request=900')
        tap.eq(setup.timeout_processing, 3600, 'timeout_processing=3600')
        tap.eq(
            setup.duration_between_stores,
            615,
            'duration_between_stores=615'
        )
        tap.eq(
            setup.auto_start_max_lag,
            300,
            'auto_start_max_lag=300'
        )


async def test_shift_underage_setup(tap, dataset, api, uuid):
    with tap.plan(7, 'установка courier_shift_underage_setup'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': external_id,
                'title': 'Дикий первозданный кластер',
                'courier_shift_setup': {
                    'slot_min_size': '00:10:00',
                    'slot_max_size': '10:00:00',
                },
                'courier_shift_underage_setup': {
                    'slot_min_size': '00:00:00',
                    'slot_max_size': '04:00:00',
                },
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        setup = t.res['json']['cluster']['courier_shift_setup']
        tap.eq(setup['slot_min_size'], '00:10:00', 'slot_min_size=00:10:00')
        tap.eq(setup['slot_max_size'], '10:00:00', 'slot_max_size=10:00:00')

        setup = t.res['json']['cluster']['courier_shift_underage_setup']
        tap.eq(setup['slot_min_size'], '00:00:00', 'slot_min_size=00:00:00')
        tap.eq(setup['slot_max_size'], '04:00:00', 'slot_max_size=04:00:00')


async def test_double_eda_region_id(tap, dataset, api, uuid):
    with tap.plan(15, 'Сохранение с повторным eda_region_id'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        external_id = uuid()
        eda_region_id = uuid()
        title = uuid()

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': external_id,
                'eda_region_id': eda_region_id,
                'title': title,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cluster.cluster_id')
        t.json_is('cluster.external_id', external_id)
        t.json_is('cluster.eda_region_id', eda_region_id)
        t.json_is('cluster.user_id', user.user_id)
        t.json_is('cluster.title', title)

        cluster = await dataset.Cluster.load(
            t.res['json']['cluster']['cluster_id']
        )
        tap.ok(cluster, 'Объект создан')

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': external_id,
                'eda_region_id': eda_region_id,
                'title': uuid(),
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': uuid(),
                'eda_region_id': eda_region_id,
                'title': uuid(),
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_EXISTS')


async def test_save_admin_courier(tap, dataset, api):
    with tap.plan(10, 'разрешаем курьеру админов менять зоны и настройки смен'):
        cluster = await dataset.cluster()
        tap.eq(cluster.map_layer, 'yandex', 'map_layer по умолчанию')
        cluster2 = await dataset.cluster(
            zone={
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [
                                34.720460300843236,
                                32.47076123053345
                            ],
                            [
                                34.34143198053074,
                                31.689728820036894
                            ],
                            [
                                34.87976205865573,
                                31.48518376703709
                            ],
                            [
                                35.280763035218236,
                                32.36126346436616
                            ],
                            [
                                34.720460300843236,
                                32.47076123053345
                            ],
                        ]
                    ]
                },
                'properties': {
                    'external_id': '',
                    'name': '',
                    'address': '',
                },
            },
            map_layer='google',
        )
        tap.eq(cluster2.map_layer, 'google', 'Не дефолтный map_layer')

        user = await dataset.user(role='courier_admin')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'external_id': cluster.external_id,
                'title': cluster.title,
                'zone': cluster2.zone,
                'courier_shift_setup': cluster2.courier_shift_setup,
                'map_layer': cluster2.map_layer,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cluster.external_id', cluster.external_id)
        t.json_is('cluster.title', cluster.title)
        t.json_is('cluster.zone', cluster2.zone.pure_python())
        t.json_is('cluster.courier_shift_setup', cluster2.courier_shift_setup)
        t.json_is('cluster.map_layer', cluster2.map_layer)


@pytest.mark.parametrize('role', [
    'admin',
    'courier_admin',
    'courier_company_admin',
])
async def test_save_dispatch(tap, dataset, api, role):
    with tap.plan(4, 'Обновление dispatch_setup разными ролями'):
        cluster = await dataset.cluster()

        user = await dataset.user(role=role)

        t = await api(user=user)

        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'cluster_id': cluster.cluster_id,
                'title': cluster.title,
                'dispatch_setup': {
                    'delivery_fallback': 'deli',
                    'delivery_max_weight': 5,
                },
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is(
            'cluster.dispatch_setup',
            {
                'delivery_fallback': 'deli',
                'delivery_max_weight': 5,
            }
        )


async def test_save_dispatch_parameter(tap, dataset, api):
    with tap.plan(8, 'Проверка работы параметра dispatch_setup'):
        cluster = await dataset.cluster()

        user = await dataset.user(role='executer')

        t = await api(user=user)

        with user.role as role:
            role.add_permit('clusters_save', True)
            role.add_permit('clusters_load', True)
            role.add_permit(
                'save',
                {
                    'cluster': [
                        'zone',
                        'courier_shift_setup',
                        'map_layer']
                }
            )

            await t.post_ok(
                'api_admin_clusters_save',
                json={
                    'cluster_id': cluster.cluster_id,
                    'title': cluster.title,
                    'dispatch_setup': {
                        'delivery_fallback': 'taxi',
                        'delivery_max_weight': 10,
                    },
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            t.json_is(
                'cluster.dispatch_setup',
                {
                    'delivery_fallback': None,
                    'delivery_max_weight': None,
                }
            )

            role.add_permit(
                'save',
                {
                    'cluster': [
                        'zone',
                        'courier_shift_setup',
                        'map_layer',
                        'dispatch_setup']
                }
            )

            await t.post_ok(
                'api_admin_clusters_save',
                json={
                    'cluster_id': cluster.cluster_id,
                    'title': cluster.title,
                    'dispatch_setup': {
                        'delivery_fallback': 'taxi',
                        'delivery_max_weight': 10,
                    },
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            t.json_is(
                'cluster.dispatch_setup',
                {
                    'delivery_fallback': 'taxi',
                    'delivery_max_weight': 10,
                }
            )


async def test_disable_role_permits(tap, dataset, api):
    with tap.plan(14, 'Управлением пермитами роли через настройки кластера'):
        cluster = await dataset.cluster(disabled_role_permits={})
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        t = await api(user=user)

        # нет такой роли
        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'cluster_id': cluster.cluster_id,
                'title': cluster.title,
                'disabled_role_permits': {
                    'admin100500': ['courier_shifts_save'],
                },
            },
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')

        # нет такого пермита
        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'cluster_id': cluster.cluster_id,
                'title': cluster.title,
                'disabled_role_permits': {
                    'admin': ['courier_shifts_save100500'],
                },
            },
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')

        # успех, ограничение назначено
        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'cluster_id': cluster.cluster_id,
                'title': cluster.title,
                'disabled_role_permits': {
                    'admin': ['courier_shifts_save'],
                },
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'cluster.disabled_role_permits',
            {
                'admin': ['courier_shifts_save']
            }
        )

        # успех, ограничение снято
        await t.post_ok(
            'api_admin_clusters_save',
            json={
                'cluster_id': cluster.cluster_id,
                'title': cluster.title,
                'disabled_role_permits': {
                    'admin': [],
                },
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'cluster.disabled_role_permits',
            {
                'admin': []
            }
        )
