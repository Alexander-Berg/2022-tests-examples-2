async def test_load(tap, api, dataset):
    with tap.plan(4):

        provider = await dataset.provider(stores=[])

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_providers_load',
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'полка получена')
        t.json_is('provider.provider_id', user.provider_id, 'Только свой')
