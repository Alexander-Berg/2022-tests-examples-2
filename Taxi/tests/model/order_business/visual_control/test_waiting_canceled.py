# hi


async def test_canceled(tap, dataset, wait_order_status):
    with tap.plan(12, 'реагируем на отмену в waiting'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        stock_banana = await dataset.stock(
            product=banana, store=store, count=300,
        )
        tap.eq(
            (stock_banana.store_id, stock_banana.count, stock_banana.reserve),
            (store.store_id, 300, 0),
            '300 бананов на складе без резерва',
        )

        stock_apple = await dataset.stock(
            product=apple, store=store, count=301,
        )
        tap.eq(
            (stock_apple.store_id, stock_apple.count, stock_apple.reserve),
            (store.store_id, 301, 0),
            '301 яблок на складе без резерва',
        )

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
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order, type='shelf2box', status='request',
        )
        tap.eq(len(suggests), 2, 'появилось 2 саджеста')

        suggests = {s.product_id: s for s in suggests}

        tap.ok(
            await suggests[banana.product_id].done(count=10),
            'нашли плохие бананы',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(order.target,  'complete', 'хотим закрыть в штатном режиме')

        order.target = 'canceled'
        await order.save()
        tap.eq(order.target, 'canceled', 'хотим отменить')

        await order.business.order_changed()

        tap.eq(order.fstatus, ('canceled', 'begin'), 'перешли в отмену')


