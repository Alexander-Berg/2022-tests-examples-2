async def test_get_shelf(tap, dataset, wait_order_status):
    with tap.plan(14, 'закрепление ордера за полкой'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='collect',
            required=[
                {'product_id': product.product_id, 'count': 123},
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('reserving', 'waiting_shelf'))
        await wait_order_status(order, ('reserving', 'waiting_shelf'))

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.problems, 'проблемы есть')

        shelf = await dataset.shelf(store=store, type='collection')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        await wait_order_status(order, ('processing', 'begin'))

        tap.ok(await shelf.reload(), 'полка перегружена')
        tap.eq(shelf.order_id, order.order_id, 'ордер к полке прикреплён')
        tap.eq(order.vars('shelf'), shelf.shelf_id, 'полка в ордере прописана')

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(not order.problems, 'проблем нет')
