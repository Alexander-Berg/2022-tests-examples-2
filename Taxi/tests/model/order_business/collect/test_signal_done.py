async def test_signal(tap, dataset, wait_order_status):
    with tap.plan(19, 'прекращение ордера по сигналу'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock1 = await dataset.stock(store=store, count=45)
        tap.eq(stock1.store_id, store.store_id, 'остаток 1 создан')

        stock2 = await dataset.stock(store=store, count=56)
        tap.eq(stock2.store_id, store.store_id, 'остаток 2 создан')

        order = await dataset.order(
            type='collect',
            required=[
                {
                    'product_id': stock1.product_id,
                    'count': 23,
                },
                {
                    'product_id': stock2.product_id,
                    'count': 34,
                }
            ],
            store=store
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting_stocks'))

        stock_send = await dataset.stock(
            product_id=stock1.product_id,
            count=23,
            shelf_id=order.vars('shelf'),
            store=store,
        )
        tap.eq(
            (stock_send.product_id, stock_send.count),
            (stock1.product_id, 23),
            'остаток создан'
        )

        tap.ok(await order.signal({'type': 'collected'}), 'сигнал отправлен')
        await wait_order_status(order, ('complete', 'waiting_child_order'))

        child = await dataset.Order.load(order.vars('child_order_id'))
        tap.eq(len(child.required), 1, 'один товар в отгрузке')
        with child.required[0] as r:
            tap.eq(r.product_id, stock1.product_id, 'product_id')
            tap.eq(r.count, 23, 'count')
        tap.eq(child.store_id, store.store_id, 'дочерний ордер создан')
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'ack')
        await wait_order_status(child, ('complete', 'done'), user_done=user)

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        shelf = await dataset.Shelf.load(order.vars('shelf'))
        tap.ok(shelf, 'полка загружена')
        tap.eq(shelf.order_id, None, 'ордер у полки не назначен')
