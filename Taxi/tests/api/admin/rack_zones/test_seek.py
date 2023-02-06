async def test_seek_by_title(tap, dataset, api):
    with tap.plan(5, 'поиск зон по названию'):

        store = await dataset.store()
        rack_zone1 = await dataset.rack_zone(
            store_id=store.store_id
        )
        await dataset.rack_zone(
            store_id=store.store_id
        )
        admin = await dataset.user(
            role='admin',
            store_id=store.store_id,
        )

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_rack_zones_seek',
            json={'title': rack_zone1.title}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('rack_zones.0.title', rack_zone1.title, 'зона найдена')
        t.json_hasnt('rack_zones.1', 'лишних нет')
