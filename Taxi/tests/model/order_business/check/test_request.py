async def test_request_noack(tap, dataset):
    with tap.plan(13, 'Нет ack'):
        order = await dataset.order(
            type='check',
            status='request',
            estatus='begin',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.type, 'check', 'type')
        tap.eq(order.status, 'request', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')
        tap.eq(order.acks, [], 'пустой массив подтверждений')

        tap.ok(await order.business.order_changed(),
               'Выполнилась стейт машина')
        tap.ok(await order.reload(), 'перегрузили')
        tap.eq(order.status, 'request', 'статус переключен')
        tap.eq(order.estatus, 'waiting', 'сабстатус переключен')

        tap.ok(not await order.business.order_changed(),
               'Повторно выполнилась стейт машина - нет результата')
        tap.ok(await order.reload(), 'перегрузили')
        tap.eq(order.status, 'request', 'статус не изменился')
        tap.eq(order.estatus, 'waiting', 'сабстатус не изменился')


async def test_request_ack(tap, dataset):
    with tap.plan(16, 'Есть ack'):
        user = await dataset.user(role='executer')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад назначен')

        order = await dataset.order(
            type='check',
            status='request',
            estatus='begin',
            store_id=user.store_id,
            acks=[user.user_id],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.type, 'check', 'type')
        tap.eq(order.status, 'request', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')
        tap.eq(order.store_id, user.store_id, 'на складе')
        tap.eq(order.acks, [user.user_id], 'массив подтверждений')

        tap.ok(await order.business.order_changed(),
               'Выполнилась стейт машина')
        tap.ok(await order.reload(), 'перегрузили')
        tap.eq(order.status, 'request', 'статус переключен')
        tap.eq(order.estatus, 'waiting', 'сабстатус переключен')

        tap.ok(await order.business.order_changed(),
               'Повторно выполнилась стейт машина - нет результата')
        tap.ok(await order.reload(), 'перегрузили')
        tap.eq(order.status, 'processing', 'статус переключен')
        tap.eq(order.estatus, 'begin', 'сабстатус переключен')
