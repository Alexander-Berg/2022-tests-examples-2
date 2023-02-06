from datetime import date

from stall.model.order import Order
from stall.model.stock import Stock
from stall.model.suggest import Suggest


# pylint: disable=too-many-locals, too-many-statements
async def test_create_child(tap, dataset, uuid, wait_order_status):
    with tap.plan(36, 'создание дочернего ордера'):
        product = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store_id=store.store_id)
        await dataset.shelf(store=store, type='lost')
        await dataset.shelf(store=store, type='found')

        stock1 = await dataset.stock(
            product_id=product.product_id,
            count=10,
            reserve=10,
            shelf=shelf,
            valid='2022-01-02',
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            product_id=product.product_id,
            count=9,
            reserve=5,
            shelf=shelf,
            valid='2022-01-02',
            lot=uuid(),
        )

        order = await dataset.order(
            type='check_product_on_shelf',
            products=[product.product_id],
            shelves=[shelf.shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            vars={
                'reserve': True,
            }
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store.store_id, 'на складе')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('request', 'waiting'))
        await order.ack(user)

        await wait_order_status(order, ('processing', 'waiting'))
        await stock2.reload()
        tap.eq_ok(stock2.reserves[order.order_id], 4,
                  'Зарезервировано все, что не было зарезервировано ранее')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=0, valid='2020-01-02'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

            stocks_in_vars = s.vars('stocks')
            stocks_in_vars = {s[0]: s[2] for s in stocks_in_vars}
            tap.eq(stocks_in_vars.get(stock1.stock_id), stock1.count,
                   'stock1 in vars, correct count')
            tap.eq(stocks_in_vars.get(stock2.stock_id), stock2.count,
                   'stock2 in vars, correct count')

            tap.eq(s.result_count, 0, 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'change_prepare'))

        order2 = await dataset.order(store_id=order.store_id)
        tap.ok(await stock1.do_put_exists(order2, 1, reserve=1),
               'положили ещё товара')

        await wait_order_status(order, ('complete', 'done'))

        stocks = await Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=product.product_id,
        )
        stocks = {s.stock_id: s.count for s in stocks}
        tap.eq_ok(stocks.get(stock1.stock_id), 11,
                  'остаток 1 стал на 1 больше')
        tap.eq_ok(stocks.get(stock2.stock_id), 9,
                  'остаток 2 не изменился')
        tap.eq(len(order.problems), 1, 'Одна проблема')
        problem = order.problems[0]
        tap.eq(problem.type, 'stock_changed', 'Тип проблемы правильный')
        tap.eq(problem.shelf_id, stock1.shelf_id, 'Полка правильная')
        tap.eq(problem.product_id, stock1.product_id, 'Продукт тот')

        child_id = order.vars('child.0', None)
        tap.ok(child_id, 'идентификатор дочернего заказа')

        children = await Order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )
        tap.eq(len(children.list), 1, 'появился один дочерний ордер')
        child = children.list[0]
        tap.eq(child.order_id, child_id, 'тот самый ребенок')

        tap.ok(child, 'дочерний загружен')
        tap.eq(child.parent[0], order.order_id, 'parent')
        tap.eq(child.store_id, order.store_id, 'store_id')
        tap.eq(child.type, 'check_product_on_shelf', 'type')
        tap.eq(child.fstatus, ('reserving', 'begin'), 'full status')
        await wait_order_status(
            child, ('reserving', 'find_lost_and_found')
        )
        tap.eq(child.products, [product.product_id], 'продукт')
        tap.eq(child.shelves, [shelf.shelf_id], 'полка')
        tap.eq(child.vars('reserve', False), True, 'child reserve is True')


async def test_not_create_final_check(tap, dataset, wait_order_status, uuid):
    with tap.plan(12, 'проверяем что не создается директорский чек'):
        ps = [await dataset.product() for _ in range(2)]
        store = await dataset.full_store()
        shelf = await dataset.shelf(store=store)
        user = await dataset.user(store=store)
        valid = date(year=2022, month=1, day=1)

        for p in ps:
            await dataset.stock(
                shelf=shelf, product=p, count=123, lot=uuid(), valid=valid
            )

        order = await dataset.order(
            type='check_product_on_shelf',
            store=store,
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': p.product_id,
                }
                for p in ps
            ],
            shelves=[shelf.shelf_id for _ in ps],
            products=[p.product_id for p in ps],
            acks=[user.user_id],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )

        suggests = await Suggest.list_by_order(order)

        tap.eq(len(suggests), 2, '2 саджеста')
        await dataset.stock(
            shelf=shelf, product=ps[1], count=321, lot=uuid(), valid=valid
        )
        for s in suggests:
            if s.product_id == ps[1].product_id:
                continue
            await s.done(count=69, user=user)

        await wait_order_status(
            order, ('complete', 'done'), user_done=user,
        )

        children = await Order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )
        tap.eq(len(children.list), 1, 'появился один дочерний ордер')

        child = children.list[0]
        await wait_order_status(
            child, ('reserving', 'find_lost_and_found'), user_done=user,
        )
        tap.eq(
            child.shelves,
            [shelf.shelf_id],
            'нужные полки',
        )
        tap.eq(
            child.products,
            [ps[1].product_id],
            'нужные продукты',
        )
        tap.eq(child.type, 'check_product_on_shelf', 'нужный тип')
        await wait_order_status(
            child, ('request', 'waiting'), user_done=user,
        )
        tap.ok(await child.ack(user), 'назначили юзера')

        await wait_order_status(
            child, ('complete', 'done'), user_done=user,
        )

        children = await Order.list(
            by='full',
            conditions=('parent', '[1]=', child.order_id),
            sort=(),
        )
        tap.eq(len(children.list), 0, 'нет дочерних ордеров')
