async def test_waiting(tap, dataset):
    with tap.plan(9, 'Обработка заказа'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_next(tap, dataset, wait_order_status):
    with tap.plan(5, 'Обработка заказа'):

        store = await dataset.full_store()
        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

