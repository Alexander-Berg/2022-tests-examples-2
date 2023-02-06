# pylint: disable=unused-variable,invalid-name

from libstall.util import time2iso


async def test_simple(tap, api, dataset):
    with tap.plan(22, 'Список курьеров'):
        cluster = await dataset.cluster()
        user = await dataset.user()
        courier = await dataset.courier(status='disabled', cluster=cluster)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_couriers_list',
            json={'cluster_id': cluster.cluster_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('couriers.0')
        t.json_is('couriers.0.courier_id', courier.courier_id)
        t.json_is('couriers.0.first_name', courier.first_name)
        t.json_is('couriers.0.middle_name', courier.middle_name)
        t.json_is('couriers.0.last_name', courier.last_name)
        t.json_is('couriers.0.external_id', courier.external_id)
        t.json_is('couriers.0.status', courier.status)
        t.json_is('couriers.0.blocks', [])
        t.json_is('couriers.0.cluster_id', courier.cluster_id)
        t.json_is('couriers.0.delivery_type', courier.delivery_type)
        t.json_is('couriers.0.tags', courier.tags)
        t.json_is('couriers.0.user_id', courier.user_id)
        t.json_is('couriers.0.updated', time2iso(courier.updated))
        t.json_is('couriers.0.created', time2iso(courier.created))
        t.json_is('couriers.0.vars', courier.vars)
        t.json_is('couriers.0.lsn', courier.lsn)
        t.json_is('couriers.0.serial', courier.serial)
        t.json_hasnt('couriers.1')


async def test_access(tap, api, dataset):
    with tap.plan(3, 'Нет доступа'):
        user = await dataset.user(role='admin')

        await dataset.courier()

        with user.role as role:
            role.remove_permit('couriers_seek')

            t = await api(user=user)
            await t.post_ok('api_admin_couriers_list', json={})

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_tags_store(tap, api, dataset):
    with tap.plan(4, 'Курьер привязан к лавке'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store1)
        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.store_id],
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_list',
                json={'cluster_id': cluster.cluster_id},
            )
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('couriers.0.courier_id', courier.courier_id)


async def test_tags_store_over(tap, api, dataset):
    with tap.plan(5, 'Курьер привязан к другой лавке'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store1)
        await dataset.courier(
            cluster=cluster,
            tags_store=[store2.store_id],
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_list',
                json={'cluster_id': cluster.cluster_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_hasnt('couriers.0')


async def test_tags_store_empty(tap, api, dataset):
    with tap.plan(5, 'Курьер не привязан к лавке'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)
        await dataset.courier(cluster=cluster)

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_list',
                json={'cluster_id': cluster.cluster_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_hasnt('couriers.0')


async def test_tags_store_stores_allow(tap, api, dataset):
    with tap.plan(5, 'Курьер привязан к лавке, но пользователь ограничен'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        store3 = await dataset.store(cluster=cluster)
        user = await dataset.user(
            role='admin',
            stores_allow=[store2.store_id],
        )

        courier1 = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.store_id],
        )
        courier2 = await dataset.courier(
            cluster=cluster,
            tags_store=[store2.store_id],
        )
        courier3 = await dataset.courier(
            cluster=cluster,
            tags_store=[store3.store_id],
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_list',
                json={'cluster_id': cluster.cluster_id},
            )
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('couriers.0.courier_id', courier2.courier_id)
            t.json_hasnt('couriers.1')


async def test_tags_store_stores_allow_many(tap, api, dataset):
    with tap.plan(
            5,
            'Курьер привязан к множеству лавок, но пользователь ограничен'
    ):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        store3 = await dataset.store(cluster=cluster)
        user = await dataset.user(
            role='admin',
            stores_allow=[store1.store_id, store2.store_id],
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store2.store_id, store3.store_id],
        )

        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_list',
                json={'cluster_id': cluster.cluster_id},
            )
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('couriers.0.courier_id', courier.courier_id)
            t.json_hasnt('couriers.1')


