from stall.model.suggest import Suggest


async def test_items(tap, dataset, wait_order_status):
    with tap.plan(23, 'работа с экземплярами: обычный workflow'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        stock = await dataset.stock(item=item, store=store, count=1)
        tap.eq(
            (stock.store_id, stock.product_id, stock.count),
            (item.store_id, item.item_id, 1),
            'Остаток создан'
        )
        stock2 = await dataset.stock(item=item, store=store, count=1)

        shelf = await dataset.shelf(store=store, type='parcel')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        shelf2 = await dataset.shelf(store=store, type='parcel')

        order = await dataset.order(
            type='hand_move',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'item_id': item.item_id,
                    'count': 1,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                    'src_shelf_id': stock2.shelf_id,
                    'dst_shelf_id': shelf2.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await Suggest.list_by_order(order)
        for s in suggests:
            await s.done()

        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.ok(await stock.reload(), 'сток перегружен')
        tap.eq(stock.count, 0, 'списано')
        tap.eq(stock.product_id, item.item_id, 'экземпляр')

        for tshelf in [shelf, shelf2]:
            stocks = await dataset.Stock.list_by_shelf(
                shelf_id=tshelf.shelf_id,
                store_id=tshelf.store_id
            )
            tap.eq(len(stocks), 1, 'один остаток появился')
            with stocks[0] as s:
                tap.eq(s.count, 1, 'остаток 1')
                tap.eq(s.shelf_type, 'parcel', 'тип полки')
                tap.eq(s.lot, order.order_id, 'lot')
                tap.eq(s.product_id, item.item_id, 'element_id')
                tap.eq(s.reserve, 0, 'нет резерва')

