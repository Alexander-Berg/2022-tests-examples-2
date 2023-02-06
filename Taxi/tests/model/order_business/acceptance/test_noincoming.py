async def test_noincoming(tap, dataset, wait_order_status):
    with tap.plan(10):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store=store, type='collection')
        tap.eq(
            (shelf.store_id, shelf.type),
            (store.store_id, 'collection'),
            'полка создана'
        )

        parent = await dataset.order(store=store)
        tap.eq(parent.store_id, store.store_id, 'родитель создан')

        order = await dataset.order(
            store=store,
            type='acceptance',
            acks=[user.user_id],
            approved=True,
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf.shelf_id,
                    'count': 17,
                }
            ],
            parent=[parent.order_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка в саджесте')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
