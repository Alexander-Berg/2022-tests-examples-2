async def test_reserving(tap, dataset, wait_order_status):
    with tap.plan(13, 'Резервирование'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf = await dataset.shelf(
            store=store,
            type='repacking'
        )
        tap.eq(shelf.store_id, store.store_id, 'Полка из')

        stock = await dataset.stock(
            store=store,
            product_id=product.product_id,
            count=123,
            shelf=shelf
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.product_id, product.product_id, 'товар')
        tap.eq(stock.reserve, 0, 'нет резервирования')
        tap.eq(stock.count, 123, 'количество')

        order = await dataset.order(
            store=store,
            type='repacking',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            shelf_id=shelf.shelf_id,
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('reserving', 'suggests_generate'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.ok(stocks, 'остатки получены')
        tap.eq(len(stocks), 1, 'один остаток')
        with stocks[0] as s:
            tap.eq(s.reserves.get(order.order_id), 123, 'количество резерва')