async def test_stores(tap, api, dataset):
    with tap.plan(7, 'Список курьеров пользователями разных складов'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)

        user1 = await dataset.user(store=store1, role='admin')
        user2 = await dataset.user(store=store2, role='admin')

        courier = await dataset.courier(cluster=cluster)

        t1 = await api(user=user1)
        await t1.post_ok(
            'api_admin_couriers_list',
            json={'cluster_id': cluster.cluster_id},
        )

        t1.status_is(200, diag=True)
        t1.json_is('code', 'OK')

        received1 = t1.res['json']['couriers']
        received1 = {c['courier_id'] for c in received1}

        exists = courier.courier_id in received1
        tap.ok(exists, 'Получены первым пользователем')

        t2 = await api(user=user2)
        await t2.post_ok('api_admin_couriers_list', json={})

        received2 = t1.res['json']['couriers']
        received2 = {c['courier_id'] for c in received2}

        exists = courier.courier_id in received2
        tap.ok(exists, 'Получены вторым пользователем')

        tap.eq(received1, received2, 'Получены одинаковые списки')

# pylint: disable=too-many-locals


async def test_filter_tags(tap, api, dataset):
    with tap.plan(10, 'Список курьеров по тегам'):
        user = await dataset.user(role='admin')

        courier1 = await dataset.courier(tags=['auto', 'velo'])
        courier2 = await dataset.courier(tags=['auto'])
        courier3 = await dataset.courier(tags=['velo'])
        courier4 = await dataset.courier(tags=[])
        courier5 = await dataset.courier()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'tags': ['auto'],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        couriers_true = [courier1, courier2]
        couriers_false = [courier3, courier4, courier5]
        expected = {courier.courier_id for courier in couriers_true}
        unexpected = {courier.courier_id for courier in couriers_false}
        received = t.res['json']['couriers']
        received = {courier['courier_id'] for courier in received}

        exists = all(e in received for e in expected)
        unexists = any(u in received for u in unexpected)

        tap.ok(exists, 'Получены все auto')
        tap.ok(not unexists, 'Лишние не получены')

        await t.post_ok('api_admin_couriers_list', json={
            'tags': ['auto', 'velo'],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        couriers_true = [courier1, courier2, courier3]
        couriers_false = [courier4, courier5]
        expected = {courier.courier_id for courier in couriers_true}
        unexpected = {courier.courier_id for courier in couriers_false}
        received = t.res['json']['couriers']
        received = {courier['courier_id'] for courier in received}

        exists = all(e in received for e in expected)
        unexists = any(u in received for u in unexpected)

        tap.ok(exists, 'Получены все auto, velo')
        tap.ok(not unexists, 'Лишние не получены')


async def test_filter_courier_id(tap, api, dataset):
    with tap.plan(11, 'Список курьеров по внутренним идентификаторам'):
        user = await dataset.user()

        courier1 = await dataset.courier()
        courier2 = await dataset.courier()
        courier3 = await dataset.courier()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'courier_id': courier1.courier_id,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('couriers.0')
        t.json_is('couriers.0.courier_id', courier1.courier_id, 'Получен 1')
        t.json_hasnt('couriers.1', 'Других нет')

        await t.post_ok('api_admin_couriers_list', json={
            'courier_id': [courier2.courier_id, courier3.courier_id],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        expected = {courier2.courier_id, courier3.courier_id}
        unexpected = {courier1.courier_id}
        received = t.res['json']['couriers']
        received = {courier['courier_id'] for courier in received}

        exists = all(e in received for e in expected)
        tap.ok(exists, 'Получены курьеры 2, 3')

        unexists = any(u in received for u in unexpected)
        tap.ok(not unexists, 'Курьер 1 не получен')


async def test_filter_external_id(tap, api, dataset):
    with tap.plan(10, 'Список курьеров по внешним идентификаторам'):
        user = await dataset.user()
        courier_1 = await dataset.courier()
        courier_2 = await dataset.courier()
        courier_3 = await dataset.courier()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'courier_id': courier_1.external_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('couriers.0')
        t.json_is('couriers.0.external_id', courier_1.external_id, 'Получен 1')
        t.json_hasnt('couriers.1', 'Других нет')

        await t.post_ok('api_admin_couriers_list', json={
            'courier_id': [courier_2.external_id, courier_3.external_id],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.eq(
            sorted([courier_2.external_id, courier_3.external_id]),
            sorted([c['external_id'] for c in t.res['json']['couriers']]),
            'Получены курьеры 2, 3',
        )


async def test_filter_status(tap, api, dataset):
    with tap.plan(6, 'Список курьеров по статусам'):
        user = await dataset.user(role='admin')

        cluster = await dataset.cluster()
        courier1 = await dataset.courier(cluster=cluster, status='disabled')
        courier2 = await dataset.courier(cluster=cluster)
        courier3 = await dataset.courier(cluster=cluster, status='active')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'cluster_id': cluster.cluster_id,
            'status': 'active',
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        received = {x['courier_id']: x for x in t.res['json']['couriers']}

        with courier1 as courier:
            tap.ok(not received.get(courier.courier_id), 'disabled')

        with courier2 as courier:
            tap.ok(received.get(courier.courier_id), 'default')

        with courier3 as courier:
            tap.ok(received.get(courier.courier_id), 'active')


async def test_filter_name(tap, api, dataset):
    with tap.plan(5, 'Список курьеров по имени'):
        user = await dataset.user(role='admin')

        courier1 = await dataset.courier(
            first_name='X',
            middle_name='X',
            last_name='Поваляев',
        )
        courier2 = await dataset.courier(
            first_name='Понасовец',
            middle_name='X',
            last_name='X',
        )
        courier3 = await dataset.courier(
            first_name=None,
            middle_name='Понов',
            last_name='X',
        )
        courier4 = await dataset.courier(
            first_name=None,
            middle_name='X',
            last_name='Понов',
        )
        courier5 = await dataset.courier(
            first_name='X',
            middle_name='X',
            last_name='Антонов',
        )
        courier6 = await dataset.courier(
            first_name='X',
            middle_name='X',
            last_name='Непонов',
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'name': 'пон',
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        expected = {courier2.courier_id, courier3.courier_id,
                    courier4.courier_id}
        unexpected = {courier1.courier_id, courier5.courier_id,
                      courier6.courier_id}
        received = t.res['json']['couriers']
        received = {courier['courier_id'] for courier in received}

        exists = all(e in received for e in expected)
        tap.ok(exists, 'Получены')

        unexists = any(u in received for u in unexpected)
        tap.ok(not unexists, 'Лишние не получены')


async def test_filter_eda_id(tap, api, dataset, uuid):
    with tap.plan(5, 'Список курьеров по Еда ID'):
        user = await dataset.user(role='admin')

        search = uuid()

        courier1 = await dataset.courier(
            first_name='X',
            middle_name='X',
            last_name='Поваляев',
            vars={'external_ids': {'eats': search}},
        )
        await dataset.courier(
            first_name='Понасовец',
            middle_name='X',
            last_name='X',
            vars={'external_ids': {'eats': uuid()}},
        )
        await dataset.courier(
            vars={'external_ids': {'eats': uuid()}},
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'name': search[:-2],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


        couriers = tuple(
            courier['courier_id']
            for courier in t.res['json']['couriers']
        )
        tap.eq_ok(len(couriers), 1, 'По запросу найден 1 курьер')
        tap.in_ok(courier1.courier_id, couriers, 'Курьер 1 найден по EDA ID')


async def test_filter_name_with_sections(tap, api, dataset):
    with tap.plan(7, 'Список курьеров по составному имени'):
        cluster = await dataset.cluster()
        user = await dataset.user(role='admin')

        courier1 = await dataset.courier(
            cluster_id=cluster.cluster_id,
            first_name='X',
            middle_name='Антонович',
            last_name='Павлов',
        )
        courier2 = await dataset.courier(
            cluster_id=cluster.cluster_id,
            first_name='Павел',
            middle_name='Антонович',
            last_name=None,
        )
        courier3 = await dataset.courier(
            cluster_id=cluster.cluster_id,
            first_name='Антон',
            middle_name='Антонович',
            last_name='Антонов',
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'cluster_id': cluster.cluster_id,
            'name': 'пав антон',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        couriers = tuple(
            courier['courier_id']
            for courier in t.res['json']['couriers']
        )
        tap.eq_ok(len(couriers), 2, 'По запросу найдено 2 курьера')
        tap.in_ok(courier1.courier_id, couriers,
                  'Курьер1 найден по Отчеству и фамилии')
        tap.in_ok(courier2.courier_id, couriers,
                  'Курьер2 найден по Имени и отчетсву')
        tap.not_in_ok(courier3.courier_id, couriers,
                      'У Курьер3 совпадает только одна часть ФИО из двух')

# pylint: disable=too-many-locals


async def test_filter_mix(tap, api, dataset):
    with tap.plan(5, 'Список курьеров по фильтрам'):
        user = await dataset.user(role='admin')

        courier1 = await dataset.courier(
            first_name='X',
            middle_name='X',
            last_name='Панасовец',
            tags=['auto', 'velo'],
        )
        courier2 = await dataset.courier(
            last_name='Поваляй',
            tags=['velo', 'walk'],
        )
        courier3 = await dataset.courier(
            last_name='Поваляев',
            tags=['auto'],
        )
        courier4 = await dataset.courier(
            last_name='Понов',
            tags=['velo'],
        )
        courier5 = await dataset.courier(
            first_name='X',
            middle_name='X',
            last_name='Александров',
            tags=['velo'],
        )
        courier6 = await dataset.courier(
            last_name='Поняка',
            tags=['plain'],
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'name': 'по',
            'tags': ['velo', 'plain'],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        couriers_true = [courier2, courier4, courier6]
        couriers_false = [courier1, courier3, courier5]
        expected = {courier.courier_id for courier in couriers_true}
        unexpected = {courier.courier_id for courier in couriers_false}
        received = t.res['json']['couriers']
        received = {courier['courier_id'] for courier in received}

        exists = all(e in received for e in expected)
        unexists = any(u in received for u in unexpected)

        tap.ok(exists, 'Получены')
        tap.ok(not unexists, 'Лишние не получены')


async def test_eda_id(tap, api, dataset, unique_int):
    with tap.plan(6, 'Фильтрация по Едовому ID'):
        user = await dataset.user()
        courier_eda_id = str(unique_int())
        courier = await dataset.courier(
            vars={'external_ids': {'eats': courier_eda_id}}
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_couriers_list',
            json={'courier_eda_id': courier_eda_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('couriers.0')
        t.json_is('couriers.0.courier_id', courier.courier_id)


async def test_filter_blocks(tap, api, dataset):
    with tap.plan(8, 'Список курьеров с блокировками'):
        user = await dataset.user(role='admin')

        cluster = await dataset.cluster()
        courier1 = await dataset.courier(
            cluster=cluster,
            blocks=[{'source': 'wms', 'reason': 'ill'}],
        )
        courier2 = await dataset.courier(cluster=cluster)

        t = await api(user=user)

        with courier1 as courier:
            await t.post_ok('api_admin_couriers_list', json={
                'cluster_id': cluster.cluster_id,
                'blocks': True,
            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is(
                'couriers.0.courier_id',
                courier.courier_id,
                'заблокированные'
            )

        with courier2 as courier:
            await t.post_ok('api_admin_couriers_list', json={
                'cluster_id': cluster.cluster_id,
                'blocks': False,
            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is(
                'couriers.0.courier_id',
                courier.courier_id,
                'не заблокирован'
            )


async def test_filter_order_provider(tap, api, dataset):
    with tap.plan(7, 'Фильтрация по источнику заказов'):
        user = await dataset.user()
        cluster = await dataset.cluster()
        courier = await dataset.courier(order_provider='lavka', cluster=cluster)
        await dataset.courier(order_provider='eda', cluster=cluster)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_couriers_list',
            json={
                'cluster_id': cluster.cluster_id,
                "delivery_type": "foot",
                'order_provider': 'lavka',
                "blocks": False,
                "status": ["active"],
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('couriers.0')
        t.json_is('couriers.0.courier_id', courier.courier_id)
        t.json_hasnt('couriers.1')


async def test_courier_service_id(tap, api, dataset):
    with tap.plan(6, 'Список курьеров по ID курьерской службы'):
        user = await dataset.user()
        courier = await dataset.courier(
            courier_service_id=123,
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'courier_service_id': 123,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('couriers.0')
        t.json_is('couriers.0.courier_id', courier.courier_id)


async def test_courier_service_name(tap, api, dataset):
    with tap.plan(6, 'Список курьеров по курьерской службе'):
        user = await dataset.user()
        courier = await dataset.courier(
            courier_service_id=123,
            courier_service_name='Служебный курьер',
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_list', json={
            'courier_service_name': 'Служебный курьер',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('couriers.0')
        t.json_is('couriers.0.courier_id', courier.courier_id)
