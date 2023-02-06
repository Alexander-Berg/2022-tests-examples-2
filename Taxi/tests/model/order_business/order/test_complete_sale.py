from stall.model.stock import Stock
from stall.model.order import Order


async def test_sale(tap, dataset):
    with tap.plan(27, 'Начало завершения выполненного заказа'):

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

        request.rehash(status='complete', estatus='sale')
        tap.ok(await request.save(), 'Заказ переведен в статус')

        order = await Order.load(request.order_id)
        tap.ok(request, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'sale', 'sale')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 9, 'Списано 1')
        tap.eq(stock1.reserve, 0, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 18, 'Списано 2')
        tap.eq(stock2.reserve, 0, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 27, 'Списано 3')
        tap.eq(stock3.reserve, 0, 'Зарезервировано 3')


async def test_sale_kitchen(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'весь созданный кофе должен быть продан'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('lost', 'lost'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 100),
                ('comp', 'coffee1', 100),
                ('comp', 'milk1', 100),
                ('comp', 'glass1', 100),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': components['coffee1'].product_id,
                    'count': 10,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 2,
                },
            ],
        )

        await wait_order_status(order, ('complete', 'sale'), user_done=user)

        tap.ok(await order.business.order_changed(), 'продаем кофе')
        tap.ok(await order.business.order_changed(), 'продаем кофе')

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'complete', 'target: complete')

        stocks_on_demand = await Stock.list_by_product(
            product_id=products['latte'].product_id,
            store_id=store.store_id,
            shelf_type='kitchen_on_demand',
        )

        tap.eq(len(stocks_on_demand), 1, 'приготовили 1 тип кофе')
        tap.eq(stocks_on_demand[0].count, 0, 'нет латте в остатках')
        tap.eq(stocks_on_demand[0].reserve, 0, 'нет латте в резерве')

        tap.eq(
            len(await Stock.list_by_order(order)),
            0,
            'по заказу вообще нет резерва',
        )
