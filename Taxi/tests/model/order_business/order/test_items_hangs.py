async def test_item_wrong_id(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'Зависание ордеров с посылками'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        stock = await dataset.stock(store=store, item=item, count=1)
        tap.eq(stock.store_id, store.store_id, 'Экземпляр зачислен на склад')
        tap.eq(stock.count, 1, 'количество')
        tap.eq(stock.reserve, 0, 'не зарезервирован')
        tap.eq(stock.product_id, item.item_id, 'iid')
        tap.eq(stock.shelf_type, 'parcel', 'тип полки у остатка')


        order = await dataset.order(
            store=store,
            status='reserving',
            type='order',
            acks=[user.user_id],
            required=[{'item_id': item.item_id}],
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.required[0].count, 1, 'одна посылка в требованиях')

        await wait_order_status(order, ('processing', 'begin'))
