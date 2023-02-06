async def test_valid(tap, dataset, wait_order_status, uuid):
    with tap.plan(20, 'Заполнение valid из стоков'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store, valid='2022-01-02')
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.ok(stock.valid, 'с заполненным valid')


        stock2 = await dataset.stock(store=store,
                                     shelf_id=stock.shelf_id,
                                     lot=uuid(),
                                     product_id=stock.product_id)
        tap.eq(stock2.store_id, store.store_id, 'остаток создан')
        tap.ok(not stock2.valid, 'с незаполненным valid')
        tap.ne(stock2.stock_id, stock.stock_id, 'остаток новый')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'полка та же')

        stock3 = await dataset.stock(store=store,
                                     shelf_id=stock.shelf_id,
                                     lot=uuid(),
                                     product_id=stock.product_id,
                                     valid='2021-01-10')
        tap.eq(stock3.store_id, store.store_id, 'остаток создан')
        tap.ok(stock3.valid, 'с заполненным valid')
        tap.ne(stock3.stock_id, stock2.stock_id, 'остаток новый')
        tap.ne(stock3.stock_id, stock.stock_id, 'остаток новый')
        tap.eq(stock3.shelf_id, stock.shelf_id, 'полка та же')

        order = await dataset.order(
            store=store,
            type='check_product_on_shelf',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': stock.product_id,
                }
            ],
            products=[stock.product_id],
            shelves=[stock.shelf_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест есть')

        with suggests[0] as s:
            tap.eq(s.type, 'check', 'тип саджеста')
            tap.eq(s.count,
                   stock.count + stock2.count + stock3.count,
                   'количество')
            tap.eq(s.shelf_id, stock.shelf_id, 'полка')
            tap.eq(s.valid, stock3.valid, 'valid заполнен')
