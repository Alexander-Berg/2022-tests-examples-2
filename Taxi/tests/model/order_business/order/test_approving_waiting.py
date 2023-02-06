async def test_waiting(tap, dataset):
    with tap.plan(11, 'Подтверждение заказа'):

        order = await dataset.order(
            type = 'order',
            status='approving',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')
        tap.eq(order.approved, None, 'Время не установлено')

        tap.ok(await order.approve(), 'Заказ одобрен')
        tap.ok(order.approved, 'Время установлено')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')




async def test_waiting_no_approved(tap, dataset):
    with tap.plan(9, 'Нет подтверждения. Ждем.'):

        order = await dataset.order(
            type = 'order',
            status='approving',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')
        tap.eq(order.approved, None, 'Время не установлено')


