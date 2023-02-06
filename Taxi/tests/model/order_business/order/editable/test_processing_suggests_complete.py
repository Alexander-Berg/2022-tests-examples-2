# pylint: disable=too-many-locals,too-many-statements,unused-variable


async def test_update_delete(tap, dataset, wait_order_status, now):
    with tap.plan(40, '#LAVKADEV-1602 удаляем товары из заказа'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        stock2 = await dataset.stock(product=product2, store=store, count=200)
        stock3 = await dataset.stock(product=product3, store=store, count=300)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
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
                    'product_id': product3.product_id,
                    'count': 30
                },

            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        # Должны быть саджесты на взятие по каждому продукту:

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 1')
            tap.eq(suggest.count, 10, 'Количество')
            tap.ok(await suggest.done('done', count=10), 'Выполнили')

        with suggests[product2.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 2')
            tap.eq(suggest.count, 20, 'Количество')

        with suggests[product3.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 3')
            tap.eq(suggest.count, 30, 'Количество')

        await wait_order_status(order, ('processing', 'waiting'))

        order.vars['required'] = [
            {
                'product_id': product2.product_id,
                'count': 20
            },
            {
                'product_id': product3.product_id,
                'count': 30
            },
        ]
        tap.ok(await order.save(), 'Удалили продукт 1 из заказа')

        await wait_order_status(order, ('processing', 'waiting'))

        # Должен добавится саджест на возврат на полку первого продукта

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Список саджестов')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'done', 'Саджест 1')
            tap.eq(suggest.count, 10, 'Количество')

        with suggests[product2.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 2')
            tap.eq(suggest.count, 20, 'Количество')

        with suggests[product3.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 3')
            tap.eq(suggest.count, 30, 'Количество')

        with suggests[product1.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 4')
            tap.eq(suggest.count, 10, 'Количество')

        await wait_order_status(order, ('processing', 'waiting'))

        order.vars['required'] = [
            {
                'product_id': product3.product_id,
                'count': 30
            },
        ]
        tap.ok(await order.save(), 'Удалили продукт 2 из заказа')

        await wait_order_status(order, ('processing', 'waiting'))

        # Ожидаем что невыполненный саджест будет просто удален
        # (в искомой баге почему то для 1-го товара саджест задваивался)

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'done', 'Саджест 1')
            tap.eq(suggest.count, 10, 'Количество')

        with suggests[product3.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 3')
            tap.eq(suggest.count, 30, 'Количество')

        with suggests[product1.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 4')
            tap.eq(suggest.count, 10, 'Количество')

        # Повторный проход так же задваивал саджесты

        with await order.signal({'type': 'update_reserve'}) as s:
            tap.ok(s, 'сигнал отправлен')
            await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'done', 'Саджест 1')
            tap.eq(suggest.count, 10, 'Количество')

        with suggests[product3.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 3')
            tap.eq(suggest.count, 30, 'Количество')

        with suggests[product1.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.status, 'request', 'Саджест 4')
            tap.eq(suggest.count, 10, 'Количество')


async def test_mark_product(tap, dataset, wait_order_status, now, uuid):
    with tap.plan(15, 'Обратные саджесты при обновлении'):
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
            ],
            vars={'editable': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 3, '3 саджеста сначала')

        for suggest, _ in zip(suggests, range(2)):
            mark = f'01{barcode}21{uuid()[:6]}\x1D93Zjqw'
            tap.eq(suggest.type, 'shelf2box', 'shelf2box')
            tap.eq(suggest.conditions.need_true_mark, True, 'Нужна марка')
            tap.ok(
                await suggest.done(user=user, count=1, true_mark=mark),
                'Закрыли успешно марочный саджест'
            )

        order.vars['required'] = [
            {
                'product_id': marked_product.product_id,
                'count': 1
            },
        ]
        tap.ok(
            await order.save(store_job_event=False),
            'Прикопали реквайред новый'
        )
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


async def test_mark_product_appeared(tap, dataset, wait_order_status, now):
    with tap.plan(6, 'Появился марочный товар'):
        store = await dataset.store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store=store)
        random_product = await dataset.product()
        mark_product = await dataset.product(true_mark=True)

        await dataset.stock(product=mark_product, store=store, count=10)
        await dataset.stock(product=random_product, store=store, count=10)
        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': random_product.product_id,
                    'count': 3
                },
            ],
            vars={'editable': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(
            order.vars('true_mark_processing', False),
            True,
            'Прикопали признак обработки марочных саджестов'
        )
        tap.not_in_ok(
            'true_mark_in_order',
            order.vars,
            'Признака нет в vars'
        )

        order.vars['required'] = [
            {
                'product_id': random_product.product_id,
                'count': 3,
            },
            {
                'product_id': mark_product.product_id,
                'count': 2,
            }
        ]
        tap.ok(
            await order.save(store_job_event=False),
            'Прикопали реквайред новый'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(
            order.vars('true_mark_in_order', False),
            True,
            'Метка хоть одного саджеста с маркой появилась'
        )
