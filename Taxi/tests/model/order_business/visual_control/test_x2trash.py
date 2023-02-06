async def test_put(tap, dataset, wait_order_status):
    with tap:
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3)
        await dataset.stock(product=apple, shelf=shelf, count=5)

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': banana.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': apple.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order, types='shelf2box', status='request',
        )
        tap.eq(len(suggests), 2, 'саджесты на проверку')

        for s in suggests:
            await s.done(count=1)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'visual_control', 'visual_control')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash', 'trash')

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 2, 'саджесты на перенос в треш')
        for s in suggests:
            await s.done(count=s.count)

        await wait_order_status(order, ('complete', 'take'), user_done=user)

        stocks_src = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=shelf.shelf_id,
        )
        tap.eq(
            sum(s.reserve for s in stocks_src), 2, 'резерв на исходной полке',
        )

        stocks_dst = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=trash.shelf_id,
        )
        tap.eq(sum(s.reserve for s in stocks_dst), 2, 'резерв на треше')
        for stock in stocks_dst:
            tap.eq(len(stock.vars['reasons']), 1, 'добавлен reason')


async def test_take_unreserve(tap, dataset, wait_order_status):
    with tap:
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3)
        await dataset.stock(product=apple, shelf=shelf, count=5)

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': banana.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': apple.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order, types='shelf2box', status='request',
        )
        tap.eq(len(suggests), 2, 'саджесты на проверку')

        for s in suggests:
            await s.done(count=1)

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'visual_control', 'visual_control')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'trash', 'trash')

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 2, 'саджесты на перенос в треш')

        for s in suggests:
            await s.done(count=s.count)

        await wait_order_status(
            order, ('complete', 'unreserve'), user_done=user,
        )

        stocks_src = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=shelf.shelf_id,
        )
        tap.eq(
            sum(s.count for s in stocks_src), 3 + 5 - 2,
            'количество на исходной полке',
        )
        tap.eq(
            sum(s.reserve for s in stocks_src), 0, 'резерв на исходной полке',
        )

        stocks_dst = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=trash.shelf_id,
        )
        tap.eq(sum(s.reserve for s in stocks_dst), 2, 'резерв на треше')

        await wait_order_status(
            order, ('complete', 'done'), user_done=user,
        )

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')
