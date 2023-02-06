from stall.model.suggest import Suggest


async def test_suggests_drop(tap, dataset, wait_order_status):
    with tap.plan(11, 'Очистка саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='complete',
            estatus='suggests_drop',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product3.product_id, 'count': 3},
                {'product_id': product2.product_id, 'count': 2},
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'complete', 'target: complete')

        for product in product1, product2, product3:
            suggest = await dataset.suggest(
                order,
                status='done',
                type='box2shelf',
                shelf_id=shelf.shelf_id,
                product_id=product.product_id,
            )
            tap.ok(suggest, f'suggest_id={suggest.suggest_id}')

        await wait_order_status(order, ('complete', 'done'))
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Саджестов нет')
