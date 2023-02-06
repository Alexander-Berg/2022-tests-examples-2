async def test_trash(tap, dataset, wait_order_status):
    with tap.plan(24, 'списание и потери'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        office = await dataset.shelf(store=store, type='office')
        tap.eq(office.store_id, store.store_id, 'офис полка создана')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='reserving',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 123}],
        )
        tap.ok(order, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.vars('stage'), 'trash', 'саджест списания')
            shelf = await dataset.Shelf.load(s.shelf_id)
            tap.eq(shelf.type, 'trash', 'на полку списания')
            tap.eq(s.count, 123, 'количество')
            tap.eq(s.conditions.error, False, 'Нельзя закрывать в ошибку')

            with tap.raises(dataset.Suggest.ErSuggestCount,
                            'нельзя закрывать больше'):
                await s.done(count=188)

            tap.ok(await s.done(count=17), 'закрываем саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'Остатки')
        with next(sl for sl in stocks if sl.shelf_type == 'trash') as s:
            tap.eq(s.shelf_type, 'trash', 'остаток на списании')
            tap.eq(s.count, 17, 'количество')
            tap.eq(s.product_id, product.product_id, 'товар')

            tap.eq(len(s.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                s.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_DECAYED',
                'Код записан'
            )

        with next(r for r in order.required
                  if r.product_id == product.product_id) as r:
            tap.eq(r.result_count, 17, 'количество принятого')


async def test_write_reason(tap, dataset, wait_order_status):
    with tap.plan(23, 'Записана причина переданая в саджест'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        office = await dataset.shelf(store=store, type='office')
        tap.eq(office.store_id, store.store_id, 'офис полка создана')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='reserving',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 123}],
        )
        tap.ok(order, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.vars('stage'), 'trash', 'саджест списания')
            shelf = await dataset.Shelf.load(s.shelf_id)
            tap.eq(shelf.type, 'trash', 'на полку списания')
            tap.eq(s.count, 123, 'количество')
            tap.eq(s.conditions.error, False, 'Нельзя закрывать в ошибку')

            with tap.raises(dataset.Suggest.ErSuggestCount,
                            'нельзя закрывать больше'):
                await s.done(count=188)

            tap.ok(await s.done(count=17,
                                reason={'code': 'TRASH_TTL'}),
                   'закрываем саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )

        with next(sl for sl in stocks if sl.shelf_type == 'trash') as s:
            tap.eq(s.shelf_type, 'trash', 'остаток на списании')
            tap.eq(s.count, 17, 'количество')
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(len(s.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                s.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_TTL',
                'Код записан'
            )
        with next(r for r in order.required
                  if r.product_id == product.product_id) as r:
            tap.eq(r.result_count, 17, 'количество принятого')
