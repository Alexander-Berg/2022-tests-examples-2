from datetime import datetime, timedelta

import pytest

from stall.model.shelf import Shelf
from stall.model.suggest import Suggest


async def test_suggests_generate(tap, dataset):
    with tap.plan(25, 'Генерация новых саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.full_store()
        shelf = (await Shelf.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'store'),
            ],
        )).list[0]

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='suggests_generate',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1,
                    'valid': datetime.utcnow() + timedelta(days=1),
                },
                {'product_id': product3.product_id, 'count': 3},
                {
                    'product_id': product2.product_id,
                    'count': 2,
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='box2shelf',
            shelf_id=shelf.shelf_id,
            product_id=product1.product_id,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Какие-то саджесты уже были')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')
        tap.in_ok(shelf.shelf_id, order.shelves, 'Список полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict((s.product_id, s) for s in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product1.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.ok(
                suggest.valid,
                f'valid={suggest.valid}'
            )

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product3.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.ok(
                not suggest.valid,
                f'valid={suggest.valid}'
            )

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product2.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.ok(
                not suggest.valid,
                f'valid={suggest.valid}'
            )


async def test_missing_shelves(tap, dataset):
    with tap.plan(11, 'В лавке нет полок раскладки'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        await dataset.shelf(store=store, type='store', status='disabled')
        await dataset.shelf(store=store, type='store', status='removed')

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='suggests_generate',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product3.product_id, 'count': 3},
                {'product_id': product2.product_id, 'count': 2},
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


async def test_tags(tap, dataset):
    with tap.plan(16, 'Проверка раскладки по тегам'):

        product1 = await dataset.product(tags=['refrigerator'])
        product2 = await dataset.product(tags=['freezer'])

        store = await dataset.full_store()

        shelf1 = await dataset.shelf(
            store=store,
            type='store',
            tags=['freezer'],
        )
        shelf2 = await dataset.shelf(
            store=store,
            type='store',
            tags=['refrigerator'],
        )

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='suggests_generate',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1,
                    'tags': product1.tags,
                },
                {
                    'product_id': product2.product_id,
                    'count': 2,
                    'tags': product2.tags,
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
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')
        tap.eq(
            sorted(order.shelves),
            sorted([shelf1.shelf_id, shelf2.shelf_id]),
            'Список полок',
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Список саджестов')
        suggests = dict((s.product_id, s) for s in suggests)

        # freezer
        with suggests[product1.product_id] as suggest:
            tap.eq(
                suggest.product_id,
                product1.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf2.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )

        # refrigerator
        with suggests[product2.product_id] as suggest:
            tap.eq(
                suggest.product_id,
                product2.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf1.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )


async def test_shelves_no_tag(tap, dataset):
    with tap.plan(16, 'В лавке нет полки подходящей для продукта'):

        product1 = await dataset.product(tags=['refrigerator'])
        product2 = await dataset.product(tags=['freezer', 'refrigerator'])

        store = await dataset.full_store()

        await dataset.shelf(
            store=store,
            type='store',
            tags=['freezer'],
        )

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='suggests_generate',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1,
                    'tags': product1.tags,
                },
                {
                    'product_id': product2.product_id,
                    'count': 2,
                    'tags': product2.tags,
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

        tap.eq(len(order.problems), 2, 'Проблема записана')

        tap.eq(order.problems[0].type, 'shelf_not_found', 'Проблема с полкой')
        tap.eq(
            order.problems[0].product_id,
            product1.product_id,
            'Продукт указан'
        )
        tap.eq(order.problems[0].count, 1, f'count={order.problems[0].count}')

        tap.eq(order.problems[1].type, 'shelf_not_found', 'Проблема с полкой')
        tap.eq(
            order.problems[1].product_id,
            product2.product_id,
            'Продукт указан'
        )
        tap.eq(order.problems[1].count, 2, f'count={order.problems[1].count}')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Список саджестов пуст')


async def test_stock_exists(tap, dataset):
    with tap.plan(16, 'Сначала раскладываем на полки где уже лежит такой-же'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.full_store()
        await dataset.shelf(store=store, type='store', order=0)
        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        shelf3 = await dataset.shelf(store=store, type='store', order=3)
        await dataset.shelf(store=store, type='store', order=4)

        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=10,
        )

        stock = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=20,
        )
        tap.ok(stock, 'остаток на 2-й полке уже есть')

        await dataset.stock(
            store=store,
            shelf=shelf3,
            product=product3,
            count=30,
        )

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='suggests_generate',
            required = [
                {'product_id': product2.product_id, 'count': 54},
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'request', 'request')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')
        tap.eq(order.shelves, [shelf2.shelf_id], 'Список полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Список саджестов')

        tap.eq(suggests[0].type, 'box2shelf', f'type={suggests[0].type}')
        tap.eq(
            suggests[0].product_id,
            product2.product_id,
            f'product_id={suggests[0].product_id}'
        )
        tap.eq(
            suggests[0].shelf_id,
            shelf2.shelf_id, (
                f'shelf_id={suggests[0].shelf_id} '
                f'- товар идет на полку где уже лежит такой-же товар'
            )
        )
        tap.eq(
            suggests[0].count,
            54,
            f'count={suggests[0].count}'
        )


@pytest.mark.parametrize('shelf_type', ['office', 'markdown'])
async def test_not_suitable_shelves(tap, dataset, shelf_type):
    with tap.plan(11, 'В лавке нет полок раскладки'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        await dataset.shelf(store=store, type=shelf_type)

        order = await dataset.order(
            store=store,
            type = 'stowage',
            status='reserving',
            estatus='suggests_generate',
            required = [
                {'product_id': product1.product_id, 'count': 1},
                {'product_id': product3.product_id, 'count': 3},
                {'product_id': product2.product_id, 'count': 2},
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
