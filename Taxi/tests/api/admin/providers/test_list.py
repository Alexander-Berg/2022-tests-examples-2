# pylint: disable=unused-variable


async def test_list_empty(api, dataset, tap):
    with tap.plan(4):
        store   = await dataset.store()
        user = await dataset.user(store=store)

        providers = [await dataset.provider() for _ in range(0, 5)]

        t = await api(user=user)
        await t.post_ok('api_admin_providers_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('providers', [], 'providers is empty')


async def test_list_nonempty(api, dataset, tap):
    with tap.plan(4):
        store   = await dataset.store()
        user    = await dataset.user(store=store)

        providers = [
            await dataset.provider(
                stores=[store.store_id]
            ) for _ in range(0, 5)
        ]

        t = await api(user=user)

        await t.post_ok('api_admin_providers_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('providers.4', 'список получен')


async def test_filter(api, dataset, tap):
    with tap.plan(5):
        store   = await dataset.store()
        user    = await dataset.user(store=store)

        provider1 = await dataset.provider(stores=[store.store_id], title="AAA")
        provider2 = await dataset.provider(stores=[store.store_id], title="BBB")

        t = await api(user=user)

        await t.post_ok('api_admin_providers_list', json={'title': 'A'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is(
            'providers.0.title',
            provider1.title,
            'Поставщик с нужным именем'
        )
        t.json_hasnt('providers.1', 'Только подходящие')
