async def test_done(tap, dataset):
    with tap.plan(9, 'Заказ выполнен'):
        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='complete',
            estatus='done',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
