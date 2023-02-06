async def test_disallow(api, dataset, tap):
    with tap.plan(4, 'Дадим доступ к стору пользователю'):
        store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            store=store,
            stores_allow=[store.store_id]
        )

        user = await dataset.user(role='executer', store=store)
        with user.role as role:
            role.add_permit('stores_load', True)
            role.add_permit('users_save', True)
            role.add_permit('sub', ['supervisor'])
            t = await api(user=user)
            await t.post_ok(
                'api_admin_stores_disallow_store',
                json={
                    'user_id': supervisor.user_id,
                    'store_id': store.store_id
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        await supervisor.reload()
        tap.eq(supervisor.stores_allow, [], 'Сохранилось')


async def test_user_in_other_store(api, dataset, tap):
    with tap.plan(4, 'Есть проверка стора у юзера'):
        store = await dataset.store()
        other_store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            store=other_store,
            stores_allow=[store.store_id]
        )

        user = await dataset.user(role='executer', store=store)
        with user.role as role:
            role.add_permit('stores_load', True)
            role.add_permit('users_save', True)
            role.add_permit('sub', ['supervisor'])
            t = await api(user=user)
            await t.post_ok(
                'api_admin_stores_disallow_store',
                json={
                    'user_id': supervisor.user_id,
                    'store_id': store.store_id
                },
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        await supervisor.reload()
        tap.eq(supervisor.stores_allow, [store.store_id], 'Не сохранилось')


async def test_disallow_other_store(api, dataset, tap):
    with tap.plan(4, 'Есть проверка стора'):
        store = await dataset.store()
        other_store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            store=store,
            stores_allow=[other_store.store_id],
        )

        user = await dataset.user(role='executer', store=store)
        with user.role as role:
            role.add_permit('stores_load', True)
            role.add_permit('users_save', True)
            role.add_permit('sub', ['supervisor'])
            t = await api(user=user)
            await t.post_ok(
                'api_admin_stores_disallow_store',
                json={
                    'user_id': supervisor.user_id,
                    'store_id': other_store.store_id
                },
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        await supervisor.reload()
        tap.eq(
            supervisor.stores_allow, [other_store.store_id], 'Не сохранилось'
        )


async def test_disallow_any_role(api, dataset, tap):
    with tap.plan(4, 'Отозвать доступ можно у любой роли'):
        store = await dataset.store()
        executer = await dataset.user(
            role='executer',
            store=store,
            stores_allow=[store.store_id],
        )

        user = await dataset.user(role='executer', store=store)
        with user.role as role:
            role.add_permit('stores_load', True)
            role.add_permit('users_save', True)
            role.add_permit('sub', ['executer'])
            t = await api(user=user)
            await t.post_ok(
                'api_admin_stores_disallow_store',
                json={
                    'user_id': executer.user_id,
                    'store_id': store.store_id
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        await executer.reload()
        tap.eq(executer.stores_allow, [], 'Не сохранилось')
