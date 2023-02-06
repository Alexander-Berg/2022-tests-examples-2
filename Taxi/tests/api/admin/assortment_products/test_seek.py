import pytest


@pytest.mark.parametrize('role', ('admin', 'analyst'))
async def test_seek_simple(tap, dataset, api, role):
    with tap.plan(6):
        assortment = await dataset.assortment()
        products = [await dataset.product() for _ in range(5)]

        for product in products:
            await dataset.assortment_product(
                assortment_id=assortment.assortment_id,
                product_id=product.product_id,
            )

        t = await api(role=role)

        await t.post_ok(
            'api_admin_assortment_products_seek',
            json={'assortment_id': assortment.assortment_id, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('cursor', 'cursor')
        tap.eq_ok(
            len(t.res['json']['assortment_products']),
            len(products),
            'correct number of relations',
        )
        tap.eq_ok(
            {i['assortment_id'] for i in t.res['json']['assortment_products']},
            {assortment.assortment_id},
            'correct assortment_id',
        )

async def test_seek_with_parent(tap, dataset, api):
    with tap.plan(6):
        p_assortment = await dataset.assortment()
        p_products = [await dataset.product() for _ in range(5)]
        for product in p_products:
            await dataset.assortment_product(
                assortment_id=p_assortment.assortment_id,
                product_id=product.product_id,
            )

        ch_assortment = await dataset.assortment(
            parents=[p_assortment.assortment_id],
        )
        ch_products = [await dataset.product() for _ in range(2)]
        for product in ch_products:
            await dataset.assortment_product(
                assortment_id=ch_assortment.assortment_id,
                product_id=product.product_id,
            )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortment_products_seek',
            json={'assortment_id': ch_assortment.assortment_id, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('cursor', 'cursor')
        tap.eq_ok(
            len(t.res['json']['assortment_products']),
            len(p_products) + len(ch_products),
            'correct number of relations',
        )
        tap.eq_ok(
            {i['assortment_id'] for i in t.res['json']['assortment_products']},
            {p_assortment.assortment_id, ch_assortment.assortment_id},
            'correct assortment_ids',
        )

async def test_seek_no_relations(tap, dataset, api):
    with tap.plan(5):
        assortment = await dataset.assortment()

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortment_products_seek',
            json={'assortment_id': assortment.assortment_id, 'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('assortment_products', [], 'no assortment_products')
        t.json_is('cursor', None, 'no cursor')

async def test_seek_not_found(tap, api, uuid):
    with tap.plan(3):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortment_products_seek',
            json={'assortment_id': uuid(), 'cursor': ''}
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_seek_products(tap, dataset, api):
    with tap.plan(7):
        assortment = await dataset.assortment()
        products = [await dataset.product() for _ in range(5)]

        for product in products:
            await dataset.assortment_product(
                assortment_id=assortment.assortment_id,
                product_id=product.product_id,
            )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortment_products_seek',
            json={'assortment_id': assortment.assortment_id,
                  'product_id': [p.product_id for p in products[:2]],
                  'cursor': ''}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('cursor', 'cursor')
        tap.eq_ok(
            len(t.res['json']['assortment_products']),
            2,
            'correct number of relations',
        )
        tap.eq_ok(
            {i['assortment_id'] for i in t.res['json']['assortment_products']},
            {assortment.assortment_id},
            'correct assortment_id',
        )
        tap.eq_ok(
            {i['product_id'] for i in t.res['json']['assortment_products']},
            {i.product_id for i in products[:2]},
            'Correct products for assortment',
        )
