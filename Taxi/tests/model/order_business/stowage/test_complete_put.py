# pylint: disable=too-many-locals

from datetime import datetime, timedelta
from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def test_sale(tap, dataset):
    with tap.plan(31, 'Зачисление товара'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.full_store()
        shelf = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='complete',
            estatus='put',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1,
                    'valid': datetime.utcnow() + timedelta(days=10),
                },
                {
                    'product_id': product3.product_id,
                    'count': 3,
                    'valid': datetime.utcnow() + timedelta(days=30),
                },
                {
                    'product_id': product2.product_id,
                    'count': 2,
                    'valid': datetime.utcnow() + timedelta(days=20),
                },
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'put', 'put')
        tap.eq(order.target, 'complete', 'target: complete')

        for i, product in enumerate([product1, product2, product3]):
            suggest = await dataset.suggest(
                order,
                status='done',
                type='box2shelf',
                shelf_id=shelf.shelf_id,
                product_id=product.product_id,
                count=i+1,
                result_count=i+1,
            )
            tap.ok(suggest, f'suggest_id={suggest.suggest_id}')

        await order.business.order_changed()
        await order.business.order_changed()
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Саджесты')

        stocks = await Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=shelf.shelf_id,
        )
        tap.eq(len(stocks), 3, 'Остатки созданы')

        stock1 = (list(
            x for x in stocks if x.product_id == product1.product_id
        ))[0]
        with stock1 as stock:
            tap.eq(
                stock.product_id,
                product1.product_id,
                f'Продукт {stock.product_id}'
            )
            tap.eq(stock.count, 1, f'Остаток={stock.count}')
            tap.eq(stock.reserve, 0, f'Зарезервировано={stock.reserve}')
            tap.ok(stock.valid, f'Годен до={stock.valid}')
            tap.eq(stock.lot, order.order_id, 'Лот как номер заказа')
            tap.eq(stock.store_id, order.store_id, 'store_id')
            tap.eq(stock.company_id, order.company_id, 'company_id')

        stock3 = (list(
            x for x in stocks if x.product_id == product3.product_id
        ))[0]
        with stock3 as stock:
            tap.eq(
                stock.product_id,
                product3.product_id,
                f'Продукт {stock.product_id}'
            )
            tap.eq(stock.count, 3, f'Остаток={stock.count}')
            tap.eq(stock.reserve, 0, f'Зарезервировано={stock.reserve}')
            tap.ok(stock.valid, f'Годен до={stock.valid}')
            tap.eq(stock.lot, order.order_id, 'Лот как номер заказа')

        stock2 = (list(
            x for x in stocks if x.product_id == product2.product_id
        ))[0]
        with stock2 as stock:
            tap.eq(
                stock.product_id,
                product2.product_id,
                f'Продукт {stock.product_id}'
            )
            tap.eq(stock.count, 2, f'Остаток={stock.count}')
            tap.eq(stock.reserve, 0, f'Зарезервировано={stock.reserve}')
            tap.ok(stock.valid, f'Годен до={stock.valid}')
            tap.eq(stock.lot, order.order_id, 'Лот как номер заказа')


async def test_suggest_not_found(tap, dataset):
    with tap.plan(16, 'Зачисление товара'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.full_store()
        shelf = await dataset.shelf(store=store, type='store')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='complete',
            estatus='put',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product3.product_id, 'count': 3},
                {'product_id': product2.product_id, 'count': 2},
            ],
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'put', 'put')
        tap.eq(order.target, 'complete', 'target: complete')

        for i, product in enumerate([product1, product3]):
            suggest = await dataset.suggest(
                order,
                status='done',
                type='box2shelf',
                shelf_id=shelf.shelf_id,
                product_id=product.product_id,
                count=i+1,
                result_count=i+1,
            )
            tap.ok(suggest, f'suggest_id={suggest.suggest_id}')

        await order.business.order_changed()
        await order.business.order_changed()
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 1, 'Появилась проблема')
        tap.eq(order.problems[0].type, 'shelf_not_found', 'shelf_not_found')
        tap.eq(order.problems[0].product_id, product2.product_id, 'Продукт')
        tap.eq(order.problems[0].count, 2, 'Количество')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты')

        stocks = await Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=shelf.shelf_id,
        )
        tap.eq(len(stocks), 2, 'Остатки созданы')
