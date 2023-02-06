async def test_seek_by_title(tap, dataset, api):
    with tap.plan(5, 'поиск по названию'):

        store = await dataset.store()
        rack1 = await dataset.rack(
            store_id=store.store_id
        )
        await dataset.rack(
            store_id=store.store_id
        )
        admin = await dataset.user(
            role='admin',
            store_id=store.store_id,
        )

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_racks_seek',
            json={'title': rack1.title}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('racks.0.title', rack1.title, 'стеллаж найден')
        t.json_hasnt('racks.1', 'лишних нет')
