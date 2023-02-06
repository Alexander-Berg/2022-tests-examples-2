async def test_load(api, dataset, tap):
    with tap.plan(
            5, "Список пользователей определенной роли c доступом к складу"
    ):
        store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            stores_allow=[store.store_id]
        )
        user = await dataset.user(
            role='executer',
            store=store,
            stores_allow=[store.store_id]
        )

        with user.role as role:
            role.add_permit('users_load', True)
            t = await api(user=user)
            await t.post_ok(
                'api_admin_users_list_allowed',
                json={
                    'role': 'supervisor',
                    'store_id': store.store_id
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('users.0.user_id', supervisor.user_id)
            t.json_hasnt('users.1')


async def test_access_error(api, dataset, tap):
    with tap.plan(3, "Проверка на склад"):
        store = await dataset.store()
        other_store = await dataset.store()
        user = await dataset.user(
            role='executer',
            store=store,
            stores_allow=[store.store_id]
        )
        with user.role as role:
            role.add_permit('users_load', True)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_users_list_allowed',
            json={
                'role': 'supervisor',
                'store_id': other_store.store_id
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
