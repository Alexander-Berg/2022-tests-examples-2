from stall.model.stock import Stock


async def test_reserve(tap, dataset, wait_order_status):
    with tap.plan(18, 'Резервирование товара'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        await dataset.stock(product=product1, store=store, count=100)
        await dataset.stock(product=product2, store=store, count=200)
        await dataset.stock(product=product3, store=store, count=300)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
            ],
            vars={'editable': True},
        )

        order.vars['required'] = [
            {
                'product_id': product1.product_id,
                'count': 11,
            },
            {
                'product_id': product2.product_id,
                'count': 2,
            },
            {
                'product_id': product3.product_id,
                'count': 30
            },
        ]
        tap.ok(await order.save(), 'Пришло изменение по продуктам')

        await wait_order_status(order, ('reserving', 'reserve'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve', 'reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve_kitchen', 'reserve_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 3, 'Остатки')

        with stocks[product1.product_id] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 11, 'Зарезервировано')

        with stocks[product2.product_id] as stock:
            tap.eq(stock.count, 200, 'Остаток')
            tap.eq(stock.reserve, 2, 'Зарезервировано')

        with stocks[product3.product_id] as stock:
            tap.eq(stock.count, 300, 'Остаток')
            tap.eq(stock.reserve, 30, 'Зарезервировано')


async def test_product_not_found(tap, dataset, uuid):
    with tap.plan(17, 'Не генерим саджесты для несуществующих товаров'):
        store = await dataset.store()
        product = await dataset.product()
        await dataset.stock(product=product, store=store, count=1)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='reserve',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                },
                {
                    'product_id': uuid(),
                    'count': 300,
                },
            ],
            vars={'editable': True},
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve', 'reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve_kitchen', 'reserve_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')
        tap.eq(len(order.problems), 1, 'Есть проблема')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 1, 'Остатки')

        with stocks[product.product_id] as stock:
            tap.eq(stock.count, 1, 'Остаток')
            tap.eq(stock.reserve, 1, 'Зарезервировано')

        await order.business.order_changed()
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(
            order.estatus,
            'calculate_order_weight',
            'calculate_order_weight',
        )
        tap.eq(order.target, 'complete', 'target: complete')
        tap.eq(len(order.problems), 1, 'Есть проблема')
