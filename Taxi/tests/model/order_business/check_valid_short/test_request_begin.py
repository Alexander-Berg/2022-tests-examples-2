async def test_begin(tap, dataset):
    with tap.plan(11, 'Начало предложение'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user = await dataset.user(store=store)
        tap.ok(user, 'Пользователь создан')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='request',
            estatus='begin',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await order.ack(user), 'Пользователь согласился взять заказ')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')
