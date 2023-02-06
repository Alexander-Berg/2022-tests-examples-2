async def test_agree(tap, dataset, wait_order_status):
    with tap.plan(24, 'Доверительная приёмка'):
        store = await dataset.full_store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        p1 = await dataset.product()
        tap.ok(p1, 'товар сгенерирован')

        p2 = await dataset.product()
        tap.ok(p2, 'ещё товар сгенерирован')

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],

            required=[
                {
                    'product_id': p1.product_id,
                    'count': 27,
                },
                {
                    'product_id': p2.product_id,
                    'count': 35,
                }
            ]
        )

        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.type, 'acceptance', 'тип')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты прочитаны')
        tap.eq(len(suggests), 2, 'их два')

        s1 = list(s for s in suggests if s.product_id == p1.product_id)[0]
        s2 = list(s for s in suggests if s.product_id == p2.product_id)[0]

        tap.ok(await s1.done(count=11), 'саджест 1 закрыт')
        tap.ok(await order.signal({'type': 'acceptance_agree'}),
               'сигнал отправлен')
        await wait_order_status(order, ('complete', 'begin'))
        tap.ok(await s2.reload(), 'саджест 2 перегружен')
        tap.eq(s2.status, 'request', 'статус остался незавершённым')

        await wait_order_status(order, ('complete', 'done'))

        stowage = await dataset.Order.load(order.vars('stowage_id'))
        tap.ok(stowage, 'раскладка сгенерирована')
        tap.eq(len(stowage.required), 2, 'две записи required')

        r1 = list(r for r in stowage.required if r.product_id == p1.product_id)
        r2 = list(r for r in stowage.required if r.product_id == p2.product_id)
        tap.ok(r1, 'required по первому продукту')
        tap.ok(r2, 'required по второму продукту')

        r1 = r1[0]
        r2 = r2[0]


        tap.eq(r1.count, 11, 'количество первого')
        tap.ok(not r1.maybe_count, 'точное количество первого')

        tap.eq(r2.count, 35, 'количество второго')
        tap.ok(r2.maybe_count, 'неточное количество второго')
