# pylint: disable=too-many-locals,too-many-statements,invalid-name
from libstall.util import now
from stall.model.stock import Stock


async def test_products_reserve(tap, dataset, uuid):
    with tap.plan(16, 'Резервирование всех продуктов на полке'):

        product = await dataset.product(valid=10)

        store = await dataset.store()

        shelf = await dataset.shelf(store=store, type='store')
        trash = await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status = 'processing',
            estatus='products_reserve',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'products_reserve', 'products_reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=7,
            lot=uuid(),
        )
        tap.ok(stock1, f'Остаток 1: {stock1.stock_id}')

        stock2 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product,
            count=18,
            lot=uuid(),
        )
        tap.ok(stock2, f'Остаток 2: {stock2.stock_id}')

        stock3 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product,
            count=13,
            lot=uuid(),
        )
        tap.ok(stock3, f'Остаток 3: {stock3.stock_id}')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        reserved = await Stock.list_by_order(order)
        tap.eq(
            sorted([x.stock_id for x in reserved]),
            sorted([x.stock_id for x in (stock2, stock3)]),
            'Зарезервированы все продукты на полке списания'
        )

        with await stock1.reload() as stock:
            tap.eq(stock.reserve, 0, 'Не резервировался')

        with await stock2.reload() as stock:
            tap.eq(stock.reserve, 18, 'Зарезервирован весь остаток')

        with await stock3.reload() as stock:
            tap.eq(stock.reserve, 13, 'Зарезервирова весь остаток')


async def test_products_reserve_from_shelves(tap, dataset, wait_order_status):
    with tap.plan(12, 'Резервирование с указанных полок'):

        product = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)

        trash1 = await dataset.shelf(store=store, type='trash')
        trash2 = await dataset.shelf(store=store, type='trash')

        stock1 = await dataset.stock(
            store=store,
            shelf=trash1,
            product=product,
            count=18,
        )
        tap.ok(stock1, f'Остаток: {stock1.stock_id}')

        stock2 = await dataset.stock(
            store=store,
            shelf=trash2,
            product=product,
            count=13,
        )
        tap.ok(stock2, f'Остаток: {stock2.stock_id}')

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status = 'reserving',
            estatus='begin',
            shelves=[trash2.shelf_id],
            acks=[user.user_id],
            approved=now(),
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('processing', 'products_reserve'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'products_reserve', 'products_reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        await order.business.order_changed()

        reserved = await Stock.list_by_order(order)
        tap.eq(
            sorted([x.stock_id for x in reserved]),
            sorted([x.stock_id for x in (stock2,)]),
            'Зарезервированы все продукты на указанной полке списания'
        )

        with await stock1.reload() as stock:
            tap.eq(stock.reserve, 0, 'Не резервировался')

        with await stock2.reload() as stock:
            tap.eq(stock.reserve, 13, 'Зарезервирован весь остаток')
