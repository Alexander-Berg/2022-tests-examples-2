
async def test_load_nf(tap, api, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok('api_provider_deliveries_load',
                        json={'delivery_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа к не нашим полкам')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(4):

        store = await dataset.store()
        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_deliveries_load',
            json={'delivery_id': delivery.delivery_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'полка получена')
        t.json_is('delivery.delivery_id', delivery.delivery_id, 'идентификатор')


async def test_load_multiple(tap, api, dataset):
    with tap.plan(5):
        store = await dataset.store()
        provider = await dataset.provider(stores=[store.store_id])
        delivery1 = await dataset.delivery(store=store, provider=provider)
        delivery2 = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_deliveries_load',
            json={
                'delivery_id': [
                    delivery1.delivery_id,
                    delivery2.delivery_id,
                ]
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('delivery', 'есть в выдаче')
        res = t.res['json']['delivery']
        tap.eq_ok(
            sorted([res[0]['delivery_id'], res[1]['delivery_id']]),
            sorted([
                delivery1.delivery_id,
                delivery2.delivery_id
            ]),
            'Пришли правильные объекты'
        )


async def test_load_multiple_fail(tap, api, dataset, uuid):
    with tap.plan(2):
        store = await dataset.store()
        provider = await dataset.provider(stores=[store.store_id])
        delivery1 = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_deliveries_load',
            json={
                'delivery_id': [
                    delivery1.delivery_id,
                    uuid(),
                ]
            },
        )
        t.status_is(403, diag=True)
