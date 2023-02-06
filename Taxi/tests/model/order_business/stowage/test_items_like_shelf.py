async def test_item_like_shelf(tap, dataset, wait_order_status):
    with tap.plan(14, 'перекладывание экземпляра с полки на полку'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='stowage',
            required=[{'item_id': item.item_id}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        shelf = await dataset.shelf(type='parcel', store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.type, 'parcel', 'тип полки')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')

        with suggests[0] as s:
            tap.ok(
                await s.done(
                    status='error',
                    reason={'code': 'LIKE_SHELF', 'shelf_id': shelf.shelf_id},
                ),
                'Закрыто в error'
            )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.status, 'request', 'статус опять request')
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка принята')
