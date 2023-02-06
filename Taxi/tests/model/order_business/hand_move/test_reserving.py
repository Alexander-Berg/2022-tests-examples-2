async def test_reserving(tap, dataset, wait_order_status, now):
    with tap.plan(18, 'Резервирование и саджесты'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        src_shelf = await dataset.shelf(store=store)
        tap.eq(src_shelf.store_id, store.store_id, 'Полка из')

        dst_shelf = await dataset.shelf(store=store)
        tap.eq(dst_shelf.store_id, store.store_id, 'Полка куда')


        stock = await dataset.stock(
            store=store,
            product_id=product.product_id,
            count=123,
            shelf=src_shelf
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.product_id, product.product_id, 'товар')
        tap.eq(stock.shelf_id, src_shelf.shelf_id, f'полка {stock.shelf_id}')
        tap.eq(stock.reserve, 0, 'нет резервирования')
        tap.eq(stock.count, 123, 'количество')


        order = await dataset.order(
            store=store,
            type='hand_move',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 17,
                    'src_shelf_id': src_shelf.shelf_id,
                    'dst_shelf_id': dst_shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'begin'))


        stocks = await dataset.Stock.list_by_order(order)
        tap.ok(stocks, 'остатки получены')
        tap.eq(len(stocks), 1, 'один остаток')
        with stocks[0] as s:
            tap.eq(s.reserves.get(order.order_id), 17, 'количество резерва')


        suggests = await dataset.Suggest.list_by_order(order)
        suggests.sort(key=lambda x: x.order)

        tap.ok(suggests, 'саджесты получены')
        tap.eq(len(suggests), 1, 'количество')

        with suggests[0] as s:
            tap.eq(s.type, 'shelf2box', 'взять с полки')
