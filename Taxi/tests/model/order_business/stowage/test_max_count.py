async def test_max_count(tap, dataset, wait_order_status):
    with tap.plan(16, 'Доверительно можно указывать бОльшее число'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            type='stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                    'maybe_count': True,
                    'valid': '2011-01-02',
                }
            ],
            status='reserving',
            estatus='begin',
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты получены')

        with suggests[0] as s:
            tap.eq(s.type, 'box2shelf', 'положить на полку')
            tap.eq(s.count, 27, 'количество')
            tap.eq(s.conditions.all, True, 'Можно указать другое количество')
            tap.eq(s.conditions.max_count, False, 'Не ограничено сверху')

            tap.ok(await s.done(count=35), 'Закрыли саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
            ),
            sort=(),
        )
        stocks = stocks.list

        tap.eq(len(stocks), 1, 'Остаток создан')
        with stocks[0] as s:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.count, 35, 'количество')
            tap.eq(s.reserve, 0, 'нет резерва')
