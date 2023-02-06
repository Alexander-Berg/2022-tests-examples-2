async def test_check_required(tap, dataset, wait_order_status):
    with tap.plan(11, 'Приемка товара - проверка товара'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=20, tags=['freezer'])
        product3 = await dataset.product()

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status = 'reserving',
            estatus='check_required',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
                {
                    'product_id': product2.product_id,
                    'count': 2,
                },
                {
                    'product_id': product3.product_id,
                    'count': 3
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_required', 'check_required')
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('reserving', 'suggests_generate'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        with order.required[0] as require:
            tap.ok(require.valid, 'Срок годности заполнен')

        with order.required[1] as require:
            tap.ok(require.valid, 'Срок годности заполнен')

        with order.required[2] as require:
            tap.eq(require.valid, None, 'Срок годности не заполнен')
