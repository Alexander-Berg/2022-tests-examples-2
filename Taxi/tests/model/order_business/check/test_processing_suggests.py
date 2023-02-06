import pytest

from libstall.util import time2time
from stall.model.stock import Stock
from stall.model.suggest import Suggest


@pytest.mark.parametrize(
    'shelf_type', ['store', 'kitchen_components'],
)
async def test_reserving_one_item(tap, dataset, shelf_type):
    with tap.plan(22, 'саджесты по одному продукту и полке'):
        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        shelves = [
            await dataset.shelf(store=store, order=10-i, type=shelf_type)
            for i in range(3)
        ]
        tap.ok(shelves, 'продукты сгенерированы')

        stocks = [await dataset.stock(shelf=s, count=123) for s in shelves]
        tap.ok(stocks, 'остатки сгенерированы')
        tap.eq([x.store_id for x in stocks],
               [store.store_id]*len(stocks),
               'Все на складе')

        order = await dataset.order(
            type='check',
            products=[stocks[1].product_id],
            shelves=[stocks[1].shelf_id],
            required=[{
                'product_id': stocks[1].product_id,
                'shelf_id': stocks[1].shelf_id,
            }],
            store=store,
            status='processing',
            estatus='suggests_generate',
        )
        version = order.version

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.type, 'check', 'инвентаризация')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'suggests_generate', 'сабстатус')

        tap.ok(await order.business.order_changed(), 'Изменение вызвано')

        tap.ok(await order.reload(), 'перезагружен')

        tap.eq(order.status, 'processing', 'статус заказа изменился')
        tap.eq(order.estatus, 'waiting', 'estatus')
        tap.ok(order.version > version, 'версия увеличилась')

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты получены')
        tap.eq(len(suggests), 1, 'всего один')

        with suggests[0] as s:
            tap.eq(s.product_id, stocks[1].product_id, 'продукт')
            tap.eq(s.shelf_id, shelves[1].shelf_id, 'полка')
            tap.eq(s.shelf_id, stocks[1].shelf_id, 'полка')
            tap.eq(s.vars('stocks.0.0'), stocks[1].stock_id, 'stock_id')
            tap.eq(s.vars('stocks.0.1'), stocks[1].lsn, 'lsn')

            tap.eq(s.count, stocks[1].count, 'количество')
            tap.eq(s.valid, stocks[1].valid, 'срок годности')


@pytest.mark.parametrize(
    'shelf_type', ['store', 'kitchen_components'],
)
async def test_reserving_shelf_2stocks(tap, dataset, uuid, shelf_type):
    with tap.plan(28, 'Несколько стоков на один продукт'):
        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        product = await dataset.product()
        tap.ok(product, 'продукт создан')

        shelves = [
            await dataset.shelf(store=store, order=10-i, type=shelf_type)
            for i in range(3)
        ]
        tap.ok(shelves, 'продукты сгенерированы')

        valids = ['2019-01-02', '2018-02-01', '2020-01-01']

        stocks = [await dataset.stock(shelf_id=shelves[0].shelf_id,
                                      count=123,
                                      product_id=product.product_id,
                                      valid=valids[i],
                                      lot=uuid())
                  for i in range(3)]
        tap.ok(stocks, 'остатки сгенерированы')
        tap.eq(len({x.stock_id for x in stocks}), 3, 'все стоки разные')
        tap.eq([x.store_id for x in stocks],
               [store.store_id]*len(stocks),
               'Все на складе')
        tap.eq({x.product_id for x in stocks},
               {product.product_id},
               'Все на один продукт')

        tap.eq({x.shelf_id for x in stocks},
               {shelves[0].shelf_id},
               'Все на одной полке')

        order = await dataset.order(
            type='check',
            shelves=[shelves[0].shelf_id],
            products=[product.product_id],
            required=[{
               'product_id': product.product_id,
               'shelf_id': shelves[0].shelf_id,
            }],
            store=store,
            status='processing',
            estatus='suggests_generate',
        )

        version = order.version
        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.type, 'check', 'инвентаризация')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'suggests_generate', 'сабстатус')
        tap.ok(order.shelves, 'полки есть')

        tap.ok(await order.business.order_changed(), 'Изменение вызвано')

        tap.ok(await order.reload(), 'перезагружен')

        tap.eq(order.status, 'processing', 'статус заказа изменился')
        tap.eq(order.estatus, 'waiting', 'estatus')
        tap.ok(version < order.version, 'версия увеличилась')

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты получены')
        tap.eq(len(suggests), 1, 'количество саджестов')

        with suggests[0] as s:
            tap.eq(s.type, 'check', 'тип')
            tap.eq(s.shelf_id, shelves[0].shelf_id, 'полка')
            tap.eq(s.count, sum(map(lambda x: x.count, stocks)), 'количество')
            tap.eq(s.valid, min(map(lambda x: x.valid, stocks)), 'СГ')
            tap.eq(s.stock_lsn, None, 'lsn')
            tap.ok(s.conditions.all, 'conditions.all')
            tap.ok(s.conditions.editable, 'conditions.editable')
            tap.ok(s.conditions.need_valid is False, 'conditions.need_valid')


