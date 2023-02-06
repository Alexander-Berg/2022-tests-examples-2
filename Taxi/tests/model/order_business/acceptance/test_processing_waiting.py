async def test_waiting(tap, dataset):
    with tap.plan(9, 'Сборка заказа'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_next(tap, dataset):
    with tap.plan(10, 'Сборка заказа'):

        store = await dataset.store()
        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await order.done('complete', user=user), 'Завершение заказа')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
