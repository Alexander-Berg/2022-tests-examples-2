async def test_load(api, dataset, tap):
    with tap.plan(7, 'Получение одной записи'):
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)
        rack = await dataset.rack(store_id=store.store_id)

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_racks_load',
            json={'rack_id': rack.rack_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('rack.rack_id', rack.rack_id)
        t.json_is('rack.store_id', rack.store_id)
        t.json_is('rack.company_id', rack.company_id)
        t.json_is('rack.status', rack.status)


async def test_load_nf(tap, api, uuid):
    with tap.plan(2):
        t = await api(role='admin')

        await t.post_ok('api_admin_racks_load',
                        json={'rack_id': uuid()})

        t.status_is(403, diag=True)
