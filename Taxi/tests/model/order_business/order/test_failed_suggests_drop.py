from stall.model.order import Order
from stall.model.suggest import Suggest


async def test_suggests_drop(tap, dataset):
    with tap.plan(23, 'Очистка саджестов'):

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
            target='failed',
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
        tap.ok(await request.business.suggests_generate(), 'Резервирование')

        suggests = await Suggest.list_by_order(request)
        tap.eq(len(suggests), 3, 'Список саджестов')

        request.rehash(status='failed', estatus='suggests_drop')
        tap.ok(await request.save(), 'Заказ переведен в статус')

        order = await Order.load(request.order_id)
        tap.ok(request, 'Заказ получен')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'failed', 'target: failed')

        tap.eq(
            sorted(order.shelves),
            sorted([stock1.shelf_id, stock2.shelf_id, stock3.shelf_id]),
            'полки'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(len(order.shelves), 0, 'Нет полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов очищен')
