async def test_se(tap, dataset, wait_order_status):
    with tap.plan(17, 'Резолвинг саджестов'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        office = await dataset.shelf(store=store, type='office')
        tap.eq(office.store_id, store.store_id, 'офис полка создана')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='reserving',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 123}],
        )
        tap.ok(order, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))


        with (await dataset.Suggest.list_by_order(order))[0] as s:
            shelf_id = s.shelf_id
            tap.eq(s.product_id, product.product_id, 'товар в саджесте')
            tap.ok(
                await s.done('error', reason={'code': 'SHELF_IS_FULL'}),
                'закрыли полка полная',
            )

        await wait_order_status(order, ('processing', 'waiting'))
        with (await dataset.Suggest.list_by_order(order))[0] as s:
            tap.ne(s.shelf_id, shelf_id, 'другая полка')
            tap.ok(
                await s.done('error', reason={'code': 'LIKE_SHELF',
                                              'shelf_id': office.shelf_id}),
                'закрыли указанием на офисную полку',
            )


        await wait_order_status(order, ('processing', 'waiting'))
        with (await dataset.Suggest.list_by_order(order))[0] as s:
            tap.ne(s.shelf_id, office.shelf_id, 'НЕ на полку офис')
            tap.ok(
                await s.done('error', reason={'code': 'LIKE_SHELF',
                                              'shelf_id': shelf.shelf_id}),
                'закрыли указанием на полку',
            )

        await wait_order_status(order, ('processing', 'waiting'))
        with (await dataset.Suggest.list_by_order(order))[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'На полку показывает')
