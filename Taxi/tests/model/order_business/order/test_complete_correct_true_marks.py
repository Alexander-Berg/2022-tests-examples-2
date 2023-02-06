from collections import defaultdict


async def test_correct_true_marks(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals
    with tap.plan(24, 'Обновляем марки'):
        store = await dataset.store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store=store)
        marked_product_one = await dataset.product(true_mark=True)
        marked_product_two = await dataset.product(true_mark=True)

        marked_products = {
            marked_product_one.product_id: marked_product_one,
            marked_product_two.product_id: marked_product_two,
        }

        await dataset.stock(product=marked_product_one, store=store, count=10)
        await dataset.stock(product=marked_product_two, store=store, count=10)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': marked_product_one.product_id,
                    'count': 2
                },
                {
                    'product_id': marked_product_two.product_id,
                    'count': 1
                },
            ],
            vars={
                'editable': True,
                'need_sell_true_mark': True,
            },
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 3, 'Три саджеста сначала')

        mark_register = defaultdict(list)
        for suggest in suggests:
            product = marked_products[suggest.product_id]
            mark = await dataset.true_mark_value(product=product)
            mark_register[product.product_id].append(mark)
            tap.ok(
                await suggest.done(
                    user=user, count=suggest.count, true_mark=mark),
                'Закрыли успешно марочный саджест'
            )

        tap.ok(await order.reload(), 'Перезабрали документ')
        order.vars['required'] = [
            {
                'product_id': marked_product_one.product_id,
                'count': 1
            },
            {
                'product_id': marked_product_two.product_id,
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
        tap.eq(len(suggests), 1, 'Один саджест еще')

        for suggest in suggests:
            mark = mark_register[suggest.product_id].pop()
            tap.ok(
                await suggest.done(
                    user=user, count=suggest.count, true_mark=mark),
                'Закрыли успешно обратный марочный саджест'
            )
            true_mark = await dataset.TrueMark.load(mark, by='value')
            tap.ok(true_mark, 'Марка есть')
            tap.eq(true_mark.status, 'for_sale', 'Вернулась марка в продажу')
        tap.ok(
            await order.done(user=user, target='complete'),
            'Успешно завершили документ',
        )

        await wait_order_status(order, ('complete', 'correct_true_marks'))
        tap.note(
            'Изменим марку, словно она вернулась в регистре, '
            'но осталась в заказе'
        )
        in_order_marks = (await dataset.TrueMark.list(
            by='full',
            conditions=[
                ('order_id', order.order_id),
                ('status', 'in_order'),
            ],
            limit=1,
        )).list
        tap.ok(in_order_marks, 'Есть марки в заказу')
        missing_mark = in_order_marks[0]
        missing_mark.status = 'for_sale'
        tap.ok(await missing_mark.save(), 'Сохранили марку в регистре')
        redundant_mark = await dataset.true_mark_object(
            order=order,
            product=marked_product_one,
            status='in_order'
        )
        await wait_order_status(order, ('complete', 'done'))
        tap.ok(await redundant_mark.reload(), 'Перезабрали лишнюю марку')
        tap.eq(
            redundant_mark.status,
            'for_sale',
            'Лишняя вернулась в продажу'
        )
        tap.ok(await missing_mark.reload(), 'Перезабрали недостающую марку')
        tap.eq(
            missing_mark.status,
            'sold',
            'Недостающая вернулась в заказ'
        )
        order_marks = await dataset.TrueMark.list(
            by='full',
            conditions=[
                ('order_id', order.order_id),
                ('status', 'sold'),
            ]
        )
        tap.eq(len(order_marks.list), 2, 'Две марки продали в заказе')
        known_marks = set()
        for few_marks in mark_register.values():
            known_marks |= set(few_marks)
        for index, true_mark in enumerate(order_marks):
            tap.ok(
                true_mark.value in known_marks,
                f'Марка {index} в регистре'
            )


async def test_true_marks_not_sold(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals
    with tap.plan(15, 'Марки переходят в статус проданных после флага'):
        store = await dataset.store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store=store)
        marked_product = await dataset.product(true_mark=True)
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
                    'count': 1
                },
            ],
            vars={
                'editable': True,
                'need_sell_true_mark': False,
            },
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 1, 'Один саджест')

        suggest = suggests[0]
        mark_value = await dataset.true_mark_value(product=marked_product)
        tap.ok(
            await suggest.done(
                user=user, count=suggest.count, true_mark=mark_value),
            'Закрыли успешно марочный саджест'
        )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Успешно завершили документ',
        )

        await wait_order_status(order, ('complete', 'correct_true_marks'))
        redundant_mark = await dataset.true_mark_object(
            order=order,
            product=marked_product,
            status='in_order'
        )
        await wait_order_status(order, ('complete', 'done'))
        tap.ok(await redundant_mark.reload(), 'Перезабрали лишнюю марку')
        tap.eq(
            redundant_mark.status,
            'for_sale',
            'Лишняя вернулась в продажу'
        )
        in_order_mark = await dataset.TrueMark.load(mark_value, by='value')
        tap.ok(in_order_mark, 'Получили марку')
        tap.eq(
            in_order_mark.order_id,
            order.order_id,
            'Марка в нужном заказе'
        )
        tap.eq(
            in_order_mark.status,
            'in_order',
            'Марка пока не продана'
        )

        order.vars['need_sell_true_mark'] = True
        tap.ok(
            await order.save(store_lp_event=False, store_job_event=False),
            'Типа пришло время продать марку'
        )
        await wait_order_status(order, ('complete', 'done'))
        tap.ok(await in_order_mark.reload(), 'Перезабрали марку')
        tap.eq(in_order_mark.status, 'sold', 'Продана марка')
