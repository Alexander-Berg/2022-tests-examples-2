async def test_update(tap, dataset, now, wait_order_status):
    with tap.plan(23, 'Пришли изменения при ожидании'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store)
        user    = await dataset.user(store=store)

        await dataset.stock(shelf=shelf, product=product1, count=100)
        await dataset.stock(shelf=shelf, product=product2, count=200)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            target='complete',
            approved=now(),
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('request', 'waiting'),
        )

        with await order.reload() as o:
            tap.eq(o.status, 'request', 'request')
            tap.eq(o.estatus, 'waiting', 'waiting')
            tap.eq(o.target, 'complete', 'target: complete')
            tap.eq(o.acks, [], 'Взятий нет')

            tap.eq(o.required[0].product_id, product1.product_id, 'Продукт 1')

            stocks = await dataset.Stock.list_by_order(order)
            stocks = dict((x.product_id, x) for x in stocks)
            tap.eq(len(stocks), 1, 'Остатки')

            with stocks[product1.product_id] as stock:
                tap.eq(stock.count, 100, 'Остаток')
                tap.eq(stock.reserve, 10, 'Зарезервировано')

            version_1 = order.version

        order.vars['required'] = [
            {
                'product_id': product2.product_id,
                'count': 20,
            },
        ]
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('request', 'check_target'))
        await wait_order_status(order, ('request', 'waiting'))

        with await order.reload() as o:
            tap.eq(o.status, 'request', 'request')
            tap.eq(o.estatus, 'waiting', 'waiting')
            tap.eq(o.target, 'complete', 'target: complete')
            tap.eq(o.acks, [], 'Взятий нет')

            tap.eq(o.required[0].product_id, product2.product_id, 'Продукт 2')

            stocks = await dataset.Stock.list_by_order(order)
            stocks = dict((x.product_id, x) for x in stocks)
            tap.eq(len(stocks), 1, 'Остатки')

            with stocks[product2.product_id] as stock:
                tap.eq(stock.count, 200, 'Остаток')
                tap.eq(stock.reserve, 20, 'Зарезервировано')

            version_2 = order.version
            tap.ok(version_2 > version_1, 'Версию подвинули')

        tap.ok(await order.ack(user), 'Пользователь согласился взять заказ')

        await wait_order_status(order, ('processing', 'begin'))
