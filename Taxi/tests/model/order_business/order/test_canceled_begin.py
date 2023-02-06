from stall.model.order import Order


async def test_begin(tap, dataset):
    with tap.plan(10, 'Отмена заказа'):
        store = await dataset.store()

        request = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='reserve',
        )
        tap.ok(request, 'Заказ создан')

        request.rehash(status='canceled', estatus='begin')
        tap.ok(await request.save(), 'Заказ переведен в статус')

        order = await Order.load(request.order_id)
        tap.ok(request, 'Заказ получен')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'unreserve', 'unreserve')

        tap.eq(len(order.problems), 0, 'Нет проблем')
