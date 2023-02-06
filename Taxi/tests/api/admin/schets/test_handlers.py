async def test_list_handlers(tap, api, dataset):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)

        t = await api(user=user)
        await t.get_ok(
            'api_admin_schets_handlers',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('handlers')
        t.json_has('handlers.0')
