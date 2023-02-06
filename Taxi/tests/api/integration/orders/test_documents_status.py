import pytest


@pytest.mark.parametrize('status', ['processing', 'rescan', 'done'])
async def test_documents_status(tap, dataset, api, status):
    with tap.plan(5, 'Обычный флоу с разными статусами'):
        t = await api(role='token:web.external.tokens.0')

        order = await dataset.order(type='acceptance')

        await t.post_ok('api_integration_orders_documents_status', json={
            'order_id': order.order_id,
            'status': status
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await order.reload()

        tap.eq(order.attr['documents_status'], status, 'status')
        tap.eq(order.attr.get('documents_comment'), None, 'Нет комментария')


async def test_status_company(tap, dataset, api):
    with tap.plan(5, 'Изменение статуса документов по ключу компании'):
        company = await dataset.company()
        store = await dataset.store(company=company)

        t = await api(token=company.token)

        order = await dataset.order(type='acceptance', store=store)

        await t.post_ok('api_integration_orders_documents_status', json={
            'order_id': order.order_id,
            'status': 'done',
            'comment': 'Some text'
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await order.reload()

        tap.eq(order.attr['documents_status'], 'done', 'status')
        tap.eq(
            order.attr.get('documents_comment'), 'Some text',
            'Комментарий'
        )


async def test_status_company_not_owner(tap, dataset, api):
    with tap.plan(3, 'Изменение статуса документов с другого склада'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store = await dataset.store(company=company1)

        t = await api(token=company2.token)

        order = await dataset.order(store=store, status='reserving')

        await t.post_ok('api_integration_orders_documents_status', json={
            'order_id': order.order_id,
            'status': 'done'
        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_incorrect_order_id(tap, uuid, api):
    with tap.plan(4, 'В запросе невалидный order_id'):
        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_integration_orders_documents_status', json={
            'order_id': uuid(),
            'status': 'done'
        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('details.message', 'Order not found')
