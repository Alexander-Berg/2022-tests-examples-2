async def test_load(tap, dataset, api):
    with tap.plan(5):
        product = await dataset.product()
        sample = await dataset.sample(product=product)

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_load',
                        json={'sample_id': sample.sample_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('sample.sample_id', sample.sample_id)
        t.json_is('sample.product_id', product.product_id)


async def test_load_list(dataset, api, tap):
    with tap.plan(5):
        product1 = await dataset.product()
        product2 = await dataset.product()
        sample1 = await dataset.sample(product=product1)
        sample2 = await dataset.sample(product=product2)

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_samples_load',
            json={'sample_id': [sample1.sample_id, sample2.sample_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        samples = t.res['json']['sample']

        tap.eq(sorted([s['sample_id'] for s in samples]),
               sorted([sample1.sample_id, sample2.sample_id]),
               'Получены верные сэмплы')
        tap.eq(sorted([s['product_id'] for s in samples]),
               sorted([sample1.product_id, sample2.product_id]),
               'В сэмплах верные продукты')
