async def test_success(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals, too-many-statements
    with tap.plan(87, 'Рефанд с марочным товаром'):
        product = await dataset.product(true_mark=True)
        store = await dataset.full_store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store_id=store.store_id)
        stock = await dataset.stock(store=store, product=product, count=10)

        trashes = await dataset.Shelf.list(
            by='full',
            conditions=[
                ('type', 'trash'),
                ('store_id', store.store_id),
            ],
            sort=(),
        )
        tap.ok(trashes.list, 'Трэшовые полки есть')
        trash = trashes.list[0]

        order = await dataset.order(
            store=store,
            type='order',
            required=[{
                'product_id': product.product_id,
                'count': 6,
            }],
            acks=[user.user_id],
            approved=now(),
            vars={'need_sell_true_mark': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 6, 'Шесть саджестов')
        true_marks = []
        for suggest in suggests:
            true_mark = await dataset.true_mark_value(product=product)
            true_marks.append(true_mark)
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 4, 'Продали 6')

        tap.ok(await order.cancel(user=user), 'Отменили заказ')
        await wait_order_status(order, ('canceled', 'done'))
        refund_orders = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )).list
        tap.ok(refund_orders, 'Есть дочерние')
        refund = refund_orders[0]
        tap.eq(refund.type, 'refund', 'Рефанд есть')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user=user), 'Взяли заказ в работу')
        await wait_order_status(refund, ('processing', 'waiting'))
        tap.eq(
            refund.vars('true_mark_processing', None),
            True,
            'Метка обработки марок'
        )
        tap.eq(
            refund.vars('parent_marks_sold', False),
            True,
            'Марки проданы'
        )

        suggests = await dataset.Suggest.list_by_order(order=refund)
        tap.eq(len(suggests), 6, 'Шесть саджестов в рефанде')
        for index, suggest in enumerate(suggests):
            true_mark = true_marks[index]
            tap.eq(suggest.count, 1, 'Количество 1 в саджесте')
            tap.eq(
                suggest.reason.code,
                'TRASH_TRUE_MARK_REFUND',
                'Причина правильная'
            )
            tap.eq(suggest.type, 'box2shelf', 'Тип b2s')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'На трэш')
            tap.eq(
                suggest.vars('stage', None),
                'trash_true_mark',
                'Cтадия в саджесте'
            )
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
            tap.eq(
                suggest.vars('true_mark', None),
                true_mark,
                'Марка прикопалась в саджесте'
            )
        tap.ok(
            await refund.done(user=user, target='complete'),
            'Заказ завершили'
        )

        await wait_order_status(refund, ('complete', 'done'))
        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 4, 'Все еще 4')
        stocks = (await stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ],
            sort=(),
        )).list
        tap.eq(len(stocks), 2, 'Два остатка')
        trash_stock = next(
            (
                stock for stock in stocks
                if stock.shelf_type == 'trash'
            ),
            None
        )
        tap.ok(trash_stock, 'Трэшовый остаток')
        tap.eq(trash_stock.count, 6, 'Все 6 на трэш')
        tap.ok('reasons' in trash_stock.vars, 'Есть причины в остатке')
        tap.ok(
            refund.order_id in trash_stock.vars['reasons'][0],
            'Заказ тот в варсах'
        )
        tap.eq(
            trash_stock.vars['reasons'][0][
                refund.order_id].get('reason_code'),
            'TRASH_TRUE_MARK_REFUND',
            'Код причины правильный',
        )
        for index, mark_value in enumerate(true_marks, start=1):
            true_mark = await dataset.TrueMark.load(
                mark_value,
                by='value'
            )
            tap.ok(true_mark, f'Марка {index} есть')
            tap.eq(
                true_mark.status,
                'sold',
                f'Марка {index} осталась проданной'
            )


