# pylint: disable=too-many-statements,too-many-locals,too-many-lines

from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def test_waiting(tap, dataset, now, wait_order_status):
    with tap.plan(27, 'Сборка заказа - простое исполнение'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store, count=100)
        await dataset.stock(product=product2, store=store, count=200)
        await dataset.stock(product=product3, store=store, count=300)

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
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 2, 'Остатки')

        with stocks[product1.product_id] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 10, 'Зарезервировано')

        with stocks[product2.product_id] as stock:
            tap.eq(stock.count, 200, 'Остаток')
            tap.eq(stock.reserve, 20, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict((x.product_id, x) for x in suggests)
        tap.eq(len(suggests), 2, 'Саджесты')

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'shelf2box')
            tap.eq(suggest.count, 10, 'Количество')
            tap.ok(await suggest.done('done'), 'Саджест выполнен')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'shelf2box')
            tap.eq(suggest.count, 20, 'Количество')
            tap.ok(await suggest.done('done'), 'Саджест выполнен')

        await order.business.order_changed()

        tap.ok(
            await order.done('complete', user=user),
            'Подтвердим завершение заказа'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_waiting_update(tap, dataset, now, wait_order_status):
    with tap.plan(45, 'Сборка заказа - пришли изменения'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        product5 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store, count=100)
        await dataset.stock(product=product2, store=store, count=200)
        await dataset.stock(product=product3, store=store, count=300)
        await dataset.stock(product=product4, store=store, count=400)
        await dataset.stock(product=product5, store=store, count=500)

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
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
                {
                    'product_id': product4.product_id,
                    'count': 40
                },
                {
                    'product_id': product5.product_id,
                    'count': 50
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Саджесты на сборку')
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)

        with suggests[(product1.product_id, 'shelf2box', 10)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product2.product_id, 'shelf2box', 20)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product4.product_id, 'shelf2box', 40)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product5.product_id, 'shelf2box', 50)] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем выполнять')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        order.vars['required'] = [
            {
                'product_id': product1.product_id,
                'count': 11,
            },
            {
                'product_id': product2.product_id,
                'count': 2,
            },
            {
                'product_id': product3.product_id,
                'count': 30
            },
        ]
        tap.ok(await order.save(), 'Пришло изменение по продуктам')

        tap.ok(
            await order.business.order_changed(),
            'Обработка измненений в заказе'
        )
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok('required' in order.vars, 'Изменения ждут применения')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok('required' not in order.vars, 'Изменения применены и удалены')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 3, 'Остатки')

        with stocks[product1.product_id] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 11, 'Зарезервировано')

        with stocks[product2.product_id] as stock:
            tap.eq(stock.count, 200, 'Остаток')
            tap.eq(stock.reserve, 2, 'Зарезервировано')

        with stocks[product3.product_id] as stock:
            tap.eq(stock.count, 300, 'Остаток')
            tap.eq(stock.reserve, 30, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)
        tap.eq(len(suggests), 7, 'Саджесты')

        with suggests[(product1.product_id, 'shelf2box', 10)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product1.product_id, 'shelf2box', 1)] as suggest:
            tap.eq(suggest.status, 'request', 'Новый саджест добора')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product2.product_id, 'shelf2box', 20)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product2.product_id, 'box2shelf', 18)] as suggest:
            tap.eq(suggest.status, 'request', 'Новый возврата')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product3.product_id, 'shelf2box', 30)] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест для нового продукта')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product4.product_id, 'shelf2box', 40)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product4.product_id, 'box2shelf', 40)] as suggest:
            tap.eq(suggest.status, 'request', 'Полный возврат')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        await order.business.order_changed()
        tap.ok(
            await order.done('complete', user=user),
            'Подтвердим завершение заказа'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_waiting_double_update(tap, dataset, now, wait_order_status):
    with tap.plan(83, 'Сборка заказа - несколько раз пришли изменения'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        product5 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store, count=100)
        await dataset.stock(product=product2, store=store, count=200)
        await dataset.stock(product=product3, store=store, count=300)
        await dataset.stock(product=product4, store=store, count=400)
        await dataset.stock(product=product5, store=store, count=500)

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
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
                {
                    'product_id': product4.product_id,
                    'count': 40
                },
                {
                    'product_id': product5.product_id,
                    'count': 50
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Саджесты на сборку')
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)

        with suggests[(product1.product_id, 'shelf2box', 10)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product2.product_id, 'shelf2box', 20)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product4.product_id, 'shelf2box', 40)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product5.product_id, 'shelf2box', 50)] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем выполнять')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        # 1 изменение
        order.vars['required'] = [
            {
                'product_id': product1.product_id,
                'count': 11,
            },
            {
                'product_id': product2.product_id,
                'count': 2,
            },
            {
                'product_id': product3.product_id,
                'count': 30
            },
            {
                'product_id': product5.product_id,
                'count': 50
            },
        ]
        tap.ok(await order.save(), 'Пришло 1 изменение по продуктам')

        tap.ok(
            await order.business.order_changed(),
            'Обработка измненений в заказе'
        )
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.ok('required' not in order.vars, 'Изменения применены и удалены')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 4, 'Остатки')

        with stocks[product1.product_id] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 11, 'Зарезервировано')

        with stocks[product2.product_id] as stock:
            tap.eq(stock.count, 200, 'Остаток')
            tap.eq(stock.reserve, 2, 'Зарезервировано')

        with stocks[product3.product_id] as stock:
            tap.eq(stock.count, 300, 'Остаток')
            tap.eq(stock.reserve, 30, 'Зарезервировано')

        with stocks[product5.product_id] as stock:
            tap.eq(stock.count, 500, 'Остаток')
            tap.eq(stock.reserve, 50, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)
        tap.eq(len(suggests), 8, 'Саджесты')

        with suggests[(product1.product_id, 'shelf2box', 10)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product1.product_id, 'shelf2box', 1)] as suggest:
            tap.eq(suggest.status, 'request', 'Новый саджест добора')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product2.product_id, 'shelf2box', 20)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product2.product_id, 'box2shelf', 18)] as suggest:
            tap.eq(suggest.status, 'request', 'Новый возврата')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product3.product_id, 'shelf2box', 30)] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест для нового продукта')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product4.product_id, 'shelf2box', 40)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product4.product_id, 'box2shelf', 40)] as suggest:
            tap.eq(suggest.status, 'request', 'Полный возврат')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product5.product_id, 'shelf2box', 50)] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем выполнять')

        # 2 изменение
        order.vars['required'] = [
            {
                'product_id': product1.product_id,
                'count': 15,
            },
            {
                'product_id': product2.product_id,
                'count': 24,
            },
            {
                'product_id': product4.product_id,
                'count': 40
            },
            {
                'product_id': product5.product_id,
                'count': 50
            },
        ]
        tap.ok(await order.save(), 'Пришло 2 изменение по продуктам')

        tap.ok(
            await order.business.order_changed(),
            'Обработка измненений в заказе'
        )
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')
        tap.ok('required' not in order.vars, 'Изменения применены и удалены')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 4, 'Остатки')

        with stocks[product1.product_id] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 15, 'Зарезервировано')

        with stocks[product2.product_id] as stock:
            tap.eq(stock.count, 200, 'Остаток')
            tap.eq(stock.reserve, 24, 'Зарезервировано')

        with stocks[product4.product_id] as stock:
            tap.eq(stock.count, 400, 'Остаток')
            tap.eq(stock.reserve, 40, 'Зарезервировано')

        with stocks[product5.product_id] as stock:
            tap.eq(stock.count, 500, 'Остаток')
            tap.eq(stock.reserve, 50, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict((
            (x.product_id, x.type, x.count, x.status), x) for x in suggests)
        tap.eq(len(suggests), 12, 'Саджесты')

        with suggests[(product1.product_id, 'shelf2box', 10, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product1.product_id, 'shelf2box', 1, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product1.product_id, 'shelf2box', 4, 'request')] as s:
            tap.ok(s, 'Новый саджест добора')
            tap.ok(await s.done(), 'Выполнили саджест')

        with suggests[(product2.product_id, 'shelf2box', 20, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product2.product_id, 'box2shelf', 18, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product2.product_id, 'shelf2box', 22, 'request')] as s:
            tap.ok(s, 'Новый добора')
            tap.ok(await s.done(), 'Выполнили саджест')

        with suggests[(product3.product_id, 'shelf2box', 30, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product3.product_id, 'box2shelf', 30, 'request')] as s:
            tap.ok(s, 'Саджест для нового продукта')
            tap.ok(await s.done(), 'Выполнили саджест')

        with suggests[(product4.product_id, 'shelf2box', 40, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product4.product_id, 'box2shelf', 40, 'done')] as s:
            tap.ok(s, 'Закрыт ранее')
        with suggests[(product4.product_id, 'shelf2box', 40, 'request')] as s:
            tap.ok(s, 'Полный возврат')
            tap.ok(await s.done(), 'Выполнили саджест')

        with suggests[(product5.product_id, 'shelf2box', 50, 'request')] as s:
            tap.ok(s, 'Не выполнялся')
            tap.ok(await s.done(), 'Выполнили саджест')

        await order.business.order_changed()
        tap.ok(
            await order.done('complete', user=user),
            'Подтвердим завершение заказа'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_waiting_update_suggests(tap, dataset, now, wait_order_status):
    with tap.plan(30, 'Постепенное убавление товара + хаос выполнения'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store')

        await dataset.stock(product=product1, shelf=shelf, count=100)
        await dataset.stock(product=product2, shelf=shelf, count=100)

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
                    'count': 1,
                },
                {
                    'product_id': product1.product_id,
                    'count': 1,
                },
                {
                    'product_id': product2.product_id,
                    'count': 10,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        stocks = await Stock.list_by_order(order)
        stocks = dict(((x.product_id, x.shelf_type), x) for x in stocks)
        tap.eq(len(stocks), 2, 'Остатки')

        with stocks[(product1.product_id, 'store')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 2, 'Зарезервировано')
        with stocks[(product2.product_id, 'store')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 10, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)
        tap.eq(len(suggests), 2, 'Саджесты')

        with suggests[(product1.product_id, 'shelf2box', 2)] as suggest:
            tap.eq(suggest.status, 'request', 'Запрос')

        with suggests[(product2.product_id, 'shelf2box', 10)] as suggest:
            tap.eq(suggest.status, 'request', 'Запрос')
            tap.ok(await suggest.done(), 'Выполнили')

        order.vars['required'] = [
            {
                'product_id': product1.product_id,
                'count': 1,
            },
            {
                'product_id': product2.product_id,
                'count': 10,
            },
        ]
        tap.ok(await order.save(), 'Пришло изменение 1 по продуктам')
        tap.ok(
            await order.business.order_changed(),
            'Обработка измненений в заказе'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        stocks = await Stock.list_by_order(order)
        stocks = dict(((x.product_id, x.shelf_type), x) for x in stocks)
        tap.eq(len(stocks), 2, 'Остатки')

        with stocks[(product1.product_id, 'store')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 1, 'Зарезервировано')
        with stocks[(product2.product_id, 'store')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 10, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)
        tap.eq(len(suggests), 2, 'Саджесты')

        with suggests[(product1.product_id, 'shelf2box', 1)] as suggest:
            tap.eq(suggest.status, 'request', 'Запрос')

        with suggests[(product2.product_id, 'shelf2box', 10)] as suggest:
            tap.eq(suggest.status, 'done', 'Выполнен')

        order.vars['required'] = [
            {
                'product_id': product2.product_id,
                'count': 10,
            },
        ]
        tap.ok(await order.save(), 'Пришло изменение 2 по продуктам')
        tap.ok(
            await order.business.order_changed(),
            'Обработка измненений в заказе'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        stocks = await Stock.list_by_order(order)
        stocks = dict(((x.product_id, x.shelf_type), x) for x in stocks)
        tap.eq(len(stocks), 1, 'Остатки')

        with stocks[(product2.product_id, 'store')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 10, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты')

        suggests = dict(
            ((x.product_id, x.type, x.count, x.status), x) for x in suggests)

        with suggests[(product2.product_id, 'shelf2box', 10, 'done')] as s:
            tap.ok(s, 'Выполнен')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )


async def test_waiting_drop(tap, dataset, now, wait_order_status):
    with tap.plan(43, 'Сборка заказа - откат саджестов при изменении'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        shelf1  = await dataset.shelf(store=store, order=1)
        shelf2  = await dataset.shelf(store=store, order=2)

        await dataset.stock(product=product1, shelf=shelf1, count=100)
        await dataset.stock(product=product1, shelf=shelf2, count=100)
        await dataset.stock(product=product2, shelf=shelf1, count=200)
        await dataset.stock(product=product2, shelf=shelf2, count=200)
        await dataset.stock(product=product3, shelf=shelf1, count=300)
        await dataset.stock(product=product3, shelf=shelf2, count=300)
        await dataset.stock(product=product4, shelf=shelf1, count=400)

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
                    'count': 110
                },
                {
                    'product_id': product2.product_id,
                    'count': 220
                },
                {
                    'product_id': product3.product_id,
                    'count': 330
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 6, 'Саджесты на сборку')
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)

        with suggests[(product1.product_id, 'shelf2box', 100)] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем выполнять')
        with suggests[(product1.product_id, 'shelf2box', 10)] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем выполнять')

        with suggests[(product2.product_id, 'shelf2box', 200)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product2.product_id, 'shelf2box', 20)] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем выполнять')

        with suggests[(product3.product_id, 'shelf2box', 300)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product3.product_id, 'shelf2box', 30)] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        order.vars['required'] = [
            {
                'product_id': product4.product_id,
                'count': 40,
            },
        ]
        tap.ok(await order.save(), 'Пришло изменение по продуктам')

        tap.ok(
            await order.business.order_changed(),
            'Обработка измненений в заказе'
        )
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'check_target', 'check_target')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok('required' in order.vars, 'Изменения ждут применения')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok('required' not in order.vars, 'Изменения применены и удалены')

        stocks = await Stock.list_by_order(order)
        stocks = dict(((x.product_id, x.shelf_id), x) for x in stocks)
        tap.eq(len(stocks), 1, 'Остатки')

        with stocks[(product4.product_id, shelf1.shelf_id)] as stock:
            tap.eq(stock.count, 400, 'Остаток')
            tap.eq(stock.reserve, 40, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)
        suggests = dict(((x.product_id, x.type, x.count), x) for x in suggests)
        tap.eq(len(suggests), 7, 'Саджесты')

        with suggests[(product2.product_id, 'shelf2box', 200)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product2.product_id, 'box2shelf', 200)] as suggest:
            tap.eq(suggest.status, 'request', 'Возврат')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product3.product_id, 'shelf2box', 300)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product3.product_id, 'box2shelf', 300)] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест для нового продукта')
            tap.ok(await suggest.done(), 'Выполнили саджест')
        with suggests[(product3.product_id, 'shelf2box', 30)] as suggest:
            tap.eq(suggest.status, 'done', 'Закрыт ранее')
        with suggests[(product3.product_id, 'box2shelf', 30)] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест для нового продукта')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        with suggests[(product4.product_id, 'shelf2box', 40)] as suggest:
            tap.eq(suggest.status, 'request', 'Полный возврат')
            tap.ok(await suggest.done(), 'Выполнили саджест')

        await order.business.order_changed()
        tap.ok(
            await order.done('complete', user=user),
            'Подтвердим завершение заказа'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_waiting_request_less(tap, dataset, now, wait_order_status):
    with tap.plan(
            18,
            'Еще один вариант ошибки генерации саджестов: '
            'в статусе request они редактируются а не отменяются'
    ):

        product1 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store, count=100)

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
                    'count': 10
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты на сборку')
        suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

        with suggests[('shelf2box', 10, 'request')] as suggest:
            tap.eq(suggest.product_id, product1.product_id, 'product_id')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        order.vars['required'] = [
            {
                'product_id': product1.product_id,
                'count': 7,
            },
        ]
        tap.ok(await order.save(), 'Продукта оказалось меньше чем надо')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok('required' not in order.vars, 'Изменения применены и удалены')

        stocks = await Stock.list_by_order(order)
        stocks = dict((x.product_id, x) for x in stocks)
        tap.eq(len(stocks), 1, 'Остатки')

        with stocks[product1.product_id] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 7, 'Зарезервировано')

        suggests = await Suggest.list_by_order(order)

        suggests = dict(((x.type, x.count, x.status), x) for x in suggests)
        tap.eq(len(suggests), 1, 'Саджесты')

        with suggests[('shelf2box', 7, 'request')] as suggest:
            tap.ok(await suggest.done(), 'Выполнили саджест')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )


