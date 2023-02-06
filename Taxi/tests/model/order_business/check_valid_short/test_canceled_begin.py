async def test_begin(tap, dataset):
    with tap.plan(8, 'Срыв заказа'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='canceled',
            estatus='begin',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'unreserve', 'unreserve')

        tap.eq(len(order.problems), 0, 'Нет проблем')
