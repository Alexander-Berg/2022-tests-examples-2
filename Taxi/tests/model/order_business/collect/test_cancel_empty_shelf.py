async def test_cancel(tap, dataset, wait_order_status):
    with tap.plan(13, 'Отмена заказа при пустой полке'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        order = await dataset.order(
            store=store,
            type='collect',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 128,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting_stocks'))

        shelf = await dataset.Shelf.load(order.vars('shelf'))
        tap.eq(shelf.store_id, store.store_id, 'полка назначена')
        tap.eq(shelf.order_id, order.order_id, 'order_id в полке')
        tap.eq(shelf.type, 'collection', 'тип полки - коллекция')

        tap.ok(await order.cancel(), 'отменяем')
        tap.eq(order.target, 'canceled', 'target')
        await wait_order_status(order, ('canceled', 'done'))
        tap.eq(
            order.vars('acceptance_id', None),
            None,
            'не создан дочерний ордер'
        )

        tap.ok(await shelf.reload(), 'полка перегружена')
        tap.eq(shelf.order_id, None, 'ордер уже не назначен')
