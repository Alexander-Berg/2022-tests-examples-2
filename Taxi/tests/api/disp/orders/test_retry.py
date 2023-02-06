async def test_retry(tap, dataset, api):
    with tap.plan(5):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        order = await dataset.order(
            store=store,
            type='order',
            status='approving',
            estatus='begin',
        )
        tap.ok(order, 'Order created')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_disp_orders_retry', json={'order_id': order.order_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')

        # дальше должна отработать джоба
