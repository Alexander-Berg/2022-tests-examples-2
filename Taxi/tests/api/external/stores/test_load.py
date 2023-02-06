async def test_load(tap, api, dataset):
    with tap:
        store = await dataset.store(title='Some store', cluster='Leningrad',
                                    cost_center='Lav023')
        tap.ok(not store.messages_count, 'Messages count not set')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_external_stores_load',
                        json={'store_id': [store.store_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.0.title', 'Some store')
        t.json_is('store.0.cluster', 'Leningrad')
        t.json_is('store.0.cost_center', 'Lav023')


async def test_load_company_forbidden(tap, api, dataset):
    with tap.plan(3, 'Нельзя смотреть чужой склад'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store2 = await dataset.store(company=company2)

        t = await api(token=company1.token)

        await t.post_ok('api_external_stores_load',
                        json={'store_id': [store2.store_id]})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_load_company(tap, api, dataset):
    with tap:
        await dataset.company()
        company2 = await dataset.company()
        store2 = await dataset.store(company=company2, title='Some store',
                                     cluster='Leningrad')

        t = await api(token=company2.token)

        await t.post_ok('api_external_stores_load',
                        json={'store_id': [store2.store_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.0.title', 'Some store')
        t.json_is('store.0.cluster', 'Leningrad')
