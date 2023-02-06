async def test_check_shelves(tap, dataset):
    with tap.plan(9, 'КСГ - проверка товара'):

        store = await dataset.store()
        await dataset.shelf(store=store, type='trash', order=3)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status = 'reserving',
            estatus='check_shelves',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_shelves', 'check_shelves')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_store_fail(tap, dataset, wait_order_status):
    with tap.plan(3, 'КСГ - проверка товара'):

        store = await dataset.store()
        await dataset.shelf(store=store, type='markdown')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status = 'reserving',
            estatus='begin',
        )

        await wait_order_status(order, ('reserving', 'check_shelves'))
        await order.business.order_changed()

        tap.eq(len(order.problems), 1, 'Проблема')
        with order.problems[0] as problem:
            tap.eq(problem.type, 'shelf_not_found', 'Полка не найдена')
