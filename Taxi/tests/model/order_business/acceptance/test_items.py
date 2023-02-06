async def test_items(tap, dataset, wait_order_status):
    with tap.plan(21, 'приёмка с экземплярами'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        order = await dataset.order(
            type='acceptance',
            status='reserving',
            acks=[user.user_id],
            required=[
                {
                    'item_id': item.item_id,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест на раскладку есть')

        with suggests[0] as s:
            tap.eq(s.type, 'check', 'раскладка')
            tap.eq(s.product_id, item.item_id, 'что проверяем')
            tap.eq(s.count, 1, 'одна штука')
            tap.eq(s.vars('mode'), 'item', 'режим саджеста')

            tap.ok(await s.done(), 'завершён')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.eq(len(order.required), 1, 'одна запись в требованиях')
        with order.required[0] as r:
            tap.eq(r.result_count, 1, 'result_count заполнен')
            tap.eq(r.item_id, item.item_id, 'item_id остался')
            tap.eq(r.product_id, None, 'product_id пуст')


        stowage = await dataset.Order.load(order.vars('stowage_id'))
        tap.ok(stowage, 'раскладка создана')
        tap.eq(len(stowage.required), 1, 'одна запись в required')
        with stowage.required[0] as r:
            tap.eq(r.item_id, item.item_id, 'экземпляр')
            tap.eq(r.count, 1, 'количество')
            tap.eq(r.product_id, None, 'product_id')

