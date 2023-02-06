
async def test_save_exists(tap, dataset, api):
    with tap.plan(6):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api()
        t.set_user(user)

        await t.post_ok('api_provider_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'car': {'number': 'A123BC123'},
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('delivery.updated', 'updated')
        t.json_has('delivery.created', 'created')
        t.json_is('delivery.car', {'number': 'A123BC123'}, 'car')


async def test_save_unexists(tap, dataset, api, uuid, now):
    with tap.plan(2, 'Создание запрещено'):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        external_id = uuid()
        plan_date   = now().date()

        t = await api(user=user)
        await t.post_ok('api_provider_deliveries_save',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'car': {'number': 'ББ11БББ'},
                            'driver': {'name': 'ААА'},
                            'plan_date': plan_date,
                        })
        t.status_is(403, diag=True)


async def test_save_done(tap, dataset, api, uuid):
    with tap.plan(2, 'Завершонную поставку редактировать нельзя'):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(
            store=store,
            provider=provider,
            status='complete',
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        dc_doc_number = uuid()

        await t.post_ok('api_provider_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'attr': {
                                'units': 1,
                                'doc_number': dc_doc_number,
                                'comment': 'тест',
                            }
                        })
        t.status_is(410, diag=True)
