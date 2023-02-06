async def test_simple(tap, dataset, api):
    with tap.plan(8, 'Обновление тегов курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='courier_admin')
        courier = await dataset.courier(tags_updated=None)

        tags = [
            (await dataset.courier_shift_tag()).title,
            (await dataset.courier_shift_tag()).title,
        ]

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_save', json={
            'courier_id': courier.courier_id,
            'tags': tags,
            'tags_store': [store.store_id],
            'cluster_id': cluster.cluster_id,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('courier.courier_id', 'Поле courier_id')
        t.json_is('courier.tags', tags, 'tags')
        t.json_isnt('courier.tags_updated', None, 'tags_updated')
        t.json_is('courier.tags_store', [store.store_id], 'tags_store')
        t.json_is('courier.cluster_id', cluster.cluster_id, 'cluster_id')


async def test_tags_unexists(tap, dataset, api, uuid):
    with tap.plan(3, 'Обновление курьера несуществующими тегами'):
        user = await dataset.user(role='courier_admin')
        courier = await dataset.courier()

        tag_title1 = uuid()

        await dataset.courier_shift_tag(title=tag_title1)

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_save', json={
            'courier_id': courier.courier_id,
            'tags': [tag_title1, uuid()],
        })

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_tags_store_unexists(tap, dataset, api, uuid):
    with tap.plan(3, 'Привязка курьера к несуществующей лавке'):
        user = await dataset.user(role='courier_admin')
        courier = await dataset.courier()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_save', json={
            'courier_id': courier.courier_id,
            'tags_store': [uuid()],
        })

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_tags_store_error_cluster(tap, dataset, api):
    with tap.plan(4, 'Нельзя привязывать курьера к лавке в другом кластере'):
        user = await dataset.user(role='courier_admin')
        cluster1 = await dataset.cluster()
        cluster2 = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster1)
        store = await dataset.store(cluster=cluster2)

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_save', json={
            'courier_id': courier.courier_id,
            'tags_store': [store.store_id],
        })

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Store not found')


async def test_wrong_cluster(tap, dataset, api, uuid):
    with tap.plan(3, 'Обновление курьера несуществующим кластером'):
        user = await dataset.user(role='courier_admin')
        courier = await dataset.courier()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_save', json={
            'courier_id': courier.courier_id,
            'cluster_id': uuid(),
        })

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_external(tap, dataset, api):
    with tap.plan(6, 'Обновление тегов курьера по внешнему идентификатору'):
        user = await dataset.user(role='courier_admin')
        courier = await dataset.courier()

        tag1 = await dataset.courier_shift_tag()
        tag2 = await dataset.courier_shift_tag()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_save', json={
            'external_id': courier.external_id,
            'tags': [tag1.title, tag2.title],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('courier.courier_id', 'Поле courier_id')
        t.json_has('courier.tags', 'Поле tags')
        t.json_is('courier.tags', [tag1.title, tag2.title], 'Правильные теги')


async def test_access(api, tap, dataset, uuid):
    with tap.plan(3, 'Нет доступа'):
        user = await dataset.user(role='admin')
        courier = await dataset.courier()

        tag_title1 = uuid()
        tag_title2 = uuid()

        await dataset.courier_shift_tag(title=tag_title1)
        await dataset.courier_shift_tag(title=tag_title2)

        with user.role as role:
            role.remove_permit('couriers_save')

            t = await api(user=user)
            await t.post_ok('api_admin_couriers_save', json={
                'courier_id': courier.courier_id,
                'tags': [tag_title1, tag_title2],
            })

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
