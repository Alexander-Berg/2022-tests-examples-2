# pylint: disable=too-many-locals, too-many-statements

from stall.model.suggest import Suggest


async def test_errors(tap, wait_order_status, dataset, now):
    with tap.plan(41, 'Обновление саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        trash   = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списания')

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        tap.eq(stock1.count, 100, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(product=product2, store=store, count=200)
        tap.eq(stock2.count, 200, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        stock3 = await dataset.stock(product=product3, store=store, count=300)
        tap.eq(stock3.count, 300, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        stock4 = await dataset.stock(product=product4, store=store, count=400)
        tap.eq(stock4.count, 400, 'Остаток 4 положен')
        tap.eq(stock4.reserve, 0, 'Резерва 4 нет')

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='reserve',
            acks=[user.user_id],
            approved=now(),
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
                {
                    'product_id': product4.product_id,
                    'count': 40
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)

        tap.eq(len(suggests), 4, 'Список саджестов shelf2box')
        suggests = dict((x.product_id, x) for x in suggests)

        with suggests[product1.product_id] as suggest:
            tap.ok(await suggest.done(), 'Саджест выполнен')
            suggest.result_count = 5
            tap.ok(await suggest.save(), 'Зафорсили меньшее количество')

        with suggests[product2.product_id] as suggest:
            tap.ok(await suggest.done(), 'Саджест выполнен')

        with suggests[product4.product_id] as suggest:
            tap.ok(await suggest.done(), 'Саджест выполнен')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.done('canceled', user=user), 'Заказ отменен')

        await wait_order_status(order, ('processing', 'suggests_error'))

        tap.ok(
            await order.business.order_changed(),
            'Обработчик запущен'
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3 + 3, 'Список саджестов + откат')

        shelf2box = dict(
            (x.product_id, x) for x in suggests if x.type == 'shelf2box'
        )
        box2shelf = dict(
            (x.product_id, x) for x in suggests if x.type == 'box2shelf'
        )

        with box2shelf[product1.product_id] as suggest:
            parent = shelf2box[suggest.product_id]

            tap.eq(parent.conditions.editable, False, 'Редактировать нельзя')

            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.count, 5, 'Количество возврата')
            tap.eq(suggest.order, -parent.order, 'Обратный порядок')
            tap.eq(suggest.shelf_id, parent.shelf_id, 'Полка')

        with box2shelf[product2.product_id] as suggest:
            parent = shelf2box[suggest.product_id]

            tap.eq(parent.conditions.editable, False, 'Редактировать нельзя')

            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.count, 20, 'Количество возврата')
            tap.eq(suggest.order, -parent.order, 'Обратный порядок')
            tap.eq(suggest.shelf_id, parent.shelf_id, 'Полка')

        with box2shelf[product4.product_id] as suggest:
            parent = shelf2box[suggest.product_id]

            tap.eq(parent.conditions.editable, False, 'Редактировать нельзя')

            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.count, 40, 'Количество возврата')
            tap.eq(suggest.order, -parent.order, 'Обратный порядок')
            tap.eq(suggest.shelf_id, parent.shelf_id, 'Полка')


async def test_result_count(tap, dataset, wait_order_status, now):
    with tap.plan(25, 'Если саджест закрыт на меньшее количество при отмене'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store   = await dataset.store(
            samples = [
                {
                    'product_id': product1.product_id,
                    'mode': 'optional',
                    'count': 1,
                    'tags': ['packaging'],
                },
                {
                    'product_id': product2.product_id,
                    'mode': 'optional',
                    'count': 2,
                    'tags': ['packaging'],
                },
            ],
        )
        user    = await dataset.user(store=store)
        shelf    = await dataset.shelf(store=store, type='store')

        trash    = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списания')

        await dataset.stock(product=product1, shelf=shelf, count=100,)
        await dataset.stock(product=product2, shelf=shelf, count=100,)
        await dataset.stock(product=product3, shelf=shelf, count=100,)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required = [
                {
                    'product_id': product3.product_id,
                    'count': 3,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Саджесты получены')
        suggests = dict(((x.type, x.product_id), x) for x in suggests)

        with suggests['shelf2box', product1.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count=1')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.ok(await suggest.done('done', user=user, count=0), 'закрыт в 0')

        with suggests['shelf2box', product2.product_id] as suggest:
            tap.eq(suggest.count, 2, 'count=2')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.ok(await suggest.done('done', user=user, count=1), 'закрыт -1')

        with suggests['shelf2box', product3.product_id] as suggest:
            tap.eq(suggest.count, 3, 'count=3')
            tap.eq(suggest.result_count, None, 'result_count=None')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.ok(await order.done('canceled', user=user), 'Заказ отменен')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Саджест получен')
        suggests = dict(((x.type, x.product_id), x) for x in suggests)

        with suggests['shelf2box', product1.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count=1')
            tap.eq(suggest.result_count, 0, 'result_count=0')
            tap.eq(suggest.status, 'done', 'done')

        with suggests['shelf2box', product2.product_id] as suggest:
            tap.eq(suggest.count, 2, 'count=2')
            tap.eq(suggest.result_count, 1, 'result_count=1')
            tap.eq(suggest.status, 'done', 'done')

        with suggests['box2shelf', product2.product_id] as suggest:
            tap.eq(suggest.count, 1, 'count=1')
            tap.eq(suggest.result_count, None, 'result_count=none')
            tap.eq(suggest.status, 'request', 'request')

        await wait_order_status(
            order,
            ('canceled', 'done'),
            user_done=user,
        )


async def test_kitchen(tap, dataset, wait_order_status, now):
    with tap.plan(10, 'при отмене заказа приготовленный кофе кладем в треш'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelves, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
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
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        suggests1 = await Suggest.list_by_order(order)

        tap.eq(len(suggests1), 1, 'один саджест')
        tap.eq(suggests1[-1].type, 'shelf2box', 'положи в пакет')
        tap.ok(await suggests1[-1].done(user=user), 'закрываем саджест')
        tap.ok(await order.done('canceled', user=user), 'отменяем заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        suggests2 = await Suggest.list_by_order(order)
        tap.eq(len(suggests2), 2, 'появился обратный саджест')

        suggests2 = {s.type: s for s in suggests2}
        tap.eq(suggests2['shelf2box'].status, 'done', 'первый исполнен')
        tap.eq(
            suggests2['box2shelf'].status, 'request', 'обратный не исполнен',
        )
        tap.eq(
            suggests2['box2shelf'].shelf_id,
            shelves['trash'].shelf_id,
            'полка для списания товара',
        )