async def test_not_sold_marks(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals, too-many-statements
    with tap.plan(58, 'Рефанд марок непроданного заказа'):
        product = await dataset.product(true_mark=True)
        store = await dataset.full_store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store_id=store.store_id)
        stock_one = await dataset.stock(store=store, product=product, count=1)
        stock_two = await dataset.stock(store=store, product=product, count=2)

        order = await dataset.order(
            store=store,
            type='order',
            required=[{
                'product_id': product.product_id,
                'count': 3,
            }],
            acks=[user.user_id],
            approved=now(),
            vars={'need_sell_true_mark': False},
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 3, 'Три саджеста')
        true_marks = []
        for suggest in suggests:
            true_mark = await dataset.true_mark_value(product=product)
            true_marks.append(true_mark)
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await stock_one.reload(), 'Перезабрали остаток')
        tap.eq(stock_one.count, 0, 'Продали весь')

        tap.ok(await stock_two.reload(), 'Перезабрали остаток второй')
        tap.eq(stock_two.count, 0, 'Продали весь второй')

        tap.ok(await order.cancel(user=user), 'Отменили заказ')
        await wait_order_status(order, ('canceled', 'done'))
        refund_orders = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
        )).list
        tap.ok(refund_orders, 'Есть дочерние')
        refund = refund_orders[0]
        tap.eq(refund.type, 'refund', 'Рефанд есть')

        await wait_order_status(refund, ('request', 'waiting'))

        tap.eq(
            refund.vars('true_mark_processing', None),
            True,
            'Метка обработки марок'
        )
        tap.eq(
            refund.vars('parent_marks_sold', False),
            False,
            'Марки не проданы'
        )
        tap.ok(await refund.ack(user=user), 'Взяли заказ в работу')
        await wait_order_status(refund, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order=refund)
        tap.eq(len(suggests), 3, 'Три саджеста в рефанде')
        for index, suggest in enumerate(suggests):
            tap.eq(suggest.count, 1, 'Количество 1 в саджесте')
            tap.eq(
                suggest.conditions.need_true_mark,
                True,
                'Марочный кондишен'
            )
            tap.ok(
                (
                    set(suggest.vars('stock_id', [])) &
                    {stock_one.stock_id, stock_two.stock_id}
                ),
                'Стоки правильные'
            )
            tap.eq(suggest.type, 'box2shelf', 'Тип b2s')
            tap.in_ok(
                suggest.shelf_id,
                {stock_one.shelf_id, stock_two.shelf_id},
                'На нужную полку'
            )
            tap.eq(
                suggest.vars('stage', None),
                'store',
                'Cтадия в саджесте'
            )
            true_mark = true_marks[index]
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
            tap.eq(
                suggest.vars('true_mark', None),
                true_mark,
                'Марка прикопалась в саджесте'
            )
        tap.ok(
            await refund.done(user=user, target='complete'),
            'Заказ завершили'
        )

        await wait_order_status(refund, ('complete', 'done'))
        tap.ok(await stock_one.reload(), 'Перезабрали остаток')
        tap.eq(stock_one.count, 1, 'Вернулся 1')
        tap.ok(await stock_two.reload(), 'Перезабрали второй остаток')
        tap.eq(stock_two.count, 2, 'Вернулся второй 2')
        stocks = (await stock_one.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ]
        )).list
        tap.eq(len(stocks), 2, 'Два остатка')

        for index, mark_value in enumerate(true_marks, start=1):
            true_mark = await dataset.TrueMark.load(
                mark_value,
                by='value'
            )
            tap.ok(true_mark, f'Марка {index} есть')
            tap.eq(
                true_mark.status,
                'for_sale',
                f'Марка {index} снова в продаже'
            )


