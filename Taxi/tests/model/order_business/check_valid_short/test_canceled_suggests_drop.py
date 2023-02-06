from stall.model.suggest import Suggest


async def test_suggests_drop(tap, dataset):
    with tap.plan(13, 'Очистка саджестов'):

        product1 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf = await dataset.shelf(store=store, type='store')
        trash = await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='canceled',
            estatus='suggests_drop',
            target='canceled',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'canceled', 'target: canceled')

        suggest1 = await dataset.suggest(
            order,
            type='shelf2box',
            status='done',
            count=10,
            result_count=10,
            shelf_id=shelf.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggest2 = await dataset.suggest(
            order,
            type='box2shelf',
            status='done',
            count=10,
            result_count=10,
            shelf_id=trash.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest2, 'Саджест 2')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(len(order.shelves), 0, 'Нет полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов очищен')
