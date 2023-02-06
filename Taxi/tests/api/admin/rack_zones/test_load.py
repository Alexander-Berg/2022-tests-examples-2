async def test_load(api, dataset, tap):
    with tap.plan(7, 'Получение одной записи'):
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)
        rack_zone = await dataset.rack_zone(store_id=store.store_id)

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_rack_zones_load',
            json={'rack_zone_id': rack_zone.rack_zone_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('rack_zone.rack_zone_id', rack_zone.rack_zone_id)
        t.json_is('rack_zone.store_id', rack_zone.store_id)
        t.json_is('rack_zone.company_id', rack_zone.company_id)
        t.json_is('rack_zone.status', rack_zone.status)


async def test_load_nf(tap, api, uuid):
    with tap.plan(2):
        t = await api(role='admin')

        await t.post_ok('api_admin_rack_zones_load',
                        json={'rack_zone_id': uuid()})

        t.status_is(403, diag=True)
