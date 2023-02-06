from stall.model.suggest import Suggest


async def test_suggests_drop(tap, dataset, wait_order_status):
    with tap.plan(13, 'Очистка саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type = 'acceptance',
            status='complete',
            estatus='suggests_drop',
            target='complete',
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
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='check',
            shelf_id=shelf.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggest2 = await dataset.suggest(
            order,
            type='check',
            shelf_id=shelf.shelf_id,
            product_id=product2.product_id,
        )
        tap.ok(suggest2, 'Саджест 2')

        suggest3 = await dataset.suggest(
            order,
            type='check',
            shelf_id=shelf.shelf_id,
            product_id=product3.product_id,
        )
        tap.ok(suggest3, 'Саджест 3')

        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(len(order.shelves), 0, 'Нет полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов очищен')
