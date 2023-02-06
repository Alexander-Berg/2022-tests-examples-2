async def test_begin(tap, dataset):
    with tap.plan(9, 'Начало завершения выполненного заказа'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='complete',
            estatus='begin',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'write_off', 'write_off')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
