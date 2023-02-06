async def test_markdown_fail(tap, dataset, wait_order_status):
    with tap.plan(3, 'КСГ - проверка товара'):

        assortment = await dataset.assortment()
        store = await dataset.store(markdown_assortment=assortment)
        await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status = 'reserving',
            estatus='begin',
            vars={'mode': 'store2markdown'},
        )

        await wait_order_status(order, ('reserving', 'check_shelves'))
        await order.business.order_changed()

        tap.eq(len(order.problems), 1, 'Проблема')
        with order.problems[0] as problem:
            tap.eq(problem.type, 'shelf_not_found', 'Полка не найдена')


async def test_assortment_fail(tap, dataset, wait_order_status):
    with tap.plan(3, 'Для распродажи уценки есть ассортимент'):

        store = await dataset.store()
        await dataset.shelf(store=store, type='markdown')
        await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status = 'reserving',
            estatus='begin',
            vars={'mode': 'store2markdown'},
        )

        await wait_order_status(order, ('reserving', 'check_shelves'))
        await order.business.order_changed()

        tap.eq(len(order.problems), 1, 'Проблема')
        with order.problems[0] as problem:
            tap.eq(problem.type, 'assortment_not_found', 'Ассортимента нет')
