async def test_shelves_property(tap, dataset, wait_order_status, now):
    with tap.plan(15, 'Проверяем что полки остаются на месте'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(store=store)
        tap.ok(user, 'Пользователь создан')

        stock1 = await dataset.stock(store=store, count=10)
        tap.ok(stock1, 'Остаток 1')
        stock2 = await dataset.stock(store=store, count=20)
        tap.ok(stock1, 'Остаток 2')
        stock3 = await dataset.stock(store=store, count=30)
        tap.ok(stock1, 'Остаток 3')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            required=[
                {
                    'product_id': stock1.product_id,
                    'count': 1
                },
                {
                    'product_id': stock2.product_id,
                    'count': 2
                },
                {
                    'product_id': stock3.product_id,
                    'count': 3
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        await wait_order_status(order, ('request', 'begin'))
        shelf_ids = {stock1.shelf_id, stock2.shelf_id, stock3.shelf_id}
        tap.eq(set(order.shelves), shelf_ids, 'Полки на месте')

        tap.ok(await order.ack(user), 'Пользователь согласился взять заказ')
        await wait_order_status(order, ('processing', 'begin'))
        tap.eq(set(order.shelves), shelf_ids, 'Полки на месте')

        await wait_order_status(order, ('complete', 'begin'), user_done=user)
        tap.eq(set(order.shelves), shelf_ids, 'Полки на месте')
        await wait_order_status(order, ('complete', 'done'))
        tap.eq(set(order.shelves), shelf_ids, 'Полки на месте')
