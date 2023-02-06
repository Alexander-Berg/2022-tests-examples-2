async def test_get_status_notfound(tap, dataset, uuid, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_external_orders_get_status', json={
            'store_id': store.store_id,
            'external_id': uuid(),
        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('details.message', 'Order not found')


async def test_get_status(tap, dataset, api):
    with tap.plan(7):
        t = await api(role='token:web.external.tokens.0')

        order = await dataset.order(status='reserving')
        tap.ok(order, 'заказ создан')

        await t.post_ok('api_external_orders_get_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
        })
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.store_id', order.store_id, 'лавка')
        t.json_is('order.external_id',
                  order.external_id,
                  'external_id в ответе')
        t.json_is('order.status', 'reserving', 'reserving')
