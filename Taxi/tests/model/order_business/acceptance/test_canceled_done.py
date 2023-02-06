async def test_done(tap, dataset):
    with tap.plan(8, 'Заказ обработан'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='canceled',
            estatus='done',
            target='canceled',
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
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')
