import pytest

from stall.model.suggest import Suggest


# pylint: disable=too-many-locals
async def test_child_reserved(tap, dataset, wait_order_status, uuid):
    with tap.plan(23, 'Зарезервировано, поэтому дочерний ордер'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        first_stock = await dataset.stock(
            count=27,
            reserve=11,
            valid='1999-12-20',
            store_id=store.store_id,
            lot=uuid(),
        )
        tap.eq(first_stock.store_id, store.store_id, 'остаток создан')
        tap.ok(first_stock.reserve, 'резерв есть')
        second_stock = await dataset.stock(
            count=33,
            valid='1999-12-21',
            store_id=store.store_id,
            product_id=first_stock.product_id,
            shelf_id=first_stock.shelf_id,
            lot=uuid(),
        )
        tap.ok(second_stock, 'Остаток на той же полке без резерва')
        third_stock = await dataset.stock(
            count=43,
            valid='1999-12-22',
            store_id=store.store_id
        )
        tap.ok(third_stock, 'Третий остаток доступный')

        order = await dataset.order(
            store=store,
            status='reserving',
            estatus='begin',
            shelves=[first_stock.shelf_id, third_stock.shelf_id],
            type='check_more',
            acks=[user.user_id],
            attr={'request_type': 'smth'},
        )

        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'Саджесты получены')

        for s in suggests:
            tap.ok(await s.done(status='error'), f'завершили саджест {s.type}')
        tap.ok(await order.done(target='complete', user=user), 'ордер завершён')

        await wait_order_status(order, ('complete', 'done'))

        await order.reload()

        tap.ok(order.vars('child'), 'Появился дочерний ордер')
        child = await order.load(order.vars('child')[0])

        tap.eq(
            child.fstatus,
            ('reserving', 'begin'),
            'Дочерний ордер в начале'
        )
        tap.eq(
            {(r.shelf_id, r.product_id) for r in child.required},
            {(first_stock.shelf_id, first_stock.product_id)},
            'Правильный реквайред'
        )

        tap.eq(len(order.problems), 1, 'одна найденная проблема')
        with order.problems[0] as p:
            tap.eq(p.type, 'product_reserved', 'Товар зарезервирован')
            tap.eq(p.product_id, first_stock.product_id, 'идентификатор товара')
            tap.eq(p.reserve, first_stock.reserve, 'количество резерва')
            tap.eq(p.stock_id, first_stock.stock_id, 'на каком стоке')

        tap.eq(
            child.attr['request_type'],
            order.attr['request_type'],
            'прокидываем request_type',
        )

        stocks = dataset.Stock.ilist(
            by='look',
            conditions=[
                ('store_id', store.store_id),
                ('shelf_type', 'store'),
            ]
        )
        tap.eq(
            {
                (stock.stock_id, stock.count)
                async for stock in stocks
            },
            {
                (first_stock.stock_id, 27),
                (second_stock.stock_id, 33),
                (third_stock.stock_id, 0),
            },
            'Остатки поменялись только по нерезервированному продукту'
        )


async def test_stock_changed(tap, dataset, wait_order_status):
    with tap.plan(22, 'Изменили остаток во время выполнения'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(
            count=27,
            valid='1999-12-20',
            store_id=store.store_id,
        )
        tap.ok(stock, 'остаток создали')

        second_stock = await dataset.stock(
            count=33,
            valid='1999-12-21',
            store_id=store.store_id,
            product_id=stock.product_id,
        )

        order = await dataset.order(
            store=store,
            status='reserving',
            estatus='begin',
            shelves=[stock.shelf_id, second_stock.shelf_id],
            type='check_more',
            acks=[user.user_id],
            attr={'request_type': 'smth'},
        )

        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('processing', 'waiting'))

        reserve_order = await dataset.order(
            store=store,
            status='complete',
            estatus='done'
        )

        tap.ok(await stock.do_reserve(reserve_order, 10), 'зарезервировали')
        tap.ok(await stock.do_unreserve(reserve_order), 'сняли резерв')

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'Саджесты получены')

        for s in suggests:
            tap.ok(await s.done(status='error'), f'завершили саджест {s.type}')
        tap.ok(await order.done(target='complete', user=user), 'ордер завершён')

        await wait_order_status(order, ('complete', 'done'))

        await order.reload()

        tap.ok(order.vars('child'), 'Появился дочерний ордер')
        child = await order.load(order.vars('child')[0])

        tap.eq(
            child.fstatus,
            ('reserving', 'begin'),
            'Дочерний ордер в начале'
        )
        tap.eq(
            {(r.shelf_id, r.product_id) for r in child.required},
            {(stock.shelf_id, stock.product_id)},
            'Правильный реквайред'
        )

        tap.eq(len(order.problems), 1, 'одна найденная проблема')
        problem = order.problems[0]

        tap.eq(problem.type, 'stock_changed', 'Товар зарезервирован')
        tap.eq(problem.product_id, stock.product_id, 'идентификатор товара')
        tap.eq(problem.reserve, stock.reserve, 'количество резерва')
        tap.eq(problem.stock_id, stock.stock_id, 'на каком стоке')

        tap.eq(
            child.attr['request_type'],
            order.attr['request_type'],
            'прокидываем request_type',
        )

        stocks = dataset.Stock.ilist(
            by='look',
            conditions=[
                ('store_id', store.store_id),
                ('shelf_type', 'store'),
            ]
        )
        tap.eq(
            {
                (stock.stock_id, stock.count)
                async for stock in stocks
            },
            {
                (stock.stock_id, 27),
                (second_stock.stock_id, 0),
            },
            'Остатки поменялись только по не продукту',
        )


@pytest.mark.parametrize('shelf_types, problem_shelves, desc', [
    (
        ['store'],
        {'lost', 'found'},
        {'desc': 'Проверяем store', 'count': 7},
    ),
    (
        ['kitchen_components'],
        {'kitchen_lost', 'kitchen_found'},
        {'desc': 'Проверяем компоненты', 'count': 7},
    ),
    (
        ['store', 'kitchen_components'],
        {'kitchen_lost', 'kitchen_found', 'lost', 'found'},
        {'desc': 'Все типы полок', 'count': 8},
    )
])
async def test_fail_shelf(
        tap, dataset, wait_order_status, shelf_types, problem_shelves, desc):
    with tap.plan(desc['count'], desc['desc']):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        shelves = []
        for shelf_type in shelf_types:
            shelf = await dataset.shelf(type=shelf_type, store=store)
            tap.eq(
                shelf.store_id,
                store.store_id,
                f'Создана полка {shelf_type}'
            )
            shelves.append(shelf.shelf_id)

        order = await dataset.order(
            store=store,
            status='reserving',
            estatus='begin',
            shelves=shelves,
            type='check_more',
            acks=[user.user_id],
        )

        await wait_order_status(order, ('failed', 'done'))
        await order.reload()

        tap.eq(
            len(order.problems),
            len(problem_shelves),
            'Найдено нужное количество проблем'
        )
        tap.ok(
            all(p.type == 'shelf_not_found' for p in order.problems),
            'Все типы проблем shelf_not_found'
        )
        tap.eq(
            {p.shelf_type for p in order.problems},
            problem_shelves,
            'В проблемах правильные типы полок'
        )
