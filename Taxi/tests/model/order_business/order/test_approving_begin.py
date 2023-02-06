async def test_begin(tap, dataset):
    with tap.plan(14, 'Ожидание подтверждения заказа'):

        order = await dataset.order(
            type = 'order',
            status = 'approving',
            estatus = 'begin',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
