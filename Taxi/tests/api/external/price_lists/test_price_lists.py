import pytest


@pytest.mark.parametrize('subscribe', [False, True])
async def test_prices(api, tap, dataset, subscribe):
    with tap.plan(8 + (5 if subscribe else 0), 'Тесты списка'):
        t = await api(role='token:web.external.tokens.0')

        price = await dataset.price_list()
        tap.ok(price, 'Один ассортимент есть')

        await t.post_ok('api_external_price_lists_list',
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
        t.json_has('price_lists.0')

        t.json_like('price_lists.0.price_list_id', r'^\S+$', 'price_list_id')
        t.json_has('price_lists.0.title')

        if subscribe:
            cursor = t.res['json']['cursor']
            await t.post_ok('api_external_price_lists_list',
                            json={
                                'cursor': cursor,
                                'subscribe': subscribe,
                            },
                            desc='Второй запрос')
            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_isnt('cursor', None)
            t.json_has('price_lists')


@pytest.mark.parametrize('subscribe', [False, True])
async def test_price_items(api, tap, dataset, subscribe):
    with tap.plan(17 + (5 if subscribe else 0), 'Тесты списка'):
        t = await api(role='token:web.external.tokens.0')

        price = await dataset.price_list()
        tap.ok(price, 'Один ассортимент есть')

        price_product = await dataset.price_list_product(
            price_list=price,
            price={'store': '1.22'},
        )
        tap.ok(price_product, 'продукт в прайсе')
        tap.eq(price_product.price_list_id, price.price_list_id, 'прайс')

        await t.post_ok('api_external_price_lists_products',
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
        t.json_has('price_list_products.0')

        t.json_like(
            'price_list_products.0.price_list_id', r'^\S+$', 'price_list_id',
        )

        t.json_has('price_list_products.0.pp_id')
        t.json_has('price_list_products.0.price_list_id')
        t.json_has('price_list_products.0.product_id')
        t.json_has('price_list_products.0.price')
        t.json_has('price_list_products.0.prices')
        t.json_has('price_list_products.0.prices.0.price_type')
        t.json_has('price_list_products.0.prices.0.price')
        t.json_has('price_list_products.0.status')

        if subscribe:
            cursor = t.res['json']['cursor']
            await t.post_ok('api_external_price_lists_products',
                            json={
                                'cursor': cursor,
                                'subscribe': subscribe,
                            },
                            desc='Второй запрос')
            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_isnt('cursor', None)
            t.json_has('price_list_products')

