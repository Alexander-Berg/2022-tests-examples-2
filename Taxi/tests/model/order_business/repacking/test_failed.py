async def test_big_required(tap, dataset, wait_order_status):
    with tap.plan(9, 'более одного required'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка перефасовки создана')

        stock1 = await dataset.stock(store=store, shelf=shelf)
        tap.eq(stock1.store_id, store.store_id, 'остаток 1 создан')

        stock2 = await dataset.stock(store=store, shelf=shelf)
        tap.eq(stock2.store_id, store.store_id, 'остаток 2 создан')

        order = await dataset.order(
            type='repacking',
            store=store,
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock1.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': stock2.product_id,
                    'shelf_id': shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('reserving', 'check_required'))
        await wait_order_status(order, ('failed', 'begin'))
        tap.eq(order.problems[0].type, 'required_too_big', 'Проблема найдена')


async def test_low_product(tap, dataset, wait_order_status):
    with tap.plan(7, 'мало продуктов'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store=store)

        stock = await dataset.stock(store=store, shelf=shelf, count=1)
        tap.eq(stock.store_id, store.store_id, 'остаток 1 создан')

        order = await dataset.order(
            type='repacking',
            store=store,
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('reserving', 'check_required'))
        await wait_order_status(order, ('failed', 'begin'))
        tap.eq(order.problems[0].type, 'low', 'Проблема найдена')
