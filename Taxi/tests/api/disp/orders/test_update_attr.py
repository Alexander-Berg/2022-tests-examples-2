# pylint: disable=too-many-statements
import pytest


@pytest.mark.parametrize(
    'role',
    [
        'admin',
        'store_admin',
        'dc_admin',
        'support',
        'support_it',
    ]
)
async def test_success(tap, dataset, api, role):
    with tap.plan(33, 'юзер с доступом и нормальные данные'):
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='approving',
            estatus='begin',
        )

        tap.eq(order.type, 'acceptance', 'ордер приемки создан')

        order.attr['foo'] = 'bar'
        order.attr['upd'] = [{'upd_number': 'xxx'}]

        await order.save()
        tap.eq(order.attr['foo'], 'bar', 'добавили поле в аттр')
        tap.eq(
            order.attr['upd'],
            [{'upd_number': 'xxx'}],
            'добавили поле, которое перетрем',
        )

        t = await api()
        t.set_user(user)

        # только УПД

        await t.post_ok(
            'api_disp_orders_update_attr',
            json={
                'order_id': order.order_id,
                'type': 'acceptance',
                'attr': {
                    'upd': [
                        {
                            'upd_number': '123-abc',
                            'upd_date': '1970-01-01',
                            'invoice_number': None,
                            'invoice_date': None,
                        },
                    ],
                },
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_has('order.attr')
        t.json_is('order.attr.foo', 'bar')
        t.json_is('order.attr.upd.0.upd_number', '123-abc')
        t.json_is('order.attr.upd.0.upd_date', '1970-01-01')

        # УПД + накладная

        await t.post_ok(
            'api_disp_orders_update_attr',
            json={
                'order_id': order.order_id,
                'type': 'acceptance',
                'attr': {
                    'upd': [
                        {
                            'upd_number': '123-abc',
                            'upd_date': '1970-01-01',
                            'invoice_number': '123',
                            'invoice_date': '1970-01-01',
                        },
                    ],
                },
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_has('order.attr')
        t.json_is('order.attr.foo', 'bar')
        t.json_is('order.attr.upd.0.upd_number', '123-abc')
        t.json_is('order.attr.upd.0.upd_date', '1970-01-01')
        t.json_is('order.attr.upd.0.invoice_number', '123')
        t.json_is('order.attr.upd.0.invoice_date', '1970-01-01')

        # два документа

        await t.post_ok(
            'api_disp_orders_update_attr',
            json={
                'order_id': order.order_id,
                'type': 'acceptance',
                'attr': {
                    'upd': [
                        {
                            'upd_number': '123-abc',
                            'upd_date': '1970-01-01',
                        },
                        {
                            'upd_number': '123-abc',
                            'upd_date': '1970-01-01',
                            'invoice_number': '123',
                            'invoice_date': '1970-01-01',
                        },
                    ],
                },
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('order')
        t.json_has('order.attr')
        t.json_is('order.attr.foo', 'bar')

        t.json_is('order.attr.upd.0.upd_number', '123-abc')
        t.json_is('order.attr.upd.0.upd_date', '1970-01-01')

        t.json_is('order.attr.upd.1.upd_number', '123-abc')
        t.json_is('order.attr.upd.1.upd_date', '1970-01-01')
        t.json_is('order.attr.upd.1.invoice_number', '123')
        t.json_is('order.attr.upd.1.invoice_date', '1970-01-01')


@pytest.mark.parametrize(
    'attr',
    [
        {
            'некорректный ключ': [
                {
                    'upd_number': '123-abc',
                    'upd_date': '1970-01-01',
                },
            ],
        },
        {
            'upd': 'некорректное значение',
        },
        {
            'upd': [],
        },
        {
            'upd': [
                {
                    'upd_number': '123-abc',
                    'upd_date': '1970-01-01',
                },
            ],
        },
        {
            'upd': [
                {
                    'upd_number': '123-abc',
                    'upd_date': '1970-01-01',
                    'invoice_number': '123',
                    'invoice_date': '1970-01-01',

                    'левый': 'ключ',
                },
            ],
        },
        {
            'upd': [
                {
                    'upd_number': '123-abc',
                    'upd_date': '1970-01-01',
                },
                {
                    'левый': 'объект',
                },
            ],
        },
    ]
)
async def test_bad_payload(tap, dataset, api, attr):
    with tap.plan(4, 'некорректный формат документов'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='approving',
            estatus='begin',
        )

        tap.ok(order, 'ордер создан')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_disp_orders_update_attr',
            json={
                'order_id': order.order_id,
                'type': 'order',
                'attr': attr,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


@pytest.mark.parametrize(
    'order_type',
    [
        'order',
        'shipment',
        'stowage',
        'move',
        'writeoff',
        'check',
        'check_product_on_shelf',
        'check_more',
        'writeoff_prepare_day',
        'check_valid_short',
        'check_valid_regular',
        'stop_list',
        'refund',
        'inventory',
        'inventory_check_more',
        'inventory_check_product_on_shelf',
    ],
)
async def test_bad_order_type(tap, dataset, api, order_type):
    with tap.plan(4, 'некорректный тип ордера'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        order = await dataset.order(
            store=store,
            type=order_type,
            status='approving',
            estatus='begin',
        )

        tap.eq(order.type, order_type, 'ордер создан')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_disp_orders_update_attr',
            json={
                'order_id': order.order_id,
                'type': 'acceptance',
                'attr': {
                    'upd': [
                        {
                            'upd_number': '123-abc',
                            'upd_date': '1970-01-01',
                        },
                    ],
                }
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


@pytest.mark.parametrize('order_status', ['canceled', 'failed'])
async def test_bad_order_status(tap, dataset, api, order_status):
    with tap.plan(4, 'статус заказа, когда уже не имеет смысла обновлять'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        order = await dataset.order(
            store=store,
            type='acceptance',
            status=order_status,
            estatus='begin',
        )

        tap.eq(order.status, order_status, 'ордер создан')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_disp_orders_update_attr',
            json={
                'order_id': order.order_id,
                'type': 'acceptance',
                'attr': {
                    'upd': [
                        {
                            'upd_number': '123-abc',
                            'upd_date': '1970-01-01',
                        },
                    ],
                },
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
