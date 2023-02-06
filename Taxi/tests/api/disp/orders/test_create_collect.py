async def test_create_collect(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(14):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'collect',
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 123,
                    }
                ]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order.order_id')

        order = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.type, 'collect', 'тип')
        tap.eq(len(order.required), 1, 'required')
        with order.required[0] as r:
            tap.eq(r.product_id, product.product_id, 'product_id')
            tap.eq(r.count, 123, 'count')

        await wait_order_status(order, ('processing', 'begin'))
        tap.ok(order.vars('shelf'), 'полка закреплена за ордером')
