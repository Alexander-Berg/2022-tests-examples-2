# pylint: disable=unused-variable


async def test_list(api, dataset, tap):
    with tap.plan(6, 'История поставок'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        gate = await dataset.gate(store=store, title='A1')

        provider1 = await dataset.provider(stores=[store.store_id])
        provider2 = await dataset.provider(stores=[])

        delivery1 = await dataset.delivery(store=store, provider=provider1)
        delivery2 = await dataset.delivery(store=store, provider=provider2)

        t = await api(user=user)
        await t.post_ok('api_admin_deliveries_history', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')

        deliveries = t.res['json']['deliveries']
        tap.eq(len(deliveries), 2, 'Только свои поставки')
        deliveries = dict((x['delivery_id'], x) for x in deliveries)

        tap.eq(
            deliveries[delivery1.delivery_id]['provider_id'],
            provider1.provider_id,
            'Получен'
        )

        tap.eq(
            deliveries[delivery2.delivery_id]['provider_id'],
            provider2.provider_id,
            'Получен'
        )
