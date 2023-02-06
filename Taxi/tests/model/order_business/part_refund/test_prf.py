async def test_prf(tap, dataset, wait_order_status):
    with tap.plan(8, 'частичный возврат'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            type='part_refund',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'stock_id': stock.stock_id,
                    'product_id': stock.product_id,
                    'shelf_id': stock.shelf_id,
                    'count': 127,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        count, reserve = stock.count, stock.reserve

        tap.ok(await stock.reload(), 'перегружен остаток')
        tap.eq(stock.count, count + 127, 'количество увеличилось')
        tap.eq(stock.reserve, reserve, 'резерв не менялся')
