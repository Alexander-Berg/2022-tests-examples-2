from datetime import date
import pytest


@pytest.mark.parametrize('shelf_type', ['store', 'repacking'])
async def test_workflow(tap, dataset, wait_order_status, uuid, shelf_type):
    with tap.plan(20, 'Обычный воркфлоу'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        shelf1 = await dataset.shelf(store=store, type='store')

        stock1 = await dataset.stock(
            store=store, count=37, reserve=1, shelf=shelf1)
        tap.eq(stock1.store_id, store.store_id, 'остаток 1')

        stock2 = await dataset.stock(store=store,
                                     count=45,
                                     shelf=shelf1,
                                     product_id=stock1.product_id,
                                     valid=date.today(),
                                     lot=uuid(),
                                     reserve=2)
        tap.eq(stock2.store_id, store.store_id, 'остаток 2')
        tap.eq(stock2.product_id, stock1.product_id, 'товар')
        tap.ne(stock2.stock_id, stock1.stock_id, 'остатки разные')
        tap.eq(stock2.shelf_id, stock1.shelf_id, 'полка та же')

        shelf = await dataset.shelf(store=store, type=shelf_type)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='hand_move',
            required=[
                {
                    'product_id': stock1.product_id,
                    'count': 54,
                    'src_shelf_id': stock1.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            await s.done()
        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 2, 'два стока зарезервировано')
        tap.eq(
            sum(s.reserves.get(order.order_id, 0) for s in stocks),
            54,
            'зарезервировано итого'
        )

        tap.eq(
            sum(s.reserve for s in stocks),
            54 + 1 + 2,
            'зарезервировано на все ордера'
        )

        await wait_order_status(order, ('complete', 'begin'), user_done=user)
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(
            len(await dataset.Stock.list_by_order(order)),
            0,
            'резервов на ордере нет'
        )

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=shelf.store_id,
        )
        tap.eq(sum(s.count for s in stocks), 54, 'положено на полку')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=stock1.shelf_id,
            store_id=shelf.store_id,
        )
        tap.eq(
            sum(s.count for s in stocks),
            37 + 45 - 54,
            'Осталось на предыдущей'
        )


async def test_2to1(tap, dataset, wait_order_status, uuid):
    with tap.plan(24, 'Обычный воркфлоу с двух полок на 1'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        stock1 = await dataset.stock(store=store, count=37, reserve=1)
        tap.eq(stock1.store_id, store.store_id, 'остаток 1')

        stock2 = await dataset.stock(store=store,
                                     count=45,
                                     product_id=stock1.product_id,
                                     lot=uuid(),
                                     reserve=2)
        tap.eq(stock2.store_id, store.store_id, 'остаток 2')
        tap.eq(stock2.product_id, stock1.product_id, 'товар')
        tap.ne(stock2.stock_id, stock1.stock_id, 'остатки разные')
        tap.ne(stock2.shelf_id, stock1.shelf_id, 'Полки разные')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='hand_move',
            required=[
                {
                    'product_id': stock1.product_id,
                    'count': 34,
                    'src_shelf_id': stock1.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': stock2.product_id,
                    'count': 43,
                    'src_shelf_id': stock2.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')
        for s in suggests:
            await s.done()
        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )

        tap.eq(
            sum(s.count for s in suggests if s.type == 'shelf2box'),
            43 + 34,
            'Количество забираемых с полок товаров'
        )

        tap.eq(
            sum(s.count for s in suggests if s.type == 'box2shelf'),
            0,
            'Количество товаров для покладки в dst'
        )

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'саджестов стало 3')
        s_box2shelf = [s for s in suggests if s.type == 'box2shelf']
        tap.eq(len(s_box2shelf), 1, 'один саджест box2shelf')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.ok(await stock1.reload(), 'остаток 1 перегружен')
        tap.eq(stock1.count, 37 - 34, 'количество на остатке 1')
        tap.ok(await stock2.reload(), 'остаток 2 перегружен')
        tap.eq(stock2.count, 45 - 43, 'количество на остатке 2')

        stocks = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=shelf.shelf_id
        )
        tap.ok(stocks, 'остатки на полке загружены')

        tap.eq(
            sum(s.count for s in stocks),
            43 + 34,
            'количество'
        )

        tap.eq(
            sum(s.reserve for s in stocks),
            0,
            'резерва нет'
        )


