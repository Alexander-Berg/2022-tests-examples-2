async def test_items(tap, dataset, now, wait_order_status):
    # pylint: disable=too-many-statements
    with tap.plan(41, 'Работа с экземплярами'):
        store = await dataset.full_store()
        tap.ok(store, f'склад создан {store.store_id}')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, f'экземпляр {item.item_id}')

        stock = await dataset.stock(store=store, item=item, count=1)
        tap.eq(stock.store_id, store.store_id, 'остаток')
        tap.eq(stock.product_id, item.item_id, 'идентификатор')
        tap.eq(stock.shelf_type, 'parcel', 'тип полки')
        tap.eq((stock.count, stock.reserve), (1, 0), 'количество')

        order = await dataset.order(
            type='order',
            store=store,
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=[{'item_id': item.item_id}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.ok(await item.reload(), 'экземпляр перегружен')
        tap.eq(item.status, 'inactive', 'он неактивен')


        tap.ok(await stock.reload(), 'остаток перегружен')
        tap.eq(stock.count, 0, 'на остатке нет ничего')

        tap.ok(await order.cancel(), 'отменяем ордер')
        await wait_order_status(order, ('canceled', 'done'), user_done=user)

        refund = await dataset.Order.load(order.vars('child_order_id'))
        tap.eq(refund.store_id, store.store_id, 'refund создан')

        tap.eq(len(refund.required), 1, 'одна запись в required')
        with refund.required[0] as r:
            tap.eq(r.stock_id, stock.stock_id, 'сток')
            tap.eq(r.item_id, item.item_id, 'экземпляр')
            tap.eq(r.count, 1, 'количество')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user), 'ack')
        await wait_order_status(refund, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(refund)
        tap.eq(len(suggests), 1, 'один саджест раскладки')
        with suggests[0] as s:
            tap.eq(s.product_id, item.item_id, 'экземпляр')
            tap.eq(s.shelf_id, stock.shelf_id, 'полка')
            tap.eq(s.count, 1, 'количество')
            tap.eq(s.vars('mode'), 'item', 'режим')
            tap.ok(await s.done(count=0), 'закрыли саджест')
            tap.ok(await s.reload(), 'саджест перегружен')
            tap.eq(s.result_count, 0, 'закрыто на нуль')

        await wait_order_status(refund, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(refund)
        tap.eq(len(suggests), 1, 'один саджест и остался')
        with suggests[0] as s:
            tap.eq(s.product_id, item.item_id, 'экземпляр')
            tap.eq(s.shelf_id, stock.shelf_id, 'полка')
            tap.eq(s.status, 'done', 'он закрыт')

        await wait_order_status(refund, ('complete', 'done'), user_done=user)

        tap.ok(await stock.reload(), 'остаток перегружен')
        tap.eq(stock.count, 0, 'на остаток НЕ вернули')

        tap.ok(await item.reload(), 'экземпляр перегружен')
        tap.eq(item.status, 'inactive', 'Остался неактивен')

