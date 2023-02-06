async def test_done_stocks(tap, dataset, wait_order_status, uuid):
    with tap.plan(13):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        order = await dataset.order(
            type='collect',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting_stocks'))
        await wait_order_status(order, ('processing', 'waiting_stocks'))

        tap.ok(order.vars('shelf'), 'полка назначена')
        shelf = await dataset.Shelf.load(order.vars('shelf'))
        tap.eq(shelf.store_id, store.store_id, 'полка выбрана')
        tap.eq(shelf.type, 'collection', 'тип полки')

        stock = await dataset.stock(
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            lot=uuid(),
            count=17,
            store=store,
        )
        tap.eq(
            (stock.store_id, stock.shelf_id, stock.product_id, stock.count),
            (store.store_id, shelf.shelf_id, product.product_id, 17),
            'остаток создан'
        )

        await wait_order_status(order, ('processing', 'waiting_stocks'))

        stock2 = await dataset.stock(
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            lot=uuid(),
            count=10,
            store=store,
        )
        tap.eq(
            (
                stock2.store_id,
                stock2.shelf_id,
                stock2.product_id,
                stock2.count
            ),
            (store.store_id, shelf.shelf_id, product.product_id, 10),
            'остаток создан'
        )
        tap.ne(stock2.stock_id, stock.stock_id, 'разные стоки')


        await wait_order_status(order, ('complete', 'begin'))