async def test_diff_result_count(tap, dataset, wait_order_status, uuid):
    # pylint: disable=too-many-locals
    with tap.plan(18, 'нормальный флоу с закрытием на меньший count'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        products = [await dataset.product() for _ in range(2)]
        shelves = [await dataset.shelf(store=store) for _ in range(4)]
        stock00 = await dataset.stock(
            store=store,
            shelf=shelves[0],
            product=products[0],
            count=50,
            lot=uuid(),
        )
        stock01 = await dataset.stock(
            store=store,
            shelf=shelves[0],
            product=products[0],
            count=50,
            lot=uuid(),
        )
        stock10 = await dataset.stock(
            store=store,
            shelf=shelves[1],
            product=products[1],
            count=100,
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='hand_move',
            required=[
                {
                    'product_id': products[0].product_id,
                    'count': 33,
                    'src_shelf_id': shelves[0].shelf_id,
                    'dst_shelf_id': shelves[1].shelf_id,
                },
                {
                    'product_id': products[0].product_id,
                    'count': 33,
                    'src_shelf_id': shelves[0].shelf_id,
                    'dst_shelf_id': shelves[2].shelf_id,
                },
                {
                    'product_id': products[0].product_id,
                    'count': 33,
                    'src_shelf_id': shelves[0].shelf_id,
                    'dst_shelf_id': shelves[3].shelf_id,
                },
                {
                    'product_id': products[1].product_id,
                    'count': 69,
                    'src_shelf_id': shelves[1].shelf_id,
                    'dst_shelf_id': shelves[3].shelf_id,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'один саджест')
        shelf2box_suggest0 = [
            s
            for s in suggests
            if s.product_id == products[0].product_id
        ][0]
        shelf2box_suggest1 = [
            s
            for s in suggests
            if s.product_id == products[1].product_id
        ][0]
        await stock00.reload()
        await stock01.reload()
        await stock10.reload()
        tap.eq(
            sum(s.reserves[order.order_id] for s in [stock00, stock01]),
            99,
            'зарезервировали 99'
        )
        tap.eq(
            stock10.reserves[order.order_id], 69, 'зарезервировали 69 (nice)'
        )

        await shelf2box_suggest0.done(user=user, count=31)
        await shelf2box_suggest1.done(user=user, count=31)
        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )
        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user
        )
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'саджесты box2shelf подъехали')
        s_box2shelf = [s for s in suggests if s.type == 'box2shelf']
        tap.eq(len(s_box2shelf), 2, 'два саджеста box2shelf')
        s_box2shelf0 = [
            s
            for s in s_box2shelf
            if s.product_id == products[0].product_id
        ][0]
        s_box2shelf1 = [
            s
            for s in s_box2shelf
            if s.product_id == products[1].product_id
        ][0]
        tap.eq(s_box2shelf0.count, 31, 'переносим 31 единицу')
        tap.eq(s_box2shelf1.count, 31, 'переносим 31 единицу')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        suggests = await dataset.Suggest.list_by_order(order)
        tap.ok(not suggests, 'саджестов нет')
        await stock00.reload()
        await stock01.reload()
        await stock10.reload()
        tap.eq(sum(s.count for s in [stock00, stock01]), 69, 'nice')
        tap.eq(stock10.count, 69, 'nice')
        tap.ok(not stock00.reserve, 'ничего не зарезервировано')
        tap.ok(not stock01.reserve, 'ничего не зарезервировано')
        tap.ok(not stock10.reserve, 'ничего не зарезервировано')
        stocks = (await dataset.Stock.list(
            by='full',
            conditions=(
                ('shelf_id', [s.shelf_id for s in shelves[1:]]),
                ('product_id', products[0].product_id),
            ),
            sort=(),
        )).list
        s0 = [s for s in stocks if s.count == 0]
        s31 = [s for s in stocks if s.count == 31]
        tap.eq(len(s0) + len(s31), len(stocks), '0 или 31')
        tap.eq(len(s31), 1, 'закинули все на одну полку')


async def test_many_products_one_shelf(tap, dataset, wait_order_status, uuid):
    with tap.plan(4, 'тестируем кейс с кучей товаров на одной полке'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        shelf1 = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store)
        ps = [await dataset.product() for _ in range(3)]
        stocks = [
            await dataset.stock(
                store=store,
                shelf=shelf1,
                product=p,
                count=10 - i,
                lot=uuid(),
            )
            for i, p in enumerate(ps)
        ]

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='hand_move',
            required=[
                {
                    'product_id': p.product_id,
                    'count': 10 - i,
                    'src_shelf_id': shelf1.shelf_id,
                    'dst_shelf_id': shelf2.shelf_id,
                }
                for i, p in enumerate(ps)
            ],
        )

        await wait_order_status(order, ('request', 'waiting'))
        for i, stock in enumerate(stocks):
            await stock.reload()
            tap.eq(stock.reserves[order.order_id], 10-i, 'нужный остаток')


async def test_trash_reason(tap, dataset, wait_order_status):
    with tap.plan(10, 'указываем причину при перемещении на треш'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        shelf1 = await dataset.shelf(store=store, type='store')

        stock1 = await dataset.stock(
            store=store, count=73, shelf=shelf1)
        tap.eq(stock1.store_id, store.store_id, 'остаток 1')

        shelf = await dataset.shelf(store=store, type='trash')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='hand_move',
            required=[
                {
                    'product_id': stock1.product_id,
                    'count': 73,
                    'src_shelf_id': stock1.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            await s.done()
        await order.signal(
            {'type': 'next_stage'},
            user=user,
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=shelf.store_id,
        )

        tap.eq(sum(s.count for s in stocks), 73, 'положено на полку')
        tap.eq(
            stocks[0].vars['reasons'][0][order.order_id]['reason_code'],
            'TRASH_DECAYED',
            'причина есть'
        )
