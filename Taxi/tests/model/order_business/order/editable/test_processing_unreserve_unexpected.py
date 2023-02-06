from stall.model.stock import Stock


async def test_reserve(tap, dataset, now, wait_order_status):
    with tap.plan(14, 'Резервирование товара с повторениями в требованиях'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, order=1)
        shelf2 = await dataset.shelf(store=store, order=2)

        await dataset.stock(product=product1, shelf=shelf1, count=100)
        await dataset.stock(product=product1, shelf=shelf2, count=100)
        await dataset.stock(product=product2, store=store, count=200)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 70,
                    'price': 100,
                },
                {
                    'product_id': product1.product_id,
                    'count': 70,
                    'price': 110,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await Stock.list_by_order(order)
        stocks = dict(((x.product_id, x.reserve), x) for x in stocks)
        tap.eq(len(stocks), 2, 'Остатки')

        with stocks[(product1.product_id, 100)] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 100, 'Зарезервировано')
        with stocks[(product1.product_id, 40)] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 40, 'Зарезервировано')

        order.vars['required'] = [
            {
                'product_id': product2.product_id,
                'count': 150,
                'price': 100,
            },
            {
                'product_id': product2.product_id,
                'count': 40,
                'price': 110,
            },
        ]
        tap.ok(await order.save(), 'Пришло изменение по продуктам')

        await wait_order_status(order, ('processing', 'unreserve_unexpected'))

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'reserve', 'reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        stocks = await Stock.list_by_order(order)
        tap.eq(
            len(stocks),
            0,
            'Остатки не резервированы: старый удален, нового еще нет'
        )
