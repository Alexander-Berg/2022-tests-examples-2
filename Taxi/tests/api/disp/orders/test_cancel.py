import pytest

from stall.model.role import PERMITS

ROLES = [
    role for role in PERMITS['roles']
    if not PERMITS['roles'][role].get('virtual', False)
]


@pytest.mark.parametrize('role', ROLES)
async def test_cancel_from_dispatcher(tap, dataset, api, role):
    with tap.plan(8):
        user = await dataset.user(role=role)

        tap.ok(user, f'User created: {role}')

        order = await dataset.order(
            store_id=user.store_id, source='dispatcher'
        )

        tap.ok(order, f'Order created: {order.source}')

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_cancel',
            json={'order_id': order.order_id},
        )

        if role in {'admin', 'support_it', 'support', 'company_admin'}:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('order.status', order.status)
            t.json_is('order.target', 'canceled')
            t.json_is('order.user_done', user.user_id)
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_has('message')


@pytest.mark.parametrize('role', [
    'admin', 'support_it', 'support', 'company_admin',
])
async def test_cancel_with_comment(tap, dataset, api, role):
    with tap.plan(17):
        user = await dataset.user(role=role)
        tap.ok(user, f'User created: {role}')

        t = await api(user=user)

        # Валидный комментарий

        order = await dataset.order(
            store_id=user.store_id, source='dispatcher'
        )
        tap.ok(order, f'Order created: {order.source}')

        comment = 'Комментарий при отмене из диспетчерской'
        await t.post_ok(
            'api_disp_orders_cancel',
            json={
                'order_id': order.order_id,
                'comment': comment,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.status', order.status)
        t.json_is('order.target', 'canceled')
        t.json_is('order.user_done', user.user_id)
        t.json_is('order.attr.cancel_comment', comment)

        # Короткий комментарий

        order = await dataset.order(
            store_id=user.store_id, source='dispatcher'
        )
        tap.ok(order, f'Order created: {order.source}')

        comment = 'UO'
        await t.post_ok(
            'api_disp_orders_cancel',
            json={
                'order_id': order.order_id,
                'comment': comment,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        #  Длинный комментарий

        order = await dataset.order(
            store_id=user.store_id, source='dispatcher'
        )
        tap.ok(order, f'Order created: {order.source}')

        comment = 'x' * 501
        await t.post_ok(
            'api_disp_orders_cancel',
            json={
                'order_id': order.order_id,
                'comment': comment,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


@pytest.mark.parametrize('role', ROLES)
async def test_cancel_from_eda(tap, dataset, api, role):
    with tap.plan(8):
        user = await dataset.user(role=role)

        tap.ok(user, f'User created: {role}')

        order = await dataset.order(store_id=user.store_id, source='eda')

        tap.ok(order, f'Order created: {order.source}')

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_cancel',
            json={'order_id': order.order_id},
        )

        if role in {'admin', 'support_it', 'support', 'company_admin'}:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('order.status', order.status)
            t.json_is('order.target', 'canceled')
            t.json_is('order.user_done', user.user_id)
        # elif role == 'store_admin':
        #     t.status_is(403, diag=True)
        #     t.json_is('code', 'ER_ACCESS')
        #     t.json_is('code', 'ER_ACCESS')
        #     t.json_is('code', 'ER_ACCESS')
        #     t.json_is(
        #         'message', 'Order cancelation needs additional permissions'
        #     )
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_has('message')


@pytest.mark.parametrize('status', ['complete', 'failed'])
async def test_noncancelable_order(tap, dataset, api, status):
    with tap.plan(4):
        user = await dataset.user(role='admin')
        order = await dataset.order(store_id=user.store_id,
                                    status=status,
                                    type='writeoff')

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_cancel',
            json={'order_id': order.order_id},
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Order has already done')


@pytest.mark.parametrize('status', ['canceled', ])
async def test_retry_order(tap, dataset, api, status):
    with tap.plan(2):
        user = await dataset.user(role='admin')
        order = await dataset.order(store_id=user.store_id,
                                    status=status,
                                    type='writeoff')

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_cancel',
            json={'order_id': order.order_id},
        )

        t.status_is(200, diag=True)


@pytest.mark.parametrize(
    'role,permitted,prohibited',
    [
        [
            'support',
            ['writeoff', 'writeoff_prepare_day', 'order',
             'check_valid_regular', 'check_valid_short',
             'stop_list', 'check_more'],
            ['acceptance', 'inventory'],
        ],
        [
            'support_ro',
            [],
            ['writeoff', 'writeoff_prepare_day', 'order',
             'check_valid_regular', 'check_valid_short', 'stop_list',
             'acceptance', 'inventory', 'check_more'],
        ],
        [
            'support_it',
            ['writeoff', 'writeoff_prepare_day',
             'check_valid_regular', 'check_valid_short', 'stop_list',
             'order', 'check_product_on_shelf', 'check_more'],
            ['move'],
        ],
        [
            'vice_store_admin',
            ['writeoff'],
            ['writeoff_prepare_day', 'check_valid_regular',
             'stop_list', 'check_valid_short', 'acceptance',
             'order', 'inventory', 'check_more'],
        ],
        [
            'store_admin',
            ['writeoff'],
            ['writeoff_prepare_day', 'check_valid_regular',
             'stop_list', 'check_valid_short', 'acceptance',
             'order', 'inventory', 'check_more'],
        ],
        [
            'employee_audit',
            ['inventory', 'check_more'],
            ['writeoff', 'writeoff_prepare_day', 'check_valid_regular',
             'stop_list', 'check_valid_short', 'acceptance', 'order'],
        ],
        [
            'chief_audit',
            ['writeoff', 'inventory',
             'stop_list', 'check_more'],
            ['writeoff_prepare_day', 'order', 'check_valid_regular',
             'check_valid_short', 'acceptance'],
        ],
    ]
)
async def test_cancel_by_type_from_disp(tap, dataset, api, role,
                                        permitted, prohibited):
    with tap.plan(63):
        store = await dataset.store()

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        for order_type in permitted:
            order = await dataset.order(
                store_id=user.store_id, source='dispatcher',
                type=order_type
            )
            tap.ok(order, f'Order created: {order.source}')

            await t.post_ok(
                'api_disp_orders_cancel',
                json={'order_id': order.order_id},
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('order.status', order.status)
            t.json_is('order.target', 'canceled')
            t.json_is('order.user_done', user.user_id)

        for order_type in prohibited:
            order = await dataset.order(
                store_id=user.store_id, source='dispatcher',
                type=order_type
            )
            tap.ok(order, f'Order created: {order.source}')

            await t.post_ok(
                'api_disp_orders_cancel',
                json={'order_id': order.order_id},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
