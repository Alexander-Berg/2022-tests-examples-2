# pylint: disable=unused-variable


async def test_list(api, dataset, tap):
    with tap.plan(6, 'Лог доставки'):
        store = await dataset.store()
        user  = await dataset.user(store=store)
        provider = await dataset.provider(stores=[store.store_id])

        delivery = await dataset.delivery(
            store=store,
            provider=provider,
            status='request',
        )
        await delivery.change_status('processing')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_deliveries_log',
            json={'delivery_id': delivery.delivery_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('log.0.status', 'request')
        t.json_is('log.1.status', 'processing')
        t.json_hasnt('log.2')
