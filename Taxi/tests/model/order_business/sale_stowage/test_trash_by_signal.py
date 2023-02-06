async def test_trash_by_signal(tap, dataset, wait_order_status):
    with tap.plan(31, 'раскладка на trash неизвестных товаров'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        product1 = await dataset.product()
        tap.ok(product1, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 123,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.ok(
            await order.signal({'type': 'sale_stowage'}),
            'раскладка завершена'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(
            order.signals[order.vars['signo']].type,
            'sale_stowage',
            'сигнал sale_stowage'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал sale_stowage закрыт'
        )
        tap.eq(order.vars('stage'), 'trash', 'stage')

        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': product2.product_id,
                        'count': 17,
                    }
                }
            ), 'Сигнал о новом товаре отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(
            order.signals[order.vars['signo']].type,
            'more_product',
            'сигнал more_product'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал закрыт'
        )
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')

        suggests_by_product = {
            suggest.product_id: suggest
            for suggest in suggests
        }

        p1_suggest = suggests_by_product.get(product1.product_id)

        tap.ok(p1_suggest, 'Саджест по product1')
        tap.ok(
            'source' not in p1_suggest.vars,
            'Нет источника в варсах обычного саджеста'
        )
        p2_suggest = suggests_by_product.get(product2.product_id)

        tap.ok(p2_suggest, 'Саджест по product2')
        tap.eq(
            p2_suggest.vars('source', None),
            'signal',
            'Источник сигнал в саджесте'
        )

        for s in suggests:
            if s.product_id != product2.product_id:
                continue
            tap.eq(s.count, 17, 'количество')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = {
            s.stock_id: s
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
        }
        tap.eq(len(stocks), 2, 'всего два остатка')
        tap.ok(
            [s for s in stocks.values() if s.product_id == product1.product_id],
            'остатки товара 1'
        )
        tap.ok(
            [s for s in stocks.values() if s.product_id == product2.product_id],
            'остатки товара 2'
        )

        for s in stocks.values():
            # оба на треш
            tap.eq(len(s.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                s.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_DECAYED',
                'Код записан'
            )
            if s.product_id != product2.product_id:
                continue
            tap.eq(s.count, 17, 'количество')
            tap.eq(s.reserve, 0, 'резерв')


async def test_trash_stocks(tap, dataset, wait_order_status):
    with tap.plan(19, 'раскладка на trash неизвестных товаров'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        product1 = await dataset.product()
        tap.ok(product1, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 123,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.ok(
            await order.signal({'type': 'sale_stowage'}),
            'раскладка завершена'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'stage')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            await s.done(count=123)

        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': product1.product_id,
                        'count': 17,
                    }
                }
            ), 'Сигнал о новом товаре отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 1, 'саджест')
        with suggests[0] as s:
            await s.done(count=17)

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
            sort=(),
        )

        tap.eq(len(stocks.list), 1, 'всего один остаток')

        trash = await dataset.Shelf.list_by_store(
            store_id=store.store_id,
            type='trash',
            status='active',
            db={'mode': 'slave'},
        )

        tap.eq(len(trash), 1, 'полка треш одна')

        with stocks.list[0] as s:
            tap.eq(s.shelf_id, trash[0].shelf_id, 'треш полка')
            tap.eq(s.count, 17+123, 'количество')
            tap.eq(s.reserve, 0, 'резерв')