# pylint: disable=too-many-locals
async def test_one_shelf_zero_stocks(
        tap, dataset, uuid, now, wait_order_status,
):
    with tap.plan(29, 'создаем саджесты для 0 стоков'):
        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store')
        tap.ok(shelf, 'полк создана')

        lost = await dataset.shelf(store=store, type='lost')
        tap.ok(lost, 'полка для списания создана')

        found = await dataset.shelf(store=store, type='found')
        tap.ok(found, 'полка для списания создана')

        product1 = await dataset.product()
        tap.ok(product1, 'продукт1 создан')

        product2 = await dataset.product()
        tap.ok(product2, 'продукт2 создан')

        valids = ['2019-01-02', '2018-02-01', '2020-02-01']

        stocks = [
            await dataset.stock(
                count=0,
                shelf_id=shelf.shelf_id,
                product_id=product1.product_id,
                valid=valids[0],
                lot=uuid(),
            ),
            await dataset.stock(
                shelf_id=shelf.shelf_id,
                count=1,
                product_id=product2.product_id,
                valid=valids[1],
                lot=uuid(),
            ),
            await dataset.stock(
                shelf_id=shelf.shelf_id,
                count=2,
                product_id=product2.product_id,
                valid=valids[2],
                lot=uuid(),
            ),
        ]
        tap.ok(stocks, 'остатки сгенерированы')
        tap.eq(
            {x.product_id for x in stocks},
            {product1.product_id, product2.product_id},
            'два товара',
        )

        tap.eq(
            {x.shelf_id for x in stocks},
            {shelf.shelf_id},
            'оба на одной полке',
        )

        order = await dataset.order(
            type='check',
            products=[product1.product_id, product2.product_id],
            shelves=[shelf.shelf_id],
            required=[
                {
                    'product_id': product2.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': product1.product_id,
                    'shelf_id': shelf.shelf_id,
                }
            ],
            store=store,
            acks=[user.user_id],
            approved=now(),
            status='reserving',
            estatus='begin',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'перезагружен')

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты получены')
        tap.eq(len(suggests), 2, 'количество саджестов')

        suggests = sorted(suggests, key=lambda item: item.count)

        with suggests[0] as s:
            tap.eq(s.type, 'check', 'тип')
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.eq(s.product_id, product1.product_id, 'товар')
            tap.eq(s.valid, time2time('2019-01-02').date(), 'сг')
            tap.eq(s.stock_lsn, None, 'lsn')
            tap.ok(s.conditions.all, 'conditions.all')
            tap.ok(s.conditions.editable, 'conditions.editable')
            tap.ok(s.conditions.need_valid is False, 'conditions.need_valid')

        with suggests[1] as s:
            tap.eq(s.type, 'check', 'тип')
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.eq(s.product_id, product2.product_id, 'товар')
            tap.eq(s.valid, time2time('2018-02-01').date(), 'сг')
            tap.eq(s.stock_lsn, None, 'lsn')
            tap.ok(s.conditions.all, 'conditions.all')
            tap.ok(s.conditions.editable, 'conditions.editable')
            tap.ok(s.conditions.need_valid is False, 'conditions.need_valid')


async def test_products_no_stocks(tap, dataset, wait_order_status):
    with tap.plan(10, 'создаем саджест на товары без остатка'):
        store = await dataset.store()

        product1 = await dataset.product()
        shelf = await dataset.shelf(store=store, type='store')
        await dataset.stock(store=store, product=product1)
        product1_stocks = await Stock.list_by_product(
            product_id=product1.product_id,
            store_id=store.store_id,
            shelf_id=shelf.shelf_id,
        )

        tap.ok(not product1_stocks, 'нет остатка на товар1')

        product2 = await dataset.product()
        product2_stocks = await Stock.list_by_product(
            product_id=product2.product_id,
            store_id=store.store_id,
            shelf_id=shelf.shelf_id,
        )
        tap.ok(not product2_stocks, 'нет остатка на товар2')

        order = await dataset.order(
            store_id=store.store_id,
            type='check',
            status='processing',
            estatus='begin',
            products=[product1.product_id, product2.product_id],
            shelves=[shelf.shelf_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': product2.product_id,
                    'shelf_id': shelf.shelf_id,
                }
            ]

        )

        tap.ok(order, 'ордер создан')
        tap.eq(order.status, 'processing', 'status')
        tap.eq(order.estatus, 'begin', 'estatus')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'перегружен')

        suggests = await Suggest.list_by_order(order)

        tap.eq(len(suggests), 2, 'количество саджестов')
        tap.ok(
            all(suggest.type == 'check' for suggest in suggests),
            'Все саджесты check'
        )
        tap.eq(
            {suggest.product_id for suggest in suggests},
            {product1.product_id, product2.product_id},
            'Оба продукта в саджестах'
        )


