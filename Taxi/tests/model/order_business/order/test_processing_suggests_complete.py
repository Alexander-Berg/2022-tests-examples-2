# pylint: disable=too-many-locals, too-many-statements
from stall.model.order import Order
from stall.model.suggest import Suggest


async def test_suggests_complete(tap, wait_order_status, dataset, now):
    with tap.plan(18, 'Простой проход без измененеий остатков'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store)
        user    = await dataset.user(store=store)

        await dataset.stock(product=product1, shelf=shelf, count=10)
        await dataset.stock(product=product2, shelf=shelf, count=20)
        await dataset.stock(product=product3, shelf=shelf, count=30)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
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
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(
            order.estatus,
            'suggests_kitchen_complete',
            'suggests_kitchen_complete',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(
            sorted(order.shelves),
            sorted([shelf.shelf_id]),
            'полки'
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict(((x.shelf_id, x.product_id), x) for x in suggests)

        with suggests[shelf.shelf_id, product1.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count')
            tap.eq(suggest.valid, None, 'valid')
            tap.eq(suggest.vars('mode'), 'product', 'product')

        with suggests[shelf.shelf_id, product2.product_id] as suggest:
            tap.eq(suggest.count, 2, 'count')
            tap.eq(suggest.valid, None, 'valid')
            tap.eq(suggest.vars('mode'), 'product', 'product')

        with suggests[shelf.shelf_id, product3.product_id] as suggest:
            tap.eq(suggest.count, 3, 'count')
            tap.eq(suggest.valid, None, 'valid')
            tap.eq(suggest.vars('mode'), 'product', 'product')


async def test_update(tap, dataset):
    with tap.plan(31, 'Обновление саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        tap.eq(stock1.count, 100, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(product=product2, store=store, count=200)
        tap.eq(stock2.count, 200, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        stock3 = await dataset.stock(product=product3, store=store, count=300)
        tap.eq(stock3.count, 300, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        request = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='reserve',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
                {
                    'product_id': product3.product_id,
                    'count': 30
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
            ],
        )
        tap.ok(request, 'Заказ создан')
        tap.ok(await request.business.reserve(), 'Резервирование')
        tap.ok(await request.business.suggests_generate(), 'Резервирование')

        suggests = await Suggest.list_by_order(request)
        tap.eq(len(suggests), 3, 'Список саджестов')

        suggest1 = list(filter(
            lambda x: x.product_id == product1.product_id, suggests
        ))[0]
        tap.ok(await suggest1.rm(), 'Имитация: Саджест 1 удален')

        suggest2 = list(filter(
            lambda x: x.product_id == product2.product_id, suggests
        ))[0]
        suggest2.count = 4
        tap.ok(await suggest2.save(), 'Имитация: Саджест 2 изменен')

        request.rehash(status='processing', estatus='suggests_complete')
        tap.ok(await request.save(), 'Заказ переведен в статус')

        order = await Order.load(request.order_id)
        tap.ok(request, 'Заказ получен')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_complete', 'suggests_complete')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(
            sorted(order.shelves),
            sorted([stock1.shelf_id, stock2.shelf_id, stock3.shelf_id]),
            'полки'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(
            order.estatus,
            'suggests_kitchen_complete',
            'suggests_kitchen_complete',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.eq(
            sorted(order.shelves),
            sorted([stock1.shelf_id, stock2.shelf_id, stock3.shelf_id]),
            'полки'
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict((x.product_id, x) for x in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.count, 10, f'Саджест 1 создан {suggest.order}')
            tap.eq(suggest.vars('mode'), 'product', 'product')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.count, 20,
                   f'Саджест 2 отредактирован {suggest.order}')
            tap.eq(suggest.vars('mode'), 'product', 'product')

        with suggests[product3.product_id] as suggest:
            tap.eq(suggest.count, 30, f'Саджест 3 не менялся {suggest.order}')
            tap.eq(suggest.vars('mode'), 'product', 'product')


async def test_kitchen(tap, dataset, wait_order_status, now):
    with tap.plan(6):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 2),
                ('comp', 'glass1', 3),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 2,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'processing', 'processing')
        tap.eq(
            order.estatus,
            'suggests_kitchen_complete',
            'suggests_kitchen_complete',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'саджесты на месте')
