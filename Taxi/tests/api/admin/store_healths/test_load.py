async def test_happy(tap, api, dataset):
    with tap.plan(5, 'Загрузка здоровья'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')

        await dataset.store_health(
            store=store,
            recalculate=True,
        )
        with user.role as role:
            role.add_permit('store_healths_load', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_load',
                json={
                    'entity': 'cluster',
                    'entity_id': store.cluster_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('store_health', 'OK')
            t.json_is('store_health.cluster_id', store.cluster_id)


async def test_no_permit(tap, api, dataset):
    with tap.plan(3, 'Нет пермита на доступ к здоровью'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')

        await dataset.store_health(
            store=store,
            recalculate=True,
        )
        with user.role as role:
            role.add_permit('store_healths_load', False)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_load',
                json={
                    'entity': 'cluster',
                    'entity_id': store.cluster_id,
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_not_found(tap, api, dataset, uuid):
    with tap.plan(3, 'Здоровье не найдено'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')
        with user.role as role:
            role.add_permit('store_healths_load', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_load',
                json={
                    'entity': 'cluster',
                    'entity_id': uuid(),
                }
            )

            t.status_is(404, diag=True)
            t.json_is('code', 'ER_NOT_FOUND')
