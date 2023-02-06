async def test_load(tap, api, dataset):
    with tap.plan(10):

        t = await api(role='admin')

        price_list = await dataset.price_list()
        product = await dataset.product()

        await dataset.price_list_product(
            price_list_id=price_list.price_list_id,
            product_id=product.product_id,
            price={'store': '3.14'},
        )
        await t.post_ok('api_admin_price_list_products_load',
                        json={'price_list_id': price_list.price_list_id,
                              'product_id': product.product_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('price_list_product.pp_id')
        t.json_has('price_list_product.created')
        t.json_has('price_list_product.updated')
        t.json_is(
            'price_list_product.price_list_id', price_list.price_list_id,
        )
        t.json_is('price_list_product.product_id', product.product_id)
        t.json_is('price_list_product.price.store', '3.14')
        t.json_is('price_list_product.price.markdown', None)


async def test_load_not_found(tap, api, dataset, uuid):
    with tap.plan(6):
        t = await api(role='admin')

        price_list = await dataset.price_list()
        product = await dataset.product()

        await dataset.price_list_product(
            price_list_id=price_list.price_list_id,
            product_id=product.product_id,
            price={'store': '3.14'},
        )
        await t.post_ok(
            'api_admin_price_list_products_load',
            json={'price_list_id': price_list.price_list_id,
                  'product_id': uuid()}
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await t.post_ok(
            'api_admin_price_list_products_load',
            json={'price_list_id': uuid(),
                  'product_id': product.product_id}
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_load_no_relation(tap, api, dataset):
    with tap.plan(4):

        t = await api(role='admin')

        price_list = await dataset.price_list()
        product = await dataset.product()

        await t.post_ok('api_admin_price_list_products_load',
                        json={'price_list_id': price_list.price_list_id,
                              'product_id': product.product_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list_product', None)
