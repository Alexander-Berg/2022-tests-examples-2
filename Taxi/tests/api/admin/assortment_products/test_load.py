async def test_load(tap, api, dataset):
    with tap.plan(12):

        t = await api(role='admin')

        assortment = await dataset.assortment()
        product = await dataset.product()

        await dataset.assortment_product(
            assortment_id=assortment.assortment_id,
            product_id=product.product_id,
            max=10,
            min=0,
            cob_time=0,
            order=50,
        )
        await t.post_ok('api_admin_assortment_products_load',
                        json={'assortment_id': assortment.assortment_id,
                              'product_id': product.product_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('assortment_product.ap_id')
        t.json_has('assortment_product.created')
        t.json_has('assortment_product.updated')
        t.json_is(
            'assortment_product.assortment_id', assortment.assortment_id,
        )
        t.json_is('assortment_product.product_id', product.product_id)
        t.json_is('assortment_product.max', 10)
        t.json_is('assortment_product.min', 0)
        t.json_is('assortment_product.cob_time', 0)
        t.json_is('assortment_product.order', 50)


async def test_load_not_found(tap, api, dataset, uuid):
    with tap.plan(6):

        t = await api(role='admin')

        assortment = await dataset.assortment()
        product = await dataset.product()

        await dataset.assortment_product(
            assortment_id=assortment.assortment_id,
            product_id=product.product_id,
            max=10,
            min=0,
            cob_time=0,
            order=50,
        )
        await t.post_ok('api_admin_assortment_products_load',
                        json={'assortment_id': uuid(),
                              'product_id': product.product_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await t.post_ok('api_admin_assortment_products_load',
                        json={'assortment_id': assortment.assortment_id,
                              'product_id': uuid()})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_load_no_relation(tap, api, dataset):
    with tap.plan(4):

        t = await api(role='admin')

        assortment = await dataset.assortment()
        product = await dataset.product()

        await t.post_ok('api_admin_assortment_products_load',
                        json={'assortment_id': assortment.assortment_id,
                              'product_id': product.product_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('assortment_product', None)
