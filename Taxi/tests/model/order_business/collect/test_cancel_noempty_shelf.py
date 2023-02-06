async def test_cancel(tap, dataset, wait_order_status):
    with tap.plan(26, 'Отмена заказа при пустой полке'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь сгенерирован')

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


        stock = await dataset.stock(shelf=shelf, product=product, count=7)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        tap.ok(await order.cancel(), 'отменяем')
        tap.eq(order.target, 'canceled', 'target')
        await wait_order_status(order, ('canceled', 'waiting_acceptance_done'))
        tap.ok(order.vars('acceptance_id'), 'создан дочерний ордер')


        acceptance = await dataset.Order.load(order.vars('acceptance_id'))
        tap.eq(acceptance.store_id, store.store_id, 'ордер раскладки загружен')
        tap.eq(acceptance.source, 'internal', 'source')
        tap.eq(len(acceptance.required), 1, 'количество required')
        with acceptance.required[0] as r:
            tap.eq(r.product_id, product.product_id, 'product_id')
            tap.eq(r.count, 7, 'count')
            tap.eq(r.shelf_id, shelf.shelf_id, 'shelf_id')

        await wait_order_status(acceptance, ('request', 'waiting'))
        tap.ok(await acceptance.ack(user), 'ack')
        tap.in_ok(user.user_id, acceptance.acks, 'попал в acks')
        await wait_order_status(
            acceptance,
            ('complete', 'done'),
            user_done=user
        )

        await wait_order_status(order, ('canceled', 'done'))

        tap.ok(await shelf.reload(), 'полка перегружена')
        tap.eq(shelf.order_id, None, 'ордер уже не назначен')
