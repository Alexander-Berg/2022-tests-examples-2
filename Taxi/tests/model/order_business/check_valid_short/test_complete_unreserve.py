from datetime import timedelta
from libstall.util import now


async def test_unreserve(tap, uuid, dataset):
    with tap.plan(25, 'Резервирование товара'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        trash  = await dataset.shelf(store=store, type='trash', order=3)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='complete',
            estatus='unreserve',
            target='complete',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'complete', 'target: complete')

        stock1 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=5,
            reserve=5,
            valid=now() + timedelta(days=15),
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=3,
            reserve=3,
            valid=now() + timedelta(days=30),
            lot=uuid(),
        )

        stock4 = await dataset.stock(
            store=store,
            order=order,
            shelf=trash,
            product=product1,
            count=7,
            reserve=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock5 = await dataset.stock(
            store=store,
            order=order,
            shelf=trash,
            product=product2,
            count=20,
            reserve=20,
            valid='2020-01-01',
            lot=uuid(),
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        # Остатки на слкладе
        with stock1 as stock:
            tap.ok(await stock.reload(), 'Остаток возвращен')
            tap.eq(stock.shelf_id, shelf1.shelf_id, 'Полка')
            tap.eq(stock.count, 5, 'Количество')
            tap.eq(stock.reserve, 0, 'Зарезервировано')

        with stock2 as stock:
            tap.ok(await stock.reload(), 'Остаток возвращен')
            tap.eq(stock.shelf_id, shelf1.shelf_id, 'Полка')
            tap.eq(stock.count, 3, 'Количество')
            tap.eq(stock.reserve, 0, 'Зарезервировано')

        # Остатки на списании
        with stock4 as stock:
            tap.ok(await stock.reload(), 'Остаток остался на списании')
            tap.eq(stock.shelf_id, trash.shelf_id, 'Полка')
            tap.eq(stock.count, 7, 'Количество')
            tap.eq(stock.reserve, 0, 'Зарезервировано')

        with stock5 as stock:
            tap.ok(await stock.reload(), 'Остаток остался на списании')
            tap.eq(stock.shelf_id, trash.shelf_id, 'Полка')
            tap.eq(stock.count, 20, 'Количество')
            tap.eq(stock.reserve, 0, 'Зарезервировано')
