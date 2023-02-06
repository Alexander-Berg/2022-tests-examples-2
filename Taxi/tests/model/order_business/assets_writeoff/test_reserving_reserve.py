async def test_reserve(tap, dataset, wait_order_status):
    with tap.plan(22, 'Резервирование товара'):
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

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
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
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('reserving', 'reserve'))
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
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


async def test_no_product(tap, dataset, wait_order_status):
    with tap.plan(19, 'Нет продукта'):

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

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
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
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('reserving', 'reserve'))
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')
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


async def test_low_product(tap, dataset, wait_order_status):
    with tap.plan(24, 'Недостаточно остатков продукта'):

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

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
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
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('reserving', 'reserve'))
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')
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


async def test_already_reserved(tap, dataset, wait_order_status):
    with tap.plan(23, 'Уже зарезервировано'):

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

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
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
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('reserving', 'reserve'))
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await stock3.do_reserve(order, 3), 'Уже зарезервировано')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
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


async def test_already_reserved_low(tap, dataset, wait_order_status):
    with tap.plan(23, 'Частично уже зарезервировано'):

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

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
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
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('reserving', 'reserve'))
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(await stock3.do_reserve(order, 2), 'Уже что-то зарезервировано')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
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


async def test_reserve_specific_shelf(tap, dataset, wait_order_status):
    with tap.plan(10, 'Резервирование товара на конкретной полке'):
        product = await dataset.product()

        store = await dataset.store()
        shelf_1 = await dataset.shelf(store=store)
        shelf_2 = await dataset.shelf(store=store)
        shelf_3 = await dataset.shelf(store=store)

        stock_1 = await dataset.stock(
            product=product,
            store=store,
            count=10,
            shelf=shelf_1
        )
        stock_2 = await dataset.stock(
            product=product,
            store=store,
            count=20,
            shelf=shelf_2
        )
        stock_3 = await dataset.stock(
            product=product,
            store=store,
            count=30,
            shelf=shelf_3
        )

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf_2.shelf_id,
                    'count': 10,
                },
            ],
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await stock_1.reload(), 'Остаток 1 перезабрали')
        tap.eq(stock_1.count, 10, 'Остаток 1 есть')
        tap.eq(stock_1.reserve, 0, 'Зарезервировано 0')

        tap.ok(await stock_2.reload(), 'Остаток 2 перезабрали')
        tap.eq(stock_2.count, 20, 'Остаток 2 есть')
        tap.eq(stock_2.reserve, 10, 'Зарезервировано 10')

        tap.ok(await stock_3.reload(), 'Остаток 3 перезабрали')
        tap.eq(stock_3.count, 30, 'Остаток 3 есть')
        tap.eq(stock_3.reserve, 0, 'Зарезервировано 0')


async def test_reserve_no_shelf(tap, dataset, wait_order_status):
    with tap.plan(7, 'Полка не с этого склада'):
        product = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf()

        stock = await dataset.stock(
            product=product,
            store_id=shelf.store_id,
            count=10,
            shelf=shelf
        )

        task = await dataset.repair_task(store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf.shelf_id,
                    'count': 10,
                },
            ],
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            },
        )
        await wait_order_status(order, ('failed', 'done'))
        tap.eq(len(order.problems), 1, 'Есть проблема')
        problem = order.problems[0]
        tap.eq(problem.type, 'shelf_not_found', 'не нашли полку')
        tap.eq(problem.shelf_id, shelf.shelf_id, 'с нужной полкой')

        tap.ok(await stock.reload(), 'Остаток 1 перезабрали')
        tap.eq(stock.count, 10, 'Количество старое')
        tap.eq(stock.reserve, 0, 'Зарезервировано 0')
