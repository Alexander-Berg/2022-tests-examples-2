from datetime import timedelta
from libstall.util import now


async def test_reserve(tap, dataset):
    with tap.plan(24, 'Резервирование товара'):

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

        order = await dataset.order(
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
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve', 'reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve_kitchen', 'reserve_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 10, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 1, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 20, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 2, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 30, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 3, 'Зарезервировано 3')


async def test_reserve_sort(tap, dataset, wait_order_status):
    with tap.plan(2, 'Приоритет резервирования с меньшим СГ'):

        product = await dataset.product()

        store = await dataset.store()

        await dataset.stock(product=product, store=store, count=10)
        await dataset.stock(product=product, store=store, count=20)
        await dataset.stock(product=product, store=store, count=30)
        await dataset.stock(
            product=product, store=store, count=5,
            valid=now(),
        )
        stock = await dataset.stock(
            product=product, store=store, count=50,
            valid=now() - timedelta(days=10),
        )
        await dataset.stock(
            product=product, store=store, count=51,
            valid=stock.valid,
        )

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            required = [
                {
                    'product_id': product.product_id,
                    'count': 1
                },
            ],
        )

        await wait_order_status(order, ('reserving', 'reserve'))
        await order.business.order_changed()

        await stock.reload()
        tap.eq(stock.reserve, 1, 'Зарезервировано приоритетное')


async def test_no_product(tap, dataset):
    with tap.plan(21, 'Нет продукта'):

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

        order = await dataset.order(
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
        tap.eq(order.problems[0].product_id, product3.product_id,
               'с продуктом 3')
        tap.eq(order.problems[0].count, 3, 'количество установлено')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 10, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 1, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 20, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 2, 'Зарезервировано 2')


async def test_low_product(tap, dataset):
    with tap.plan(26, 'Недостаточно остатков продукта'):

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

        order = await dataset.order(
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
                    'count': 300
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
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
        tap.eq(order.problems[0].product_id, product3.product_id,
               'с продуктом 3')
        tap.eq(order.problems[0].count, 270, 'количество установлено')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 10, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 1, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 20, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 2, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 30, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 30, 'Зарезервировано 3 сколько было')


async def test_already_reserved(tap, dataset):
    with tap.plan(25, 'Уже зарезервировано'):

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

        order = await dataset.order(
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
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve', 'reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await stock3.do_reserve(order, 3), 'Уже зарезервировано')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve_kitchen', 'reserve_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 10, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 1, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 20, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 2, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 30, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 3, 'Зарезервировано 3')


async def test_already_reserved_low(tap, dataset):
    with tap.plan(25, 'Частично уже зарезервировано'):

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

        order = await dataset.order(
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
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve', 'reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await stock3.do_reserve(order, 2), 'Уже что-то зарезервировано')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve_kitchen', 'reserve_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 10, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 1, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 20, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 2, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 30, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 3, 'Зарезервировано 3')
