async def test_done(tap, dataset):
    with tap.plan(8, 'Заказ обработан'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type ='acceptance',
            status='failed',
            estatus='done',
            target='failed',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
                {
                    'product_id': product3.product_id,
                    'count': 3
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')


async def test_defibrillation(tap, dataset, wait_order_status):
    with tap.plan(17, 'Заказ реанимирован'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.full_store()
        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='failed',
            estatus='done',
            target='failed',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
                {
                    'product_id': product3.product_id,
                    'count': 3
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')

        tap.ok(await order.signal({'type': 'order_defibrillation'}),
               'сигнал отправлен')

        await order.business.order_changed()
        await order.reload()
        tap.eq(order.status, 'reserving', 'status reserving')
        tap.eq(order.estatus, 'begin', 'estatus begin')

        await wait_order_status(
            order,
            ('request', 'begin'),
        )
        tap.ok(await order.ack(user), 'ack')
        tap.in_ok(user.user_id, order.acks, 'попал в acks')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.status, 'processing', 'status processing')
        tap.eq(order.estatus, 'waiting', 'estatus waiting')

