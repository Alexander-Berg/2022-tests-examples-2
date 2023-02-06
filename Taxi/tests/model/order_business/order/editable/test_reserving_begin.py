async def test_begin_editable(tap, dataset):
    with tap.plan(4, 'Резервирование товара'):

        product = await dataset.product()
        store   = await dataset.store()

        await dataset.stock(product=product, store=store, count=100)

        order = await dataset.order(
            store=store,
            type = 'order',
            status = 'reserving',
            required = [
                {
                    'product_id': product.product_id,
                    'count': 10
                },
            ],
            vars={'editable': True},
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'edit_required', 'edit_required')
        tap.eq(order.target, 'complete', 'target: complete')
