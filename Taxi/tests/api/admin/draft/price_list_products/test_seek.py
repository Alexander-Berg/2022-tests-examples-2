async def test_has_relations(tap, dataset, api):
    with tap.plan(5):
        price_list = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]

        for product in products:
            await dataset.draft_price_list_product(
                price_list_id=price_list.price_list_id,
                product_id=product.product_id,
            )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_draft_price_list_products_seek',
            json={'price_list_id': price_list.price_list_id, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('cursor', 'cursor')

        tap.eq_ok(
            {i['product_id'] for i in t.res['json']['price_list_products']},
            {i.product_id for i in products},
            'Correct products for price-list',
        )


async def test_no_relations(tap, api, uuid):
    with tap.plan(2):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_draft_price_list_products_seek',
            json={'price_list_id': uuid(), 'cursor': ''},
        )

        t.status_is(403, diag=True)


async def test_seek_products(tap, dataset, api):
    with tap.plan(5):
        price_list = await dataset.draft_price_list()
        products = [await dataset.product() for _ in range(5)]

        for product in products:
            await dataset.draft_price_list_product(
                price_list_id=price_list.price_list_id,
                product_id=product.product_id,
            )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_draft_price_list_products_seek',
            json={'price_list_id': price_list.price_list_id,
                  'product_id': [p.product_id for p in products[:2]],
                  'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('cursor', 'cursor')

        tap.eq_ok(
            {i['product_id'] for i in t.res['json']['price_list_products']},
            {i.product_id for i in products[:2]},
            'Correct products for price-list',
        )