async def test_required_only_product(tap, dataset, uuid, wait_order_status):
    with tap.plan(8, 'проверяем поиск полок'):
        store = await dataset.full_store()
        ps = [await dataset.product() for _ in range(2)]
        user = await dataset.user(store=store)

        shelf_ok1 = await dataset.shelf(store=store)
        shelf_ok2 = await dataset.shelf(store=store)
        shelf_bad = await dataset.shelf(store=store, type='trash')

        stock_bad = await dataset.stock(
            store=store,
            shelf=shelf_bad,
            lot=uuid(),
            product=ps[1],
            count=123,
        )
        tap.ok(stock_bad, 'сток не найдется, полка плохая')
        stock_ok1_0_1 = await dataset.stock(
            store=store,
            shelf=shelf_ok1,
            lot=uuid(),
            product=ps[0],
            count=0,
        )
        tap.ok(stock_ok1_0_1, 'нулевой сток, полка 1, продукт 0')
        stock_ok1_0_2 = await dataset.stock(
            store=store,
            shelf=shelf_ok1,
            lot=uuid(),
            product=ps[1],
            count=0,
        )
        tap.ok(stock_ok1_0_2, 'нулевой сток, полка 1, продукт 1')
        stock_ok2_1_1 = await dataset.stock(
            store=store,
            shelf=shelf_ok2,
            lot=uuid(),
            product=ps[1],
            count=60,
        )
        tap.ok(stock_ok2_1_1, 'сток на 60, полка 2')
        stock_ok2_1_2 = await dataset.stock(
            store=store,
            shelf=shelf_ok2,
            lot=uuid(),
            product=ps[1],
            count=9,
        )
        tap.ok(stock_ok2_1_2, 'сток на 9, полка 2')

        order = await dataset.order(
            type='check',
            store=store,
            required=[
                {'product_id': p.product_id}
                for p in ps
            ],
            acks=[user.user_id],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user
        )
        suggests = await Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 3, '3 саджеста')
        suggest_params = {
            (s.shelf_id, s.product_id, s.count)
            for s in suggests
        }
        expected_params = {
            (shelf_ok1.shelf_id, ps[0].product_id, 0),
            (shelf_ok1.shelf_id, ps[1].product_id, 0),
            (shelf_ok2.shelf_id, ps[1].product_id, 69),
        }
        tap.eq(suggest_params, expected_params, 'нужные саджесты')


async def test_check_vars_shelf_types(tap, dataset, wait_order_status):
    with tap.plan(15, 'тестим подтягивание shelf_types из варсов'):
        store = await dataset.store()
        stock_store = await dataset.stock(store=store)
        stock_office = await dataset.stock(store=store, shelf_type='office')
        user = await dataset.user(store=store)
        orders = [
            await dataset.order(
                type='check',
                store=store,
                required=[
                    {'product_id': stock_store.product_id},
                    {'product_id': stock_office.product_id},
                ],
                vars={'shelf_types': st},
            )
            for st in ([], ['store'], ['fake_shelf_type'])
        ]

        all_order = orders[0]
        store_order = orders[1]
        fail_order = orders[2]

        await wait_order_status(all_order, ('request', 'waiting'))
        await all_order.ack(user)
        await wait_order_status(
            all_order, ('processing', 'suggests_generate'), user_done=user,
        )
        await wait_order_status(
            all_order, ('processing', 'waiting'), user_done=user,
        )
        suggests = await dataset.Suggest.list_by_order(all_order)
        tap.eq(len(suggests), 2, 'два саджеста')
        tap.eq(
            {s.shelf_id for s in suggests},
            {stock_store.shelf_id, stock_office.shelf_id},
            'все полки',
        )
        await wait_order_status(
            all_order, ('complete', 'done'), user_done=user,
        )

        await wait_order_status(store_order, ('request', 'waiting'))
        await store_order.ack(user)
        await wait_order_status(
            store_order, ('processing', 'suggests_generate'), user_done=user,
        )
        await wait_order_status(
            store_order, ('processing', 'waiting'), user_done=user,
        )
        suggests = await dataset.Suggest.list_by_order(store_order)
        tap.eq(len(suggests), 1, 'один саджеста')
        tap.eq(suggests[0].shelf_id, stock_store.shelf_id, 'store полка')
        await wait_order_status(
            store_order, ('complete', 'done'), user_done=user,
        )

        await wait_order_status(fail_order, ('request', 'waiting'))
        await fail_order.ack(user)
        await wait_order_status(
            fail_order, ('processing', 'suggests_generate'), user_done=user,
        )
        with tap.raises(AssertionError):
            await wait_order_status(
                fail_order, ('processing', 'waiting'), user_done=user,
            )
