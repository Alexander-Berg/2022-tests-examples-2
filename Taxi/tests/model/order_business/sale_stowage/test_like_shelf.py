async def test_like_shelf(tap, dataset, wait_order_status):
    with tap.plan(15, 'неподходящая полка для LIKE_SHELF'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(tags=['freezer'], store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.tags, ['freezer'], 'теги')

        product = await dataset.product(tags=['freezer'])
        tap.eq(product.tags, ['freezer'], 'товар создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')


        wrong_shelf = await dataset.shelf(tags=[], store=store)
        tap.eq(wrong_shelf.store_id, store.store_id, 'неправильная полка')
        tap.eq(wrong_shelf.tags, [], 'теги')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': wrong_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'саджест на старую полку')


async def test_like_shelf_items(tap, dataset, wait_order_status):
    with tap.plan(18, 'неподходящая полка для LIKE_SHELF'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(tags=['freezer'],
                                    store=store,
                                    type='parcel')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.tags, ['freezer'], 'теги')
        tap.eq(shelf.type, 'parcel', 'тип полки')

        item = await dataset.item(tags=['freezer'], store=store)
        tap.eq(item.tags, ['freezer'], 'экземпляр создан')
        tap.eq(item.store_id, store.store_id, 'на складе')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'item_id': item.item_id}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')


        wrong_shelf = await dataset.shelf(tags=[], store=store, type='parcel')
        tap.eq(wrong_shelf.store_id, store.store_id, 'неправильная полка')
        tap.eq(wrong_shelf.tags, [], 'теги')
        tap.eq(wrong_shelf.type, 'parcel', 'тип полки')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': wrong_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'саджест на старую полку')


async def test_like_items_success(tap, dataset, wait_order_status):
    with tap.plan(12, 'подходящая полка для LIKE_SHELF'):
        store = await dataset.full_store()
        shelf = await dataset.shelf(
            tags=['freezer'],
            store=store,
            type='parcel'
        )
        item = await dataset.item(tags=['freezer'], store=store)

        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'item_id': item.item_id}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        correct_shelf = await dataset.shelf(
            tags=['freezer'], store=store, type='parcel')
        shelf.type = 'store'
        tap.ok(await shelf.save(), 'Изменили тип полки')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': correct_shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(
                s.shelf_id,
                correct_shelf.shelf_id,
                'саджест на новую полку'
            )
            tap.ok(await s.done(count=1), 'закрыли саджест')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)


async def test_like_shelf_office(tap, dataset, wait_order_status):
    with tap.plan(10, 'размещение на полку office через LIKE_SHELF'):
        store = await dataset.full_store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(type='office', store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        product = await dataset.product(
            vars={
                'imported': {
                   'nomenclature_type': 'consumable',
                }
            }
        )

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 77}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': shelf.shelf_id,
                    },
                ),
                'Закрыт на ошибку'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'саджест на office полку')
