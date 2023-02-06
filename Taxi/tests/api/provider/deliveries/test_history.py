# pylint: disable=unused-variable


async def test_list(api, dataset, tap):
    with tap.plan(5, 'История поставок'):
        store1 = await dataset.store()
        await dataset.gate(store=store1, title='A1')
        store2 = await dataset.store()

        provider1 = await dataset.provider(
            stores=[x.store_id for x in (store1, store2)]
        )
        provider2 = await dataset.provider(
            stores=[x.store_id for x in (store1, store2)]
        )

        delivery = await dataset.delivery(store=store2, provider=provider1)

        # Не показаны по фильтру
        await dataset.delivery(store=store1, provider=provider1)
        # Не показано не свое
        await dataset.delivery(store=store1, provider=provider2)

        user = await dataset.user(
            provider=provider1,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_deliveries_history',
            json={'store_id': store2.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')

        deliveries = t.res['json']['deliveries']
        tap.eq(len(deliveries), 1, 'Только свои поставки')
        deliveries = dict((x['delivery_id'], x) for x in deliveries)

        tap.eq(
            deliveries[delivery.delivery_id]['provider_id'],
            provider1.provider_id,
            'Получено по фильтру'
        )