async def test_unsold_mark_trash_lost(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals, too-many-statements
    with tap.plan(53, 'Непроданные марки в трэш и потери'):
        product = await dataset.product(true_mark=True)
        store = await dataset.full_store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store_id=store.store_id)
        stock = await dataset.stock(store=store, product=product, count=2)

        order = await dataset.order(
            store=store,
            type='order',
            required=[{
                'product_id': product.product_id,
                'count': 2,
            }],
            acks=[user.user_id],
            approved=now(),
            vars={'need_sell_true_mark': False},
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 2, '2 саджеста')
        true_marks = []
        for suggest in suggests:
            true_mark = await dataset.true_mark_value(product=product)
            true_marks.append(true_mark)
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 0, 'Продали весь')

        tap.ok(await order.cancel(user=user), 'Отменили заказ')
        await wait_order_status(order, ('canceled', 'done'))
        refund_orders = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
        )).list
        tap.ok(refund_orders, 'Есть дочерние')
        refund = refund_orders[0]
        tap.eq(refund.type, 'refund', 'Рефанд есть')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user=user), 'Взяли заказ в работу')
        await wait_order_status(refund, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order=refund)
        tap.eq(len(suggests), 2, 'Два саджеста в рефанде')
        for index, suggest in enumerate(suggests):
            tap.eq(suggest.count, 1, 'Количество 1 в саджесте')
            tap.eq(suggest.type, 'box2shelf', 'Тип b2s')
            tap.eq(
                suggest.conditions.need_true_mark,
                True,
                'Кондишен'
            )
            tap.eq(
                suggest.vars('stage', None),
                'store',
                'Cтадия в саджесте'
            )
            tap.ok(
                await suggest.done(
                    status='done',
                    count=0,
                    true_mark=None,
                ),
                'Саджест закрыли в 0'
            )

        await wait_order_status(refund, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order=refund, status='request')
        trash_shelf = (await dataset.Shelf.list_by_store(
            store_id=store.store_id,
            type='trash'
        ))[0]
        tap.eq(len(suggests), 2, 'Два саджеста в рефанде')
        for index, suggest in enumerate(suggests):
            tap.eq(suggest.count, 1, 'Количество 1 в саджесте')
            tap.eq(suggest.type, 'box2shelf', 'Тип b2s')
            tap.eq(
                suggest.conditions.need_true_mark,
                True,
                'Кондишен'
            )
            tap.eq(
                suggest.vars('stage', None),
                'trash',
                'Cтадия в саджесте trash'
            )
            tap.eq(
                suggest.shelf_id,
                trash_shelf.shelf_id,
                'На полку trash'
            )
        suggest = suggests[0]
        tap.ok(
            await suggest.done(
                status='done',
                true_mark=true_marks[0],
            ),
            'Саджест закрыли в трэш'
        )
        suggest = suggests[1]
        tap.ok(
            await suggest.done(
                status='done',
                count=0,
                true_mark=None,
            ),
            'Саджест закрыли в 0'
        )
        tap.ok(
            await refund.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(refund, ('complete', 'done'))

        for index, mark_value in enumerate(true_marks, start=1):
            true_mark = await dataset.TrueMark.load(
                mark_value,
                by='value'
            )
            tap.ok(true_mark, f'Марка {index} есть')
            tap.eq(
                true_mark.status,
                'in_order',
                f'Марка {index} осталась в заказе'
            )

        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 0, 'Не появилось на том же остатке')
        stocks = (await stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ]
        )).list
        tap.eq(len(stocks), 3, 'Три остатка')

        stocks = await stock.list_by_product(
            store_id=store.store_id,
            product_id=product.product_id,
            shelf_type='lost'
        )
        tap.eq(len(stocks), 1, 'Один остаток в потерях')
        tap.eq(stocks[0].count, 1, 'Один экземпляр')

        stocks = await stock.list_by_product(
            store_id=store.store_id,
            product_id=product.product_id,
            shelf_type='trash',
        )
        tap.eq(len(stocks), 1, 'Один остаток в трэше')
        tap.eq(stocks[0].count, 1, 'count = 1')


async def test_cancel_refund(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals
    with tap.plan(33, 'Рефанд отменили'):
        product = await dataset.product(true_mark=True)
        store = await dataset.full_store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store_id=store.store_id)
        stock = await dataset.stock(store=store, product=product, count=10)

        order = await dataset.order(
            store=store,
            type='order',
            required=[{
                'product_id': product.product_id,
                'count': 3,
            }],
            acks=[user.user_id],
            approved=now(),
            vars={'need_sell_true_mark': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 3, 'Три саджеста')
        true_marks = []
        for suggest in suggests:
            true_mark = await dataset.true_mark_value(product=product)
            true_marks.append(true_mark)
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 7, 'Продали 3')

        tap.ok(await order.cancel(user=user), 'Отменили заказ')
        await wait_order_status(order, ('canceled', 'done'))
        refund_orders = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )).list
        tap.ok(refund_orders, 'Есть дочерние')
        refund = refund_orders[0]
        tap.eq(refund.type, 'refund', 'Рефанд есть')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user=user), 'Взяли заказ в работу')
        await wait_order_status(refund, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order=refund)
        tap.eq(len(suggests), 3, 'Три саджеста в рефанде')
        for index, suggest in enumerate(suggests):
            if index > 1:
                break
            true_mark = true_marks[index]
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )

        tap.ok(await refund.cancel(user=user), 'Отменили заказ')
        await wait_order_status(refund, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order=refund, status='request')
        tap.eq(len(suggests), 2, 'Два саджеста')

        for index, suggest in enumerate(suggests):
            true_mark = true_marks[index]
            tap.eq(suggest.type, 'shelf2box', 'Тип саджеста в корзину')
            tap.eq(
                suggest.vars('stage', None),
                'canceling',
                'Саджесты отмены'
            )
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )

        await wait_order_status(refund, ('canceled', 'done'))
        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 7, 'Все еще 7 на остатке')
        stocks = (await stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ],
            sort=(),
        )).list
        tap.eq(len(stocks), 1, 'Один остаток')
        sls = await dataset.StockLog.list(
            by='full',
            conditions=[
                ('order_id', refund.order_id)
            ],
        )
        tap.eq(sls.list, [], 'Остатки вообще не подвигали')


