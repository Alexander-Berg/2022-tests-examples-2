
async def test_status(tap, dataset, api):
    with tap.plan(5, 'Смена статуса'):
        store       = await dataset.store()
        user        = await dataset.user(store=store)
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(store=store, provider=provider)

        tap.eq(delivery.status, 'request', 'Поставка создана')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_deliveries_status',
            json={
                'delivery_id': delivery.delivery_id,
                'status': 'processing',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('delivery.status', 'processing')


async def test_status_done(tap, dataset, api):
    with tap.plan(4, 'Смена статуса'):
        store       = await dataset.store()
        user        = await dataset.user(store=store)
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(
            store=store,
            provider=provider,
            status='complete',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_deliveries_status',
            json={
                'delivery_id': delivery.delivery_id,
                'status': 'processing',
            }
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')
        t.json_is('message', 'Already done')
