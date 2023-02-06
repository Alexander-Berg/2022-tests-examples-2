import pytest


async def test_save_exists(tap, dataset, api):
    with tap.plan(12):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        gate = await dataset.gate(store=store, title='медвед')
        tap.ok(gate, 'полка создана')
        tap.eq(gate.store_id, store.store_id, 'на складе')
        tap.eq(gate.title, 'медвед', 'название полки')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_gates_save',
                        json={
                            'gate_id': gate.gate_id,
                            'title': 'привет'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('gate.updated', 'updated')
        t.json_has('gate.created', 'created')
        t.json_is('gate.title', 'привет', 'title')


async def test_save_unexists(tap, dataset, api, uuid):
    with tap.plan(12):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        external_id = uuid()

        await t.post_ok('api_admin_gates_save',
                        json={
                            'external_id': external_id,
                            'title': 'привет'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('gate.updated', 'updated')
        t.json_has('gate.created', 'created')
        t.json_is('gate.title', 'привет', 'title')
        t.json_is('gate.external_id', external_id, 'идентификатор')
        t.json_is('gate.status', 'active', 'статус "активный"')
        t.json_is('gate.user_id', user.user_id)


@pytest.mark.parametrize('role', ['store_admin'])
async def test_save_prohibited(tap, dataset, api, role):
    with tap.plan(3):
        store = await dataset.store()
        gate = await dataset.gate(store=store, title='медвед')

        t = await api(role=role)

        await t.post_ok('api_admin_gates_save',
                        json={
                            'gate_id': gate.gate_id,
                            'title': 'привет',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_save_user_id(tap, dataset, api):
    with tap:
        store = await dataset.store()
        gate = await dataset.gate(store=store, title='медвед')

        t = await api(role='admin')

        await t.post_ok('api_admin_gates_save',
                        json={
                            'gate_id': gate.gate_id,
                            'title': 'привет',
                            'user_id': 'hello',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('gate.user_id', 'hello')
