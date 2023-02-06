from stall.model.order import Order


async def test_unreserve(tap, dataset):
    with tap.plan(27, 'Резервирование товара'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        stock1 = await dataset.stock(product=product1, store=store, count=10)
        tap.eq(stock1.count, 10, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(product=product2, store=store, count=20)
        tap.eq(stock2.count, 20, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        stock3 = await dataset.stock(product=product3, store=store, count=30)
        tap.eq(stock3.count, 30, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        request = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='reserve',
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

        tap.ok(request, 'Заказ создан')
        tap.ok(await request.business.reserve(), 'Резервирование')

        request.rehash(status='canceled', estatus='unreserve')
        tap.ok(await request.save(), 'Заказ переведен в статус')

        order = await Order.load(request.order_id)
        tap.ok(request, 'Заказ получен')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 10, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 0, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 20, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 0, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 30, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 0, 'Зарезервировано 3')


