import datetime as dt


async def test_seek(tap, dataset, api):
    with tap.plan(5):
        sample1 = await dataset.sample()
        sample2 = await dataset.sample()
        await dataset.sample()
        store = await dataset.store(
            samples_ids=[sample1.sample_id, sample2.sample_id])

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_seek',
                        json={'store_id': store.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        samples = t.res['json']['samples']

        tap.eq(
            sorted([s['sample_id'] for s in samples]),
            sorted([sample1.sample_id, sample2.sample_id]),
            'correct samples'
        )


async def test_incorrect_store(tap, api, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok('api_admin_samples_seek',
                        json={'store_id': uuid()})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('samples', [])


async def test_seek_company(tap, dataset, api):
    with tap.plan(6):
        company1 = await dataset.company()
        company2 = await dataset.company()
        sample1 = await dataset.sample(company_id=company1.company_id)
        await dataset.sample(company_id=company2.company_id)

        user = await dataset.user(role='admin',
                                  company_id=company1.company_id)
        with user.role as role:
            role.remove_permit('out_of_company')
            t = await api(user=user)

            await t.post_ok('api_admin_samples_seek', json={})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('cursor', None)
            t.json_is('samples.0.sample_id', sample1.sample_id)
            t.json_hasnt('samples.1')


async def test_seek_out_of_store(tap, dataset, api):
    with tap.plan(6):
        company = await dataset.company()
        sample1 = await dataset.sample(company_id=company.company_id)
        await dataset.sample(company_id=company.company_id)
        store = await dataset.store(company_id=company.company_id,
                                    samples_ids=[sample1.sample_id])

        user = await dataset.user(role='admin', store_id=store.store_id)
        with user.role as role:
            role.remove_permit('out_of_store')
            t = await api(user=user)

            await t.post_ok('api_admin_samples_seek', json={})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('cursor', None)
            t.json_is('samples.0.sample_id', sample1.sample_id)
            t.json_hasnt('samples.1')


async def test_seek_stores_allow(tap, dataset, api):
    with tap.plan(5):
        company = await dataset.company()
        sample1 = await dataset.sample(company_id=company.company_id)
        sample2 = await dataset.sample(company_id=company.company_id)
        await dataset.sample(company_id=company.company_id)
        store1 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample1.sample_id])
        store2 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample2.sample_id])

        user = await dataset.user(
            role='admin',
            stores_allow=[store1.store_id, store2.store_id])
        t = await api(user=user)

        await t.post_ok('api_admin_samples_seek', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        samples = t.res['json']['samples']

        tap.eq(
            sorted([s['sample_id'] for s in samples]),
            sorted([sample1.sample_id, sample2.sample_id]),
            'correct samples'
        )


async def test_seek_title(tap, dataset, api, uuid):
    with tap.plan(6):
        query = uuid()
        sample1 = await dataset.sample(title=f'{query}-{uuid()}')
        await dataset.sample()

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_seek',
                        json={'title': query.upper()})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_is('samples.0.sample_id', sample1.sample_id)
        t.json_hasnt('samples.1')


async def test_seek_product(tap, dataset, api):
    with tap.plan(6):
        product1 = await dataset.product()
        product2 = await dataset.product()
        sample1 = await dataset.sample(product_id=product1.product_id)
        await dataset.sample(product_id=product2.product_id)

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_seek',
                        json={'product_id': product1.product_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_is('samples.0.sample_id', sample1.sample_id)
        t.json_hasnt('samples.1')


async def test_seek_active(tap, dataset, api):
    with tap.plan(11):
        product = await dataset.product()
        sample1 = await dataset.sample(mode='required',
                                       product_id=product.product_id)
        sample2 = await dataset.sample(mode='optional',
                                       product_id=product.product_id)
        sample3 = await dataset.sample(mode='disabled',
                                       product_id=product.product_id)

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_seek',
                        json={'active': True,
                              'product_id': product.product_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        samples = t.res['json']['samples']

        tap.eq(
            sorted([s['sample_id'] for s in samples]),
            sorted([sample1.sample_id, sample2.sample_id]),
            'correct samples'
        )

        await t.post_ok('api_admin_samples_seek',
                        json={'active': False,
                              'product_id': product.product_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_is('samples.0.sample_id', sample3.sample_id)
        t.json_hasnt('samples.1')


async def test_seek_dttm(tap, dataset, api):
    with tap.plan(12):
        utc = dt.timezone.utc
        product = await dataset.product()
        sample1 = await dataset.sample(
            dttm_start=dt.datetime(2020, 10, 1, 11, 30, tzinfo=utc),
            dttm_till=dt.datetime(2020, 10, 2, 11, 30, tzinfo=utc),
            product_id=product.product_id)
        sample2 = await dataset.sample(
            dttm_start=dt.datetime(2020, 10, 5, 11, 30, tzinfo=utc),
            dttm_till=dt.datetime(2020, 10, 6, 11, 30, tzinfo=utc),
            product_id=product.product_id)
        await dataset.sample(product_id=product.product_id)

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_seek', json={
            'product_id': product.product_id,
            'dttm_start_from': dt.datetime(2020, 10, 1, 10, 30, tzinfo=utc),
            'dttm_start_to': dt.datetime(2020, 10, 1, 12, 30, tzinfo=utc),
            'dttm_till_from': dt.datetime(2020, 10, 2, 10, 30, tzinfo=utc),
            'dttm_till_to': dt.datetime(2020, 10, 2, 12, 30, tzinfo=utc)})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_is('samples.0.sample_id', sample1.sample_id)
        t.json_hasnt('samples.1')

        await t.post_ok('api_admin_samples_seek', json={
            'product_id': product.product_id,
            'dttm_start_from': dt.datetime(2020, 10, 5, 10, 30, tzinfo=utc),
            'dttm_start_to': dt.datetime(2020, 10, 5, 12, 30, tzinfo=utc),
            'dttm_till_from': dt.datetime(2020, 10, 6, 10, 30, tzinfo=utc),
            'dttm_till_to': dt.datetime(2020, 10, 6, 12, 30, tzinfo=utc)})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_is('samples.0.sample_id', sample2.sample_id)
        t.json_hasnt('samples.1')
