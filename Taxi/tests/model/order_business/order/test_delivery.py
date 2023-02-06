# pylint: disable=too-many-statements,unused-variable


async def test_delivery(tap, dataset, now, wait_order_status):
    with tap.plan(24, 'Сборка заказа'):

        product = await dataset.product()
        store   = await dataset.store()
        user    = await dataset.user(store=store)
        courier = await dataset.user(store=store, role='courier')
        stock   = await dataset.stock(product=product, store=store, count=100)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required = [
                {
                    'product_id': product.product_id,
                    'count': 10
                },
            ],
            dispatch_type='grocery',
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('delivery', 'begin'), user_done=user)

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'waiting'), 'delivery:waiting')
        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'waiting'),
               'delivery:waiting ожидаем назначения')

        order.courier_id = courier.user_id
        tap.ok(await order.save(), 'зафорсили курьера')

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'enqueued'), 'delivery:enqueued')
        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'enqueued'),
               'delivery:enqueued ожидаем отправки')

        tap.ok(await order.signal({'type': 'departure'}),
               'сигнал: departure')

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'en_route'), 'delivery:en_route')
        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'en_route'),
               'delivery:en_route ожидаем прибытия')

        tap.ok(await order.signal({'type': 'arrive'}),
               'сигнал: arrive')

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'wait_client'),
               'delivery:wait_client')
        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('delivery', 'wait_client'),
               'delivery:wait_client ожидаем забора клиентом')

        tap.ok(await order.signal({'type': 'hand_over'}),
               'сигнал: hand_over')

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'Доставка завершена')
