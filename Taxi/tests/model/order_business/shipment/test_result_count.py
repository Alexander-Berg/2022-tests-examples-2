async def test_result_count(tap, dataset, uuid, now, wait_order_status):
    with tap.plan(17, 'заполнение result_count'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store, count=7, reserve=2)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.reserve, 2, 'зарезервировано')

        stock2 = await dataset.stock(product_id=stock.product_id,
                                     store=store,
                                     count=8,
                                     shelf_id=stock.shelf_id,
                                     lot=uuid(),
                                     reserve=3)
        tap.eq(stock2.store_id, store.store_id, 'ещё остаток создан')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'разные полки')
        tap.eq(stock2.product_id, stock.product_id, 'тот же товар')
        tap.ne(stock2.stock_id, stock.stock_id, 'разные стоки')
        tap.eq(stock2.reserve, 3, 'зарезервировано')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='shipment',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 14,
                }
            ],
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.required[0].result_count, None, 'result_count нет')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            tap.eq(s.count, 10, 'сколько есть отгружаем')
            tap.ok(await s.done(count=10), 'закрыт саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(order.required[0].result_count, 10, 'result_count')

