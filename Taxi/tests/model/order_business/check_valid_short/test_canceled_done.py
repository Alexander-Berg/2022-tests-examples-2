async def test_done(tap, dataset):
    with tap.plan(8, 'Заказ обработан'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='canceled',
            estatus='done',
            target='canceled',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')
