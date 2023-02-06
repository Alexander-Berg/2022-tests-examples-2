async def test_common(tap, dataset, api):
    with tap.plan(10, 'назначение исполнителей'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        order = await dataset.order(
            company_id=admin.company_id,
            store_id=admin.store_id,
            status='processing',
        )
        tap.ok(order, 'order created')

        user = await dataset.user(
            company_id=order.company_id,
            store_id=order.store_id,
        )
        tap.ok(user, 'user created')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': order.order_id,
                  'users': [user.user_id]}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.users', [user.user_id])

        await order.reload()

        tap.eq(order.users, [user.user_id], 'users changed')


async def test_same_users(tap, dataset, api):
    with tap.plan(11, 'исполнители уже те же, что в запросе'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(
            company_id=admin.company_id,
            store_id=admin.store_id,
        )
        tap.ok(user, 'user created')

        order = await dataset.order(
            company_id=admin.company_id,
            store_id=admin.store_id,
            status='processing',
            users=[user.user_id],
        )
        tap.ok(order, 'order created')
        tap.eq(order.users, [user.user_id], 'users set')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': order.order_id,
                  'users': [user.user_id]}
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.users', [user.user_id])

        await order.reload()

        tap.eq(order.users, [user.user_id], 'users remain')


async def test_empty_users(tap, dataset, api):
    with tap.plan(7, 'передача пустого списка в запросе'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(
            company_id=admin.company_id,
            store_id=admin.store_id,
        )
        tap.ok(user, 'user created')

        order = await dataset.order(
            company_id=admin.company_id,
            store_id=admin.store_id,
            status='processing',
            users=[user.user_id],
        )
        tap.ok(order, 'order created')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': order.order_id,
                  'users': []}
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_USERS_EMPTY')

        await order.reload()

        tap.eq(order.users, [user.user_id], 'users remain')


async def test_unknown_order(tap, dataset, api, uuid):
    with tap.plan(5, 'обращение к неизвестному заказу'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(
            company_id=admin.company_id,
            store_id=admin.store_id,
        )
        tap.ok(user, 'user created')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': uuid(),
                  'users': [user.user_id]}
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_order_not_processing(tap, dataset, api):
    with tap.plan(8, 'статус заказа не processing'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(
            company_id=admin.company_id,
            store_id=admin.store_id,
        )
        tap.ok(user, 'user created')

        order = await dataset.order(
            company_id=admin.company_id,
            store_id=admin.store_id,
            users=[user.user_id],
        )
        tap.ok(order, 'order created')
        tap.eq(order.users, [user.user_id], 'users set')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': order.order_id,
                  'users': [user.user_id]}
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_ORDER_IS_NOT_PROCESSING')

        await order.reload()

        tap.eq(order.users, [user.user_id], 'users remain')


async def test_user_not_found(tap, dataset, api, uuid):
    with tap.plan(8, 'назначение неизвестного исполнителя'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(
            company_id=admin.company_id,
            store_id=admin.store_id,
        )
        tap.ok(user, 'user created')

        order = await dataset.order(
            company_id=admin.company_id,
            store_id=admin.store_id,
            status='processing',
            users=[user.user_id],
        )
        tap.ok(order, 'order created')
        tap.eq(order.users, [user.user_id], 'users set')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': order.order_id,
                  'users': [user.user_id, uuid()]}
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_USER_NOT_FOUND')

        await order.reload()

        tap.eq(order.users, [user.user_id], 'users remain')


async def test_permits_check(tap, dataset, api):
    with tap.plan(7, 'проверка доступа пользователя к заказу'):
        admin = await dataset.user(role='admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(
            company_id=admin.company_id,
            store_id=admin.store_id,
            role='stocktaker',
        )
        tap.ok(user, 'user created')

        order = await dataset.order(
            company_id=admin.company_id,
            store_id=admin.store_id,
            status='processing',
        )
        tap.ok(order, 'order created')

        t = await api(user=admin)
        await t.post_ok(
            'api_disp_orders_set_users',
            json={'order_id': order.order_id,
                  'users': [user.user_id]}
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_WRONG_USER_FOR_ORDER')

        await order.reload()

        tap.eq(order.users, [], 'users not set')
