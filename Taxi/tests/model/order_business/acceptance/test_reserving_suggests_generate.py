from stall.model.suggest import Suggest


async def test_suggests_generate(tap, dataset):
    with tap.plan(19, 'Генерация новых саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='incoming')

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='reserving',
            estatus='suggests_generate',
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
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='check',
            shelf_id=shelf.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggests = await Suggest.list_by_order(order)
        suggests = dict((s.product_id, s) for s in suggests)
        tap.eq(len(suggests), 1, 'Какие-то саджесты уже были')

        await order.business.order_changed()

        suggests = await Suggest.list_by_order(order)
        suggests = dict((s.product_id, s) for s in suggests)
        tap.eq(len(suggests.keys()), 3, 'Список саджестов')

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.type, 'check', 'Саджест type')
            tap.eq(
                suggest.product_id,
                product1.product_id,
                'Саджест product_id'
            )

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.type, 'check', 'Саджест type')
            tap.eq(
                suggest.product_id,
                product3.product_id,
                'Саджест product_id'
            )

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.type, 'check', 'Саджест type')
            tap.eq(
                suggest.product_id,
                product2.product_id,
                'Саджест product_id'
            )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(order.shelves, [shelf.shelf_id], 'Список полок')


async def test_missing_incoming(tap, dataset):
    with tap.plan(11, 'В лавке нет полки приемки'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='reserving',
            estatus='suggests_generate',
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
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов пока пуст')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(len(order.problems), 1, 'Проблема записана')
        tap.ok(order.problems[0].type, 'shelf_not_found', 'Проблема с полкой')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов пока пуст')
