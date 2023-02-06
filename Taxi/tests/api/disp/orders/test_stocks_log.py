# pylint: disable=unused-variable


async def test_log(tap, dataset, api):
    with tap.plan(7, 'Лог движения остатков по заказу'):

        store = await dataset.store()
        user = await dataset.user(store=store)

        order1 = await dataset.order(store=store, type='stowage')
        order2 = await dataset.order(store=store, type='stowage')

        stock1 = await dataset.stock(order=order1, count=100)
        stock2 = await dataset.stock(order=order2, count=200)

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_stocks_log',
            json={'order_id': order1.order_id, 'cursor': None},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('cursor', r'\S')

        t.json_is('stocks_log.0.stock_id', stock1.stock_id)
        t.json_is('stocks_log.0.order_id', order1.order_id)

        t.json_hasnt('stocks_log.1')
