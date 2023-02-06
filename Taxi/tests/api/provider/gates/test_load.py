# pylint: disable=


async def test_load(api, dataset, tap):
    with tap.plan(4, 'Ворота'):

        store = await dataset.store()
        gate = await dataset.gate(store=store, title='A1')
        provider = await dataset.provider(stores=[store.store_id])
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gates_load',
            json={'gate_id': gate.gate_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('gate.gate_id', gate.gate_id)


async def test_load_multiple(api, dataset, tap):
    with tap.plan(5, 'Список ворот'):

        store1 = await dataset.store()
        gate1 = await dataset.gate(store=store1, title='A1')

        store2 = await dataset.store()
        gate2 = await dataset.gate(store=store2, title='B1')

        store3 = await dataset.store()
        gate3 = await dataset.gate(store=store3, title='C1', status='removed')

        provider = await dataset.provider(
            stores=[store1.store_id, store3.store_id]
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gates_load',
            json={'gate_id': [gate1.gate_id, gate2.gate_id, gate3.gate_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('gate.0.gate_id', gate1.gate_id)
        t.json_hasnt('gate_id.1', 'Только подходящие ворота')


async def test_load_not_found(api, dataset, tap, uuid):
    with tap.plan(3, 'Нет такого склада'):

        provider = await dataset.provider()
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gates_load',
            json={'gate_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
