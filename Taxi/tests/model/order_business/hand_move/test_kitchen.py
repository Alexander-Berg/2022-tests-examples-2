from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def test_hand_move_kitchen(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals,too-many-statements
    with tap.plan(29, 'проверяем корректность работы с компонентными полками'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        product = await dataset.product(quants=100)

        shelf = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store)
        kshelf = await dataset.shelf(store=store, type='kitchen_components')
        kshelf2 = await dataset.shelf(store=store, type='kitchen_components')

        await dataset.stock(
            store=store, shelf=shelf, product=product, count=10,
        )
        await dataset.stock(
            store=store, shelf=kshelf, product=product, count=100,
        )

        order = await dataset.order(
            store=store,
            type='hand_move',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': kshelf2.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': kshelf.shelf_id,
                },
            ],
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].type, 'shelf2box', 'нужный тип саджеста')
        tap.eq(suggests[0].shelf_id, shelf.shelf_id, 'нужная полка')
        tap.eq(suggests[0].count, 2, '2 пачки')
        for s in suggests:
            await s.done()
        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )

        await wait_order_status(order, ('complete', 'begin'), user_done=user)
        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'добавилось еще 2 саджеста')
        sug1_0 = [s for s in suggests if s.shelf_id == kshelf.shelf_id][0]
        sug1_1 = [s for s in suggests if s.shelf_id == kshelf2.shelf_id][0]
        tap.eq(sug1_0.type, 'box2shelf', 'нужный тип саджеста')
        tap.eq(sug1_0.shelf_id, kshelf.shelf_id, 'нужная полка')
        tap.eq(sug1_0.count, 1, '1 пачка')
        tap.eq(sug1_1.type, 'box2shelf', 'нужный тип саджеста')
        tap.eq(sug1_1.shelf_id, kshelf2.shelf_id, 'нужная полка')
        tap.eq(sug1_1.count, 1, '1 пачка')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        async def sum_stock_by_shelf(sh):
            return sum(
                s.count
                for s in await Stock.list_by_shelf(
                    shelf_id=sh.shelf_id,
                    store_id=store.store_id,
                )
            )

        sum_cnt_shelf = await sum_stock_by_shelf(shelf)
        sum_cnt_kshelf = await sum_stock_by_shelf(kshelf)
        sum_cnt_kshelf2 = await sum_stock_by_shelf(kshelf2)

        tap.eq(sum_cnt_shelf, 8, '10-1-1=8')
        tap.eq(sum_cnt_kshelf, 200, '100+100=200')
        tap.eq(sum_cnt_kshelf2, 100, '0+100=100')

        await dataset.stock(
            store=store, shelf=shelf2, product=product, count=10,
        )

        order = await dataset.order(
            store=store,
            type='hand_move',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': shelf2.shelf_id,
                },
            ],
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await Suggest.list_by_order(order)
        tap.eq(suggests[0].type, 'shelf2box', 'нужный тип саджеста')
        tap.eq(suggests[0].shelf_id, shelf.shelf_id, 'нужная полка')
        tap.eq(suggests[0].count, 1, '1 пачка')
        for s in suggests:
            await s.done()
        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )

        await wait_order_status(order, ('complete', 'begin'), user_done=user)
        suggests = await Suggest.list_by_order(order)
        box2shelf_suggest = [s for s in suggests if s.type == 'box2shelf'][0]
        tap.eq(box2shelf_suggest.shelf_id, shelf2.shelf_id, 'нужная полка')
        tap.eq(box2shelf_suggest.count, 1, '1 пачка')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        sum_cnt_shelf = await sum_stock_by_shelf(shelf)
        sum_cnt_shelf2 = await sum_stock_by_shelf(shelf2)

        tap.eq(sum_cnt_shelf, 7, '8-1=7')
        tap.eq(sum_cnt_shelf2, 11, '10+1=11')

        order = await dataset.order(
            store=store,
            type='hand_move',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': shelf2.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': kshelf.shelf_id,
                },
            ],
        )
        await wait_order_status(order, ('failed', 'begin'))
        await order.reload()
        tap.ok(
            [
                p
                for p in order.problems
                if p.type == 'move_diff_shelf_types'
            ],
            'Есть перемещения с различными типами src/dst-полок'
        )
