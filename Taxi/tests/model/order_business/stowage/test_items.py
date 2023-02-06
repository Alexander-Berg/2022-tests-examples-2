async def test_items(tap, dataset, wait_order_status):
    with tap.plan(22, 'Раскладка с экземплярами'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        order = await dataset.order(
            type='stowage',
            acks=[user.user_id],
            status='reserving',
            store=store,
            required=[{'item_id': item.item_id}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            shelf = await dataset.Shelf.load(s.shelf_id)
            tap.eq(shelf.store_id, store.store_id, 'полка саджеста')
            tap.eq(shelf.type, 'parcel', 'послыки')

            tap.eq(s.type, 'box2shelf', 'операция')
            tap.eq(s.product_id, item.item_id, 'что кладём')
            tap.eq(s.count, 1, 'количество')

            tap.eq(s.conditions.max_count, True, 'Нельзя класть больше')
            tap.eq(s.conditions.need_valid, False, 'СГ не требуется')
            tap.eq(s.conditions.all, False, 'Всё надо положить')

            tap.ok(await s.done(), 'Завершён')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('shelf_type', 'parcel'),
            ),
            sort=(),
        )
        stocks = stocks.list

        tap.eq(len(stocks), 1, 'один остаток')
        with stocks[0] as s:
            tap.eq(s.shelf_type, 'parcel', 'на полке посылок')
            tap.eq(s.count, 1, 'штук')
            tap.eq(s.product_id, item.item_id, 'идентификатор посылки')
            tap.eq(s.reserve, 0, 'не резервировано')
            tap.eq(s.shelf_type, 'parcel', 'тип полки')
