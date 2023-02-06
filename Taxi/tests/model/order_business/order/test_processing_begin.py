async def test_begin(tap, dataset):
    with tap.plan(9, 'Сборка заказа'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'order',
            status='processing',
            estatus='begin',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
