# pylint: disable=invalid-name


async def test_get_status_not_found(tap, dataset, uuid, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_integration_orders_get_status', json={
            'store_id': store.store_id,
            'external_id': uuid(),
        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('details.message', 'Order not found')


async def test_get_status(tap, dataset, api):
    with tap.plan(7):
        t = await api(role='token:web.external.tokens.0')

        order = await dataset.order(status='reserving')
        tap.ok(order, 'заказ создан')

        await t.post_ok('api_integration_orders_get_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
        })
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.store_id', order.store_id, 'лавка')
        t.json_is('order.external_id',
                  order.external_id,
                  'external_id в ответе')
        t.json_is('order.status', 'reserving', 'reserving')


async def test_get_status_company(tap, dataset, api):
    with tap.plan(7, 'Получение статуса по ключу компании'):
        company = await dataset.company()
        store   = await dataset.store(company=company)

        t = await api(token=company.token)

        order = await dataset.order(store=store, status='reserving')

        await t.post_ok('api_integration_orders_get_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
        })
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.company_id', order.company_id)
        t.json_is('order.store_id', order.store_id)
        t.json_is('order.external_id', order.external_id)
        t.json_is('order.status', 'reserving')


async def test_get_status_company_not_owner(tap, dataset, api):
    with tap.plan(3, 'Получение статуса по ключу компании с чужого склада'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store   = await dataset.store(company=company1)

        t = await api(token=company2.token)

        order = await dataset.order(store=store, status='reserving')

        await t.post_ok('api_integration_orders_get_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
