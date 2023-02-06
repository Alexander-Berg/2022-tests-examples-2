async def test_stowage(tap, dataset, wait_order_status):
    with tap.plan(34):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            required=[{'product_id': product.product_id, 'count': 123}],
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        for s in await dataset.Suggest.list_by_order(order):
            tap.ok(await s.done(), 'завершаем саджест')
        tap.ok(
            await order.signal({'type': 'sale_stowage'}),
            'сигнал о смене стейджа'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'кладём на треш')

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 0, 'саджестов нет')

        suggest = None
        for _ in range(3):
            tap.ok(
                await order.signal(
                    {
                        'type': 'more_product',
                        'data': {
                            'product_id': product.product_id,
                            'count': 32,
                        }
                    }
                ),
                'сигнал о новом товаре для полки trash'
            )
            await wait_order_status(order, ('processing', 'waiting'))
            suggests = await dataset.Suggest.list_by_order(
                order, status='request'
            )
            tap.eq(len(suggests), 1, 'Только один допсаджест')
            suggest = suggests[0]

        tap.eq(suggest.product_id, product.product_id, 'товар в саджесте')
        tap.eq(suggest.count, 32, 'количество')
        tap.ok(suggest.conditions.all, 'all')

        tap.ok(await suggest.done(count=77), 'закрыт')
        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': product.product_id,
                        'count': 32,
                    }
                }
            ),
            'сигнал о новом товаре для полки trash'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order, status='request'
        )

        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.ok(not s.conditions.error, 'нельзя закрывать в ошибку')
            with tap.raises(dataset.Suggest.ErSuggestErrorDenided,
                            'нельзя закрыть с ошибкой'):
                await s.done('error', reason={'code': 'SHELF_IS_FULL'})
            tap.ok(await suggest.done(count=32), 'закрыт')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
            sort=(),
        )

        tap.eq(
            {s.product_id for s in stocks},
            {product.product_id},
            'все остатки про товар'
        )

        tap.eq(
            sum(s.left for s in stocks if s.shelf_type == 'store'),
            123,
            'на полке store количество верное'
        )
        tap.eq(
            sum(s.left for s in stocks if s.shelf_type == 'trash'),
            109,
            'на полке trash количество верное'
        )
