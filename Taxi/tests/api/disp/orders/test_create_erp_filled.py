import pytest

from stall.model.role import PERMITS


@pytest.mark.parametrize('role', [
    'admin',
    'company_admin'
])
async def test_order(tap, dataset, api, uuid, role):
    with tap.plan(5, 'Создание заказа клиента'):
        product = await dataset.product()
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        admin = await dataset.user(role=role, store=store)
        tap.eq(admin.role, role, 'роль')
        courier = await dataset.user(role='courier', store=store)

        t = await api(user=admin)

        external_id = uuid()

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'order',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': admin.user_id,
                            'dispatch_type': 'grocery',
                            'courier_id': courier.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_acceptance(tap, dataset, api, uuid):
    with tap.plan(5, 'Создание заказа приёмки'):
        product = await dataset.product()
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.role, 'admin', 'роль')
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_acceptance_er(tap, dataset, api, uuid):
    with tap.plan(6, 'Создание заказа приёмки с ошибкой доступа'):
        product = await dataset.product()
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        user = await dataset.user(role='company_admin', store=store)
        tap.eq(user.role, 'company_admin', 'роль')
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'The order must be created from ERP only')


async def test_shipment(tap, dataset, api, uuid):
    with tap.plan(5, 'Создание отгрузки'):
        product = await dataset.product()
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        user = await dataset.user(role='admin', store=store)
        tap.eq(user.role, 'admin', 'роль')
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'shipment',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'price_type': 'store',
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_shipment_er(tap, dataset, api, uuid):
    with tap.plan(6, 'Создание отгрузки c ошибкой доступа'):
        product = await dataset.product()
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        user = await dataset.user(role='company_admin', store=store)
        tap.eq(user.role, 'company_admin', 'роль')
        t = await api(user=user)

        external_id = uuid()
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'shipment',
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 10,
                                    'price_type': 'store',
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'The order must be created from ERP only')


async def test_shipment_rollback(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(7, 'Возврат отгрузки'):
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        user = await dataset.user(store=store, role='admin')
        tap.eq(user.role, 'admin', 'роль')

        item = await dataset.item(store=store)

        product = await dataset.product()

        await dataset.stock(
            product=product,
            store=store,
            count=27
        )

        await dataset.stock(
            item=item,
            store=store,
            count=1
        )

        shipment = await dataset.order(
            type='shipment',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 25,
                },
                {
                    'item_id': item.item_id,
                }
            ]
        )
        tap.eq(shipment.store_id, store.store_id, 'заказ создан')
        await wait_order_status(shipment, ('complete', 'done'), user_done=user)


        t = await api(user=user)

        external_id = uuid()

        tap.note('Рефандим часть')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 15
                    },
                    {
                        'item_id': item.item_id,
                    }
                ],
                'approved': True,
                'ack': user.user_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_shipment_rollback_er(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(8, 'Возврата отгрузки с ошибкой доступа'):
        company = await dataset.company(instance_erp='ru')
        tap.eq(company.instance_erp, 'ru', 'ERP система')
        store = await dataset.store(company=company)

        user = await dataset.user(store=store, role='support_it')
        tap.eq(user.role, 'support_it', 'роль')

        item = await dataset.item(store=store)

        product = await dataset.product()

        await dataset.stock(
            product=product,
            store=store,
            count=27
        )

        await dataset.stock(
            item=item,
            store=store,
            count=1
        )

        shipment = await dataset.order(
            type='shipment',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 25,
                },
                {
                    'item_id': item.item_id,
                }
            ]
        )
        tap.eq(shipment.store_id, store.store_id, 'заказ создан')
        await wait_order_status(shipment, ('complete', 'done'), user_done=user)

        t = await api(user=user)

        external_id = uuid()

        tap.note('Рефандим часть')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 15
                    },
                    {
                        'item_id': item.item_id,
                    }
                ],
                'approved': True,
                'ack': user.user_id,
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'The order must be created from ERP only')


def _get_roles_with_permit(permit: str):
    """Возвращает все роли с указанным пермитом"""
    return [r for r, p in PERMITS['roles'].items() if p['permits'].get(permit)]


async def test_erp_permit(tap):
    with tap.plan(2, 'Проверка пермита у ролей'):
        roles = _get_roles_with_permit('create_order_bypass_erp')
        tap.eq(len(roles), 1, 'количество ролей')
        tap.eq(roles[0], 'admin', 'роль')
