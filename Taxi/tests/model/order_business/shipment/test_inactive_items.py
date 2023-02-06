async def test_items(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'Отгрузка помечает экземпляр неактивным'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')
        tap.eq(item.status, 'active', 'активен')

        stock = await dataset.stock(item=item, store=store)
        tap.eq(stock.store_id, store.store_id, 'экземпляр на полке')
        tap.eq(stock.shelf_type, 'parcel', 'тип полки')
        tap.eq(stock.count, 1, 'количество')

        order = await dataset.order(
            type='shipment',
            acks=[user.user_id],
            required=[
                {
                    'item_id': item.item_id,
                }
            ],
            store=store,
            approved=now(),
        )
        tap.eq(order.store_id, store.store_id, 'отгрузка создана')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.ok(await item.reload(), 'перегружен')
        tap.eq(item.status, 'inactive', 'помечен как неактивный')
