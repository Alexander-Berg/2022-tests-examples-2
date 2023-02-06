import pytest


@pytest.mark.parametrize('subscribe', [False, True])
async def test_assortments(api, tap, dataset, subscribe):
    with tap.plan(11 + (5 if subscribe else 0), 'Тесты списка'):
        t = await api(role='token:web.external.tokens.0')

        assortment = await dataset.assortment()
        tap.ok(assortment, 'Один ассортимент есть')

        await t.post_ok('api_external_assortments_list',
                        json={
                            'cursor': None,
                            'subscribe': subscribe,
                        })

        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        if subscribe:
            t.json_isnt('cursor', None)
        else:
            t.json_has('cursor')
        t.json_has('assortments.0')

        t.json_like('assortments.0.assortment_id', r'^\S+$', 'assortment_id')
        t.json_has('assortments.0.title')
        t.json_has('assortments.0.parent_id')
        t.json_has('assortments.0.parents')
        t.json_like('assortments.0.status', r'^(active|disabled|removed)$')

        if subscribe:
            cursor = t.res['json']['cursor']
            await t.post_ok('api_external_assortments_list',
                            json={
                                'cursor': cursor,
                                'subscribe': subscribe,
                            },
                            desc='Второй запрос')
            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_isnt('cursor', None)
            t.json_has('assortments')


@pytest.mark.parametrize('subscribe', [False, True])
async def test_assortment_products(api, tap, dataset, subscribe):
    with tap.plan(15 + (5 if subscribe else 0), 'Тесты списка'):
        t = await api(role='token:web.external.tokens.0')

        assortment = await dataset.assortment()
        tap.ok(assortment, 'Один ассортимент есть')

        assortment_product = await dataset.assortment_product(
            assortment_id=assortment.assortment_id)
        tap.ok(assortment_product, 'продукт создан')
        tap.eq(assortment_product.assortment_id,
               assortment.assortment_id,
               'assortment_id')

        await t.post_ok('api_external_assortments_products',
                        json={
                            'cursor': None,
                            'subscribe': subscribe,
                        })

        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        if subscribe:
            t.json_isnt('cursor', None)
        else:
            t.json_has('cursor')
        t.json_has('assortment_products.0')

        t.json_has('assortment_products.0.ap_id')
        t.json_like(
            'assortment_products.0.status', r'^(active|removed|excluded)$'
        )
        t.json_has('assortment_products.0.assortment_id')
        t.json_has('assortment_products.0.product_id')
        t.json_has('assortment_products.0.min')
        t.json_has('assortment_products.0.max')
        t.json_has('assortment_products.0.cob_time')


        if subscribe:
            cursor = t.res['json']['cursor']
            await t.post_ok('api_external_assortments_products',
                            json={
                                'cursor': cursor,
                                'subscribe': subscribe,
                            },
                            desc='Второй запрос')
            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_isnt('cursor', None)
            t.json_has('assortment_products')
