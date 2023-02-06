async def test_done(tap, dataset, wait_order_status, now):
    with tap.plan(9, 'сохранение пользователей в логе ордера (саджесты)'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='acceptance',
            store=store,
            acks=[user.user_id],
            approved=now(),
            required=[
                {'product_id': product.product_id, 'count': 27},
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)

        for s in suggests:
            tap.ok(await s.done(user=user), 'саджест закрыт')
            tap.ok(await s.reload(), 'перегружен')
            tap.eq(s.user_done, user.user_id, 'user_done в саджесте')

        logs = (await dataset.OrderLog.list_by_order(order))


        for l in [ l for l in logs if l.source == 'suggest_done' ]:
            tap.eq(l.user_id, user.user_id, 'пользователь в логе сохранён')
