import pytest


@pytest.mark.parametrize('status', ['reserving', 'request'])
async def test_cancel_before_request(tap, dataset, wait_order_status, status):
    with tap.plan(9, 'Отмена до процессинга'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        stock = await dataset.stock(store=store, count=27)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        order = await dataset.order(
            type='hand_move',
            store=store,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 11,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        if status == 'reserving':
            tap.passed('Не ждём статуса reserving,begin: с него начали')
        else:
            await wait_order_status(order, (status, 'begin'))
        tap.ok(await order.cancel(), 'отменён')

        await wait_order_status(order, ('canceled', 'done'))

        tap.ok(await stock.reload(), 'перегружен остаток')
        tap.eq(
            (stock.count, stock.reserve),
            (27, 0),
            'значение в остатке не менялось'
        )


async def test_cancel(tap, dataset, wait_order_status):
    with tap.plan(12, 'Отмена в процессинге'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        stock = await dataset.stock(store=store, count=27)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            type='hand_move',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 11,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.ok(await order.cancel(), 'отменён')


        suggests = await dataset.Suggest.list_by_order(order)
        for s in suggests:
            tap.ok(await s.done(), f'Саджест {s.type} завершён')


        await wait_order_status(order, ('processing', 'switched_target'))
        await wait_order_status(order, ('canceled', 'done'), user_done=user)

        tap.ok(await stock.reload(), 'перегружен остаток')
        tap.eq(
            (stock.count, stock.reserve),
            (27, 0),
            'значение в остатке не менялось'
        )
