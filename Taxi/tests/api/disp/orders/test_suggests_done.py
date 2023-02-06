# pylint: disable=unused-variable


async def test_done(tap, dataset, api, now, wait_order_status):
    with tap.plan(10, 'Завершение саджеста по заказу'):

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        product = await dataset.product()
        stock   = await dataset.stock(store=store, product=product, count=100)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            required = [
                {'product_id': product.product_id, 'count': 10},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты')

        with suggests[0] as suggest:
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={'suggest_id': suggest.suggest_id, 'status': 'done'},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
            t.json_is('suggest.status', 'done')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')


async def test_production(tap, dataset, api, now, wait_order_status, cfg):
    with tap.plan(5, 'Только в тестинге'):

        cfg.set('mode', 'production')

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        product = await dataset.product()
        stock   = await dataset.stock(store=store, product=product, count=100)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=now(),
            required = [
                {'product_id': product.product_id, 'count': 10},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты')

        with suggests[0] as suggest:
            t = await api(user=user)
            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={'suggest_id': suggest.suggest_id, 'status': 'done'},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_TESTING_ONLY')


async def test_suggest_check_more(
        tap, dataset, api, wait_order_status, cfg):
    with tap.plan(28, 'Завершение саджеста проверки'):
        cfg.set(
            'business.order.inventory_check_more.upversion_each_check_more',
            True
        )
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        tap.ok(await dataset.shelf(
            store=store,
            type='lost',
        ), 'полка lost')

        tap.ok(await dataset.shelf(
            store=store,
            type='found',
        ), 'полка found')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        stock2 = await dataset.stock(store=store,
                                     shelf_id=stock.shelf_id)
        tap.eq(stock2.shelf_id, stock.shelf_id, 'на той же полке ещё сток')

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[{'shelf_id': stock.shelf_id}],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(order.shelves, [stock.shelf_id], 'shelves заполнился')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на полку')
        t = await api(user=user)

        with suggests[0] as suggest:
            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'status': 'done',
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': product.product_id,
                    'status': 'done',
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': product.product_id,
                    'count': 0,
                    'status': 'done',
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': product.product_id,
                    'count': 20,
                    'status': 'done',

                },
            )
            t.status_is(200, diag=True)

            await suggest.reload()
            tap.eq(suggest.status, 'done', 'саджест закрыт')
            tap.eq(suggest.product_id, product.product_id, 'продукт')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест на полку')
        tap.ok(
            await suggests[0].done(status='error'),
            'работу с саджестами завершаем'
        )


# pylint: disable=too-many-statements
async def test_done_with_weight(tap, dataset, api, wait_order_status):
    with tap.plan(44, 'Завершение саджеста по заказу'):

        store   = await dataset.full_store()
        user    = await dataset.user(store=store)

        parent, *childs = await dataset.weight_products()

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                    'count': 10,
                }
            ]
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты')
        t = await api(user=user)
        with suggests[0] as suggest:
            tap.ok(suggest.type, 'shelf2box', 'shelf2box')
            tap.ok(suggest.product_id, parent.product_id, 'product_id')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': childs[1].product_id,
                    'status': 'done',
                    'weight': 3000,
                    'count': 10,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': parent.product_id,
                    'status': 'done',
                    'weight': 3000,
                    'count': 1,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')
            t.json_has('message', 'Could not identify child')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': parent.product_id,
                    'status': 'done',
                    'weight': 1000,
                    'count': 10,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
            t.json_is('suggest.status', 'done')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'Саджесты')

        with suggests[0] as suggest:
            tap.ok(suggest.type, 'box2shelf', 'box2shelf')
            tap.ok(
                suggest.product_id,
                childs[0].product_id,
                'product_id'
            )
            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': childs[1].product_id,
                    'status': 'done',
                    'weight': 1000,
                    'count': 10,
                },
            )
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')
            t.json_has('message', 'Not right weight for kid')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': childs[0].product_id,
                    'status': 'done',
                    'weight': 1000,
                    'count': 10,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
            t.json_is('suggest.status', 'done')

            tap.ok(await suggest.reload(), 'саджест перегружен')
            tap.eq(suggest.status, 'done', 'саджест завершён')
            tap.eq_ok(suggest.user_done, user.user_id, 'user_done')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'Саджесты')

        with suggests[0] as suggest:
            tap.ok(suggest.type, 'shelf2box', 'shelf2box')
            tap.ok(suggest.product_id, parent.product_id, 'product_id')

            await t.post_ok(
                'api_disp_orders_suggests_done',
                json={
                    'suggest_id': suggest.suggest_id,
                    'product_id': parent.product_id,
                    'status': 'done',
                    'weight': 0,
                    'count': 0,
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'Suggest was done.')
        await wait_order_status(order, ('complete', 'done'), user_done=user)


async def test_done_true_mark(tap, dataset, api, uuid):
    with tap.plan(14, 'Завершение марочного саджеста'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        product_barcode = '1' + uuid()[:13]
        product = await dataset.product(barcode=[product_barcode])
        stock = await dataset.stock(store=store, count=10, product=product)
        order = await dataset.order(
            store=store,
            type='order',
            status='processing',
            estatus='waiting',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 2,
                }
            ],
            acks=[user.user_id],
            users=[user.user_id],

        )
        suggest_one = await dataset.suggest(
            type='shelf2box',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )
        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_suggests_done',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_TRUE_MARK_REQUIRED')

        await t.post_ok(
            'api_disp_orders_suggests_done',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': '123456789',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_INVALID_TRUE_MARK')

        true_mark = '0199999999999999215Qbag!\x1D93Zjqw'

        await t.post_ok(
            'api_disp_orders_suggests_done',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': true_mark,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WRONG_PRODUCT_TRUE_MARK')

        correct_true_mark_one = f'01{product_barcode}215Qbag!\x1D93Zjqw'
        await t.post_ok(
            'api_disp_orders_suggests_done',
            json={
                'suggest_id': suggest_one.suggest_id,
                'status': 'done',
                'count': 1,
                'true_mark': correct_true_mark_one,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await suggest_one.reload(), 'Перезабрали саджест')

        tap.eq(
            suggest_one.vars('true_mark', None),
            correct_true_mark_one,
            'Марка нужная в саджесте',
        )
