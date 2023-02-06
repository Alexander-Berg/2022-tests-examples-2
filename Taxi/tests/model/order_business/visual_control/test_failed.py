from stall.model.suggest import Suggest

async def test_order_defibrillation(tap, dataset, wait_order_status):
    with tap.plan(16, 'Реанимировнаие заказа'):
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
            (stock_banana.store_id, stock_banana.count,
             stock_banana.reserve),
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

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')

        await wait_order_status(order, ('failed', 'done'))

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        tap.ok(await order.signal({'type': 'order_defibrillation'}),
               'сигнал отправлен')

        await order.business.order_changed()
        await order.reload()
        tap.eq(order.status, 'reserving', 'status reserving')
        tap.eq(order.estatus, 'begin', 'estatus begin')

        await wait_order_status(
            order,
            ('request', 'begin'),
        )

        tap.ok(await order.ack(user), 'ack')
        tap.in_ok(user.user_id, order.acks, 'попал в acks')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.status, 'processing', 'status processing')
        tap.eq(order.estatus, 'waiting', 'estatus waiting')

        suggests = await Suggest.list_by_order(
            order,
            status='request',
        )

        tap.ne(len(suggests), 0, 'Есть саджесты проверки')
