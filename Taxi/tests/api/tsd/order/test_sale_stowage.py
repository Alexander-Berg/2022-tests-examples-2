async def test_sale_stowage(tap, api, dataset, wait_order_status):
    with tap.plan(19, 'Ошибки при незавершённых саджестах'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар 2 создан')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='sale_stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                },
                {
                    'product_id': product2.product_id,
                    'count': 1,
                    'maybe_count': True,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Order is not waiting')

        await wait_order_status(order, ('processing', 'waiting'))

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message', 'Some suggests have to be done')

        count = 0
        for s in await dataset.Suggest.list_by_order(order):
            count += 1
            if s.product_id == product.product_id:
                tap.ok(await s.done(), 'завершён саджест')
        tap.eq(count, 2, 'всего два саджеста')

        await wait_order_status(order, ('processing', 'waiting'))

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(200, diag=True, desc='При закрытых саджестах всё ок')


async def test_sale_stowage_status_error(tap, api, dataset, wait_order_status):
    with tap.plan(10, 'Ошибки при саджестах с ошибкой'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар 2 создан')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='sale_stowage',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                },
                {
                    'product_id': product2.product_id,
                    'count': 1,
                    'maybe_count': True,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        t = await api(user=user)

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        for s in suggests:
            s.status = 'error'
            await s.save()

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_INCOMPLETE_SUGGESTS')
        t.json_is('message', 'Some suggests have to be done')


async def test_trash_with_role_up(api, tap, dataset, wait_order_status):
    with tap.plan(19, 'Запрещаем списывать без поднятия роли'):
        store = await dataset.full_store()

        product1 = await dataset.product()

        product2 = await dataset.product()

        user = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer'
        )

        order = await dataset.order(
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 7,
                    'maybe_count': True
                },
                {
                    'product_id': product2.product_id,
                    'count': 9,
                    'maybe_count': True
                }
            ],
            store=store,
            status='reserving'
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)

        for s in suggests:
            if s.count == 7:
                tap.ok(
                    await s.done(
                        count=2,
                        user=user
                    ),
                    'разложили один продукт'
                )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )

        for s in suggests:
            if s.count == 5:
                tap.ok(
                    await s.done(
                        count=2,
                        user=user
                    ),
                    'разложили еще продукт'
                )

        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(403, diag=True)

        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(
            user=user,
            spec='doc/api/tsd/user.yaml',
        )

        await t.post_ok(
            'api_tsd_user_upgrade',
            json={'pin': user.pin}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t = await api(token=t.res['json']['token'])
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(200, diag=True)

        while order.vars('stage') != 'trash':
            await wait_order_status(order, ('processing', 'waiting'))

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        async for stock in dataset.Stock.ilist(
            by='look',
            conditions=(
                ('store_id', store.store_id)
            ),
        ):
            shelf_type = 'trash'
            if stock.count == 2:
                shelf_type = 'store'
            tap.eq(stock.shelf_type, shelf_type, 'Правильный тип полки')


async def test_no_need_role_up(api, tap, dataset, wait_order_status):
    with tap.plan(6, 'Поднятие роли не требуется'):
        store = await dataset.full_store()

        product1 = await dataset.product()

        product2 = await dataset.product()

        user = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer'
        )

        order = await dataset.order(
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 6,
                    'maybe_count': True
                },
                {
                    'product_id': product2.product_id,
                    'count': 9,
                    'maybe_count': True
                }
            ],
            store=store,
            status='reserving'
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)

        for s in suggests:
            await s.done(
                count=s.count,
                user=user
            )

        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(200, diag=True)

        while order.vars('stage') != 'trash':
            await wait_order_status(order, ('processing', 'waiting'))

        await wait_order_status(order, ('complete', 'done'), user_done=user)
