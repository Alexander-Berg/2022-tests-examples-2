async def test_study(tap, dataset, now, wait_order_status):
    with tap.plan(22, 'Учебные ордера'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, study=True)
        tap.eq(user.store_id, store.store_id, 'пользователь')
        tap.eq(user.study, True, 'пользователь-ученик')

        stock = await dataset.stock(count=10, store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            type='order',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 7,
                }
            ],
            store=store,
            study=True,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.study, True, 'Учебный заказ')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        for s in suggests:
            tap.ok(await s.done(), 'саджест закрыт')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.done(target='complete', user=user), 'Завершён')
        tap.eq(order.target, 'complete', 'ордер НЕ помечен как отменённый')
        while not order.vars('suggests_error', False):
            await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')
        tap.eq({s.type for s in suggests}, {'box2shelf', 'shelf2box'}, 'типы')
        tap.eq(order.target, 'canceled', 'ордер помечен как отменённый')
        for s in suggests:
            if s.status == 'done':
                tap.eq(s.type, 'shelf2box', 'закрытый - shelf2box')
            else:
                tap.eq(s.type, 'box2shelf', 'открытый - box2shelf')
                tap.ok(await s.done(), 'закрываем открытый')
        await wait_order_status(order, ('canceled', 'done'))

        tap.ok(await stock.reload(), 'перегружен остаток')
        tap.eq((stock.count, stock.reserve), (10, 0), 'значение в остатке')
