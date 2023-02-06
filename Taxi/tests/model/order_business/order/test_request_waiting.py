async def test_waiting(tap, dataset):
    with tap.plan(13, 'Резервирование товара'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user = await dataset.user(store=store)
        tap.ok(user, 'Пользователь создан')

        order = await dataset.order(
            store=store,
            type = 'order',
            status='request',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await order.ack(user), 'Пользователь согласился взять заказ')

        old_version = order.version
        tap.ok(old_version, f'Старая версия={old_version}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(order.version > old_version, f'Новая версия={order.version}')


async def test_waiting_no_ack(tap, dataset):
    with tap.plan(8, 'Резервирование товара'):

        order = await dataset.order(
            type = 'order',
            status='request',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')