async def test_waiting_recount(tap, dataset, now, wait_order_status):
    with tap.plan(8, 'Всегда редактируем саджест в request'):

        product1 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store, count=100)

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
                    'count': 10
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты на сборку')
        suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

        with suggests[('shelf2box', 10, 'request')] as suggest:
            tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(4, 'Снизили до 7') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 7,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 1, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 7, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(4, 'Увеличили до 15') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 15,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 1, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 15, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(4, 'Снизили до 8') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 8,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 1, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 8, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(4, 'Снизили до 1') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 1,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 1, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 1, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )


async def test_waiting_recount_mix(tap, dataset, now, wait_order_status):
    with tap.plan(8, 'Редактирование + генерация'):

        product1 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store, count=100)

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
                    'count': 10
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты на сборку')
        suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

        with suggests[('shelf2box', 10, 'request')] as suggest:
            tap.ok(await suggest.done('done'), 'Саджест выполнен')

        with tap.subtest(5, 'Снизили до 7') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 7,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 2, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 10, 'done')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')
            with suggests[('box2shelf', 3, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(5, 'Увеличили до 15') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 15,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 2, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 10, 'done')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')
            with suggests[('shelf2box', 5, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(5, 'Снизили до 8') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 8,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 2, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 10, 'done')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')
            with suggests[('box2shelf', 2, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        with tap.subtest(5, 'Снизили до 1') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product1.product_id,
                    'count': 1,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await Suggest.list_by_order(order)
            _tap.eq(len(suggests), 2, 'Саджесты')
            suggests = dict(((x.type, x.count, x.status), x) for x in suggests)

            with suggests[('shelf2box', 10, 'done')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')
            with suggests[('box2shelf', 9, 'request')] as suggest:
                _tap.eq(suggest.product_id, product1.product_id, 'product_id')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
