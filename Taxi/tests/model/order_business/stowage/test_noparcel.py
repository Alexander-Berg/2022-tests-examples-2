async def test_noparcel(tap, dataset, wait_order_status):
    with tap.plan(17, 'отсутствие problem при отсутствии полки parcel'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        # всё кроме parcel тут!
        for st in ('trash', 'store', 'lost', 'found', 'office', 'markdown'):
            shelf = await dataset.shelf(store=store, type=st)
            tap.eq(shelf.store_id, store.store_id, 'полка создана')
            tap.eq(shelf.type, st, st)

        order = await dataset.order(
            type='stowage',
            status='reserving',
            store=store,
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 123}],
        )
        tap.ok(order, 'ордер создан')

        if not await wait_order_status(order, ('processing', 'waiting')):
            for p in order.problems:
                tap.diag(f'problem: {p.pure_python()}')
