# pylint: disable=too-many-statements,too-many-locals,unused-variable


async def test_canceled(tap, dataset, now, wait_order_status):
    with tap.plan(9, 'Отмена заказа'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списания')

        await dataset.stock(product=product1, store=store, count=100)
        await dataset.stock(product=product2, store=store, count=200)

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

        await wait_order_status(
            order, ('processing', 'waiting')
        )

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await order.cancel(user=user), 'Заказ отменен')

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await wait_order_status(order, ('canceled', 'done'))


async def test_canceled_problems(tap, dataset, now, wait_order_status):
    with tap.plan(17, 'Отмена заказа с проблемами'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списания')

        await dataset.stock(product=product1, store=store, count=100)
        await dataset.stock(product=product2, store=store, count=200)

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
                    'count': 220
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

        tap.eq(len(order.problems), 1, 'Проблема с реервированием')

        tap.ok(await order.cancel(user=user), 'Заказ отменен')

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await wait_order_status(order, ('canceled', 'done'))


async def test_canceled_after_edit(tap, dataset, now, wait_order_status):
    with tap.plan(10, 'Поведение саджестов отката после редактирования'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        stock2 = await dataset.stock(product=product2, store=store, count=200)

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
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты на сборку')
        suggests = dict(((x.type, x.status, x.product_id), x) for x in suggests)

        with suggests[('shelf2box', 'request', product1.product_id)] as suggest:
            tap.ok(await suggest.done('done'), 'Саджест выполнен')

        await wait_order_status(order, ('processing', 'waiting'))

        with tap.subtest(7, 'Перевели на другой продукт') as _tap:
            order.vars['required'] = [
                {
                    'product_id': product2.product_id,
                    'count': 1,
                },
            ]
            _tap.ok(await order.save(), 'Изменения сохранены')

            await wait_order_status(order, ('processing', 'waiting'), tap=_tap)

            suggests = await dataset.Suggest.list_by_order(order)
            _tap.eq(len(suggests), 3, 'Саджесты')
            suggests = dict(
                ((x.type, x.status, x.product_id), x) for x in suggests)

            with suggests[('shelf2box', 'done', product1.product_id)] as s:
                _tap.ok(s, 'Уже был выполнен')

            with suggests[('box2shelf', 'request', product1.product_id)] as s:
                _tap.ok(s, 'Саджест возврата на полку')
                _tap.ok(await s.done('done'), 'Саджест выполнен')

            with suggests[('shelf2box', 'request', product2.product_id)] as s:
                _tap.ok(s, 'Саджест взятия нового продукта')

        tap.ok(await order.cancel(user=user), 'Заказ отменен')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.note('Не выполненные удаляться. Выполненные уже уравновешены.')
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты')
        suggests = dict(((x.type, x.status, x.product_id), x) for x in suggests)

        with suggests[('shelf2box', 'done', product1.product_id)] as s:
            tap.ok(s, 'Взятие уже было выполнено')

        with suggests[('box2shelf', 'done', product1.product_id)] as s:
            tap.ok(s, 'Возврат уже был выполнен')


async def test_mark_product(tap, dataset, wait_order_status, now, uuid):
    with tap.plan(13, 'Обратные саджесты на марочные товары в отмене'):
        store = await dataset.store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store=store)

        barcode = '1' + uuid()[:13]
        marked_product = await dataset.product(
            vars={'imported': {'true_mark': True}},
            barcode=[barcode],
        )
        await dataset.stock(product=marked_product, store=store, count=10)
        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': marked_product.product_id,
                    'count': 3
                },
            ]
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 3, '3 саджеста сначала')

        first_suggest = suggests[0]
        true_mark = f'01{barcode}21{uuid()[:6]}\x1D93Zjqw'
        tap.eq(
            first_suggest.product_id,
            marked_product.product_id,
            'Нужный продукт'
        )
        tap.eq(first_suggest.type, 'shelf2box', 'shelf2box')
        tap.eq(first_suggest.conditions.need_true_mark, True, 'Нужна марка')
        tap.ok(
            await first_suggest.done(user=user, count=1, true_mark=true_mark),
            'Закрыли успешно марочный саджест'
        )
        tap.ok(await order.cancel(user=user), 'Заказ отменен')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 1, '1 саджест еще')

        single_suggest = suggests[0]
        tap.eq(
            single_suggest.product_id,
            marked_product.product_id,
            'Нужный продукт'
        )
        tap.eq(single_suggest.type, 'box2shelf', 'box2shelf')
        tap.eq(single_suggest.count, 1, 'кол-во 1')
        tap.eq(single_suggest.conditions.need_true_mark, True, 'Нужна марка')
