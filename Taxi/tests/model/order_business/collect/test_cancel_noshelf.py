async def test_cancel(tap, dataset, wait_order_status):
    with tap.plan(8, 'отмена ещё не назначенной полки'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            type='collect',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 873,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('reserving', 'waiting_shelf'))
        await wait_order_status(order, ('reserving', 'waiting_shelf'))
        tap.ok(await order.cancel(), 'ордер отменён')
        tap.eq(order.target, 'canceled', 'отменён')
        await wait_order_status(order, ('canceled', 'done'))

