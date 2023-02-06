async def test_list_empty(api, dataset, tap):
    with tap.plan(7):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='dc_admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_gates_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('gates', [], 'gates is empty')


async def test_list_nonempty(api, dataset, tap):
    with tap.plan(8):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='dc_admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        gates = [await dataset.gate(store=store) for _ in range(0, 5)]
        tap.ok(gates, 'полки созданы')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_gates_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('gates', 'полки в выдаче')
