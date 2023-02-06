async def test_non_weight_product(tap, dataset):
    with tap.plan(7):
        store = await dataset.store()
        product = await dataset.product(
            type_accounting='unit',
        )

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='check_required',
            required=[
                {
                    'product_id': product.product_id,
                    'weight': 5,
                },
            ],
        )

        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_required', 'check_required')

        await order.business.order_changed()

        tap.eq(len(order.problems), 1, 'Проблема обнаружена')
        tap.eq(
            order.problems[0].type,
            'non_weight_product',
            'Обнаружен вес для невесового товара',
        )
        tap.eq(
            order.problems[0].product_id,
            product.product_id,
            'Корректный product_id',
        )
        tap.eq(order.status, 'failed', 'failed')
