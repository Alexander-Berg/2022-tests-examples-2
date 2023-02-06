
async def test_unreserve(tap, uuid, dataset):
    with tap.plan(18, 'Резервирование товара'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='canceled',
            estatus='unreserve',
            target='canceled',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'canceled', 'target: canceled')

        stock1 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=7,
            reserve=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=3,
            reserve=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock3 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf2,
            product=product2,
            count=20,
            reserve=20,
            valid='2020-01-01',
            lot=uuid(),
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 7, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 0, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 3, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 0, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 20, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 0, 'Зарезервировано 3')
