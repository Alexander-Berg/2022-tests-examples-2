async def test_load_empty(tap, api):
    with tap.plan(4, 'Пустой запрос с id'):
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_load',
                        json={'order_ids': []})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('orders.0')


async def test_load(tap, api, dataset, uuid):
    with tap.plan(11, 'Запрос за ордерами'):
        order = await dataset.order(
            required=[
                {
                    'product_id': uuid(),
                    'count': 27,
                    'price': 760,
                    'price_unit': 3,
                }
            ]
        )
        tap.ok(order, 'ордер создан')

        nf_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_load',
                        json={'order_ids': [order.order_id, nf_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_hasnt('orders.1')
        t.json_hasnt('errors.1')

        t.json_is('orders.0.order_id', order.order_id)
        t.json_is('orders.0.required.0.sum',
                  '6840.00',
                  'сумма а не прайс в выдаче')

        t.json_is('errors.0.order_id', nf_id)
        t.json_is('errors.0.code', 'ER_ORDER_NOT_FOUND')
        t.json_is('errors.0.message', f'Order {nf_id} is not found')


async def test_load_company(tap, api, dataset):
    with tap.plan(8, 'Запрос за ордерами'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        order1 = await dataset.order(store=store1)
        order2 = await dataset.order(store=store2)

        t = await api(token=company1.token)
        await t.post_ok(
            'api_external_orders_load',
            json={'order_ids': [order1.order_id, order2.order_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('orders.0.order_id', order1.order_id)
        t.json_hasnt('orders.1')

        t.json_is('errors.0.order_id', order2.order_id)
        t.json_is('errors.0.code', 'ER_ORDER_NOT_FOUND')
        t.json_hasnt('errors.1')
