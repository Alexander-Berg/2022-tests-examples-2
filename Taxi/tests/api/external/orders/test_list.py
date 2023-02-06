import pytest


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_store(tap, dataset, api, subscribe):
    with tap.plan(11, f'{"подписка" if subscribe else "проход"} по складу'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27
                }
            ]
        )
        tap.ok(order, 'ордер создан')
        tap.ok(order.required, 'required не пустой')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_list',
                        json={'cursor': None,
                              'subscribe': subscribe,
                              'store_id': order.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders.0.order_id')
        t.json_has('cursor')

        t.json_hasnt('orders.1')

        t.json_is('orders.0.order_id', order.order_id)
        t.json_is('orders.0.external_id', order.external_id)


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_company(tap, dataset, api, subscribe):
    with tap.plan(14, 'Получение списка для компании, по ее ключу'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        product = await dataset.product()

        order1   = await dataset.order(
            store=store1,
            required=[{'product_id': product.product_id, 'count': 10}]
        )
        tap.eq(order1.company_id, company1.company_id, 'company_id')

        order2   = await dataset.order(
            store=store2,
            required=[{'product_id': product.product_id, 'count': 20}]
        )
        tap.eq(order2.company_id, company2.company_id, 'company_id')

        t = await api(token=company1.token)

        tap.note('Заказ компании')
        await t.post_ok(
            'api_external_orders_list',
            json={
                'cursor': None,
                'subscribe': subscribe,
                'store_id': store1.store_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_hasnt('orders.1')
        t.json_is('orders.0.order_id', order1.order_id)
        t.json_is('orders.0.company_id', company1.company_id)

        tap.note('Заказ не от компании')
        await t.post_ok(
            'api_external_orders_list',
            json={
                'cursor': None,
                'subscribe': True,
                'store_id': store2.store_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_hasnt('orders.0')


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_common(tap, dataset, api, subscribe):
    with tap.plan(6, f'{"подписка" if subscribe else "проход"} по складу'):
        order = await dataset.order()

        tap.ok(order, 'order создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_list',
                        json={'cursor': None,
                              'subscribe': subscribe})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders.0.order_id')
        t.json_has('cursor')


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_count0(tap, dataset, api, subscribe):
    with tap.plan(7, f'{"подписка" if subscribe else "проход"} по складу'):
        product = await dataset.product()

        order = await dataset.order(
            required=[
                {
                    'product_id': product.product_id,
                    'count': 0,
                }
            ]
        )

        tap.ok(order, 'order создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_list',
            json={
                'cursor': None,
                'subscribe': subscribe,
                'store_id': order.store_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders.0.order_id')
        t.json_is('orders.0.required.0.count', 0)
        t.json_has('cursor')


@pytest.mark.parametrize('product_attrs, expected', [
    (
        {'weight': 22, },
        {'sum': None, 'weight': 22, },
    ),
    (
        {'weight': 22, 'price_unit': 11, 'price': 100, },
        {'sum': "200.00", 'weight': 22, },
    ),
    (
        {'weight': 22, 'price_unit': 44, 'price': 222.22, },
        {'sum': "111.11", 'weight': 22, },
    ),
    (
        {'weight': 10, 'price_unit': 1, },
        {'sum': None, 'weight': 10, },
    ),
])
async def test_list_weight_product(tap, dataset, api, product_attrs, expected):
    with tap.plan(8, 'Поля, отдаваемые в external  ручке'):
        product = await dataset.product()

        order = await dataset.order(
            required=[
                {
                    'product_id': product.product_id,
                    **product_attrs,
                }
            ]
        )

        tap.ok(order, 'order создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_list',
            json={
                'cursor': None,
                'subscribe': True,
                'store_id': order.store_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('orders.0.order_id', order.order_id)
        t.json_is('orders.0.required.0.product_id', product.product_id)
        for key, value in expected.items():
            t.json_is(f'orders.0.required.0.{key}', value)
