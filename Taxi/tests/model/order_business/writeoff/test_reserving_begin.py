async def test_begin(tap, dataset):
    with tap.plan(9, 'Списание товара - начало'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status = 'reserving',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_shelves', 'check_shelves')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
