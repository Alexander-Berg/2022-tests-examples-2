async def test_negative_stowage(tap, dataset, wait_order_status):
    with tap.plan(14, 'Не возникает исключений если закрывать больше'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='sale_stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                    'maybe_count': True,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            tap.ok(await s.done(count=45, valid='2019-01-02'),
                   'завершён на бОльшую сумму')
            tap.ok(s.result_count > s.count, 'правда бОльшая сумма')
        tap.ok(await order.signal({'type': 'sale_stowage'}),
               'сигнал отправлен')

        with tap.subtest(None, 'Ожидаем стадии списания') as taps:
            while order.vars('stage') != 'trash':
                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
        await wait_order_status(order,
                                ('complete', 'done'),
                                user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')
        with stocks.list[0] as s:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.count, 45, 'количество')


async def test_negative_trash(tap, dataset, wait_order_status):
    with tap.plan(14, 'Не возникает исключений если списать больше'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='sale_stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                    'maybe_count': True,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        tap.ok(await order.signal({'type': 'sale_stowage'}),
               'сигнал отправлен')
        with tap.subtest(None, 'Ожидаем стадии списания') as taps:
            while order.vars('stage', None) != 'trash':
                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        for s in suggests:
            s.conditions.max_count = False
            tap.ok(await s.done(count=45, valid='2019-01-02'),
                   'завершён на бОльшую сумму')
            tap.ok(s.result_count > s.count, 'правда бОльшая сумма')

        await wait_order_status(order,
                                ('complete', 'done'),
                                user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')
        with next(sl for sl in stocks if sl.shelf_type == 'trash') as s:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.count, 45, 'количество')