async def test_part_lost(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals
    with tap.plan(29, 'Рефанд не полностью сгрузили'):
        product = await dataset.product(true_mark=True)
        store = await dataset.full_store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store_id=store.store_id)
        stock = await dataset.stock(store=store, product=product, count=5)
        order = await dataset.order(
            store=store,
            type='order',
            required=[{
                'product_id': product.product_id,
                'count': 3,
            }],
            acks=[user.user_id],
            approved=now(),
            vars={'need_sell_true_mark': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 3, 'Три саджеста')
        true_marks = []
        for suggest in suggests:
            true_mark = await dataset.true_mark_value(product=product)
            true_marks.append(true_mark)
            tap.ok(
                await suggest.done(
                    count=1,
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await stock.reload(), 'Перезабрали остаток')
        tap.eq(stock.count, 2, 'Продали 5-3')

        tap.ok(await order.cancel(user=user), 'Отменили заказ')
        await wait_order_status(order, ('canceled', 'done'))
        refund_orders = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )).list
        tap.ok(refund_orders, 'Есть дочерние')
        refund = refund_orders[0]
        tap.eq(refund.type, 'refund', 'Рефанд есть')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user=user), 'Взяли заказ в работу')
        await wait_order_status(refund, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order=refund)
        tap.eq(len(suggests), 3, 'Три саджеста в рефанде')

        first_suggest = suggests[0]
        true_mark = true_marks[0]
        tap.ok(
            await first_suggest.done(
                status='done',
                true_mark=true_mark,
            ),
            'Саджест закрыли'
        )
        for index, suggest in enumerate(suggests):
            if index == 0:
                continue
            tap.ok(
                await suggest.done(
                    count=0,
                    status='done',
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await refund.done(user=user, target='complete'),
            'Закрыли заказ'
        )
        await wait_order_status(refund, ('complete', 'done'))

        stocks = (await stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ],
            sort=(),
        )).list
        tap.eq(len(stocks), 3, 'Три остатка')
        stocks = {
            stock.shelf_type: stock
            for stock in stocks
        }
        tap.in_ok('lost', stocks, 'Появился остаток на потерях')
        tap.eq(stocks['lost'].count, 2, 'Две марки потеряли')

        tap.in_ok('trash', stocks, 'Появился остаток на списании')
        tap.eq(stocks['trash'].count, 1, 'Одна марка в списание')

        tap.in_ok('store', stocks, 'Остаток на полке')
        tap.eq(stocks['store'].count, 2, '5-3 на полке')


async def test_true_mark_no_stocks(tap, dataset, wait_order_status, now):
    # pylint: disable=too-many-locals, too-many-statements
    with tap.plan(37, 'Марка больше там не лежит'):
        product = await dataset.product(true_mark=True)
        store = await dataset.full_store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store_id=store.store_id)
        stock_1 = await dataset.stock(store=store, product=product, count=3)
        stock_2 = await dataset.stock(store=store, product=product, count=5)

        trashes = await dataset.Shelf.list(
            by='full',
            conditions=[
                ('type', 'trash'),
                ('store_id', store.store_id),
            ],
            sort=(),
        )
        tap.ok(trashes.list, 'Трэшовые полки есть')

        order = await dataset.order(
            store=store,
            type='order',
            required=[{
                'product_id': product.product_id,
                'count': 8,
            }],
            acks=[user.user_id],
            approved=now(),
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 8, '8 саджестов')
        true_marks = []
        for suggest in suggests:
            true_mark = await dataset.true_mark_value(product=product)
            true_marks.append(true_mark)
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Заказ завершили'
        )
        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await order.cancel(user=user), 'Отменили заказ')
        await wait_order_status(order, ('canceled', 'done'))
        refund_orders = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )).list
        tap.ok(refund_orders, 'Есть дочерние')
        refund = refund_orders[0]
        tap.eq(refund.type, 'refund', 'Рефанд есть')

        shelf_1 = await dataset.Shelf.load(stock_1.shelf_id)
        shelf_1.status = 'removed'
        tap.ok(await shelf_1.save(), 'Сменили статус полки')

        await wait_order_status(refund, ('request', 'waiting'))
        tap.ok(await refund.ack(user=user), 'Взяли заказ в работу')
        await wait_order_status(refund, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order=refund)
        tap.eq(len(suggests), 8, '8 саджестов в рефанде')
        for index, suggest in enumerate(suggests):
            true_mark = true_marks[index]
            tap.ok(
                await suggest.done(
                    status='done',
                    true_mark=true_mark,
                ),
                'Саджест закрыли'
            )
        tap.ok(
            await refund.done(user=user, target='complete'),
            'Заказ завершили'
        )

        await wait_order_status(refund, ('complete', 'done'))

        stocks = (await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ],
            sort=(),
        )).list
        tap.eq(len(stocks), 2, 'Два остатка')
        tap.ok(await stock_1.reload(), 'Перезабрали остаток')
        tap.eq(stock_1.count, 0, 'Все еще 0')
        tap.ok(await stock_2.reload(), 'Перезабрали остаток')
        tap.eq(stock_2.count, 8, 'Все 8 на остатке')
