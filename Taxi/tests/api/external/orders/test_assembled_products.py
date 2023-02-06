import pytest


@pytest.mark.parametrize('status,estatus,order_vars,expected', [
    (
        'complete',
        'done',
        {'assembled_products': []},
        []
    ),
    (
        'canceled',
        'begin',
        {
            'assembled_products': [
                {
                    'product_id': 'abcd',
                    'product_type': 'product',
                    'count': 1,
                }
            ]
        },
        [
            {
                'product_id': 'abcd',
                'product_type': 'product',
                'count': 1,
            }
        ],
    ),
    (
        'failed',
        'done',
        {
            'assembled_products': [
                {
                    'product_id': 'abcd',
                    'product_type': 'sample',
                    'count': 1,
                    'true_mark': 'lolkek',
                    'trash': 'trash here',
                }
            ]
        },
        [
            {
                'product_id': 'abcd',
                'product_type': 'sample',
                'count': 1,
                'true_mark': 'lolkek',
            }
        ],
    ),
    (
        'failed',
        'done',
        {},
        [],
    ),
])
async def test_success(
        tap, dataset, api,
        status, estatus, order_vars, expected
):
    with tap.plan(5, 'Успешно получаем данные'):
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            status=status,
            estatus=estatus,
            type='order',
            vars=order_vars,
        )
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_assembled_products',
            json={
                'store_id': store.store_id,
                'external_id': order.external_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assembled_products')
        tap.eq(
            t.res['json']['assembled_products'],
            expected,
            'В ответе все, что ожидали',
        )


async def test_company_token(tap, dataset, api):
    with tap.plan(5, 'Доступ по токену компании'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        order = await dataset.order(
            store=store,
            status='complete',
            estatus='done',
            type='order',
            vars={
                'assembled_products': [
                    {
                        'product_id': 'abcd',
                        'product_type': 'product',
                        'count': 1,
                    }
                ]
            },
        )
        t = await api(token=company.token)
        await t.post_ok(
            'api_external_orders_assembled_products',
            json={
                'store_id': store.store_id,
                'external_id': order.external_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assembled_products')
        tap.eq(
            t.res['json']['assembled_products'],
            [{
                'product_id': 'abcd',
                'product_type': 'product',
                'count': 1,
            }],
            'В ответе все, что ожидали',
        )


async def test_company_token_failure(tap, dataset, api):
    with tap.plan(3, 'Компания пошла не за своим заказом'):
        company = await dataset.company()
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            status='complete',
            estatus='done',
            type='order',
            vars={
                'assembled_products': [
                    {
                        'product_id': 'abcd',
                        'product_type': 'product',
                        'count': 1,
                    }
                ]
            },
        )
        t = await api(token=company.token)
        await t.post_ok(
            'api_external_orders_assembled_products',
            json={
                'store_id': store.store_id,
                'external_id': order.external_id,
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_missing_order(tap, dataset, api, uuid):
    with tap.plan(3, 'Не нашли документ'):
        store = await dataset.store()
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_assembled_products',
            json={
                'store_id': store.store_id,
                'external_id': uuid(),
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize(
    'status,estatus,order_type,http_code,expected_code',
    [
        ('request', 'waiting', 'order', 409, 'ER_CONFLICT'),
        ('complete', 'begin', 'order', 409, 'ER_CONFLICT'),
        ('complete', 'done', 'acceptance', 400, 'ER_BAD_REQUEST'),
    ]
)
async def test_order_status_failure(
        tap, dataset, api,
        status, estatus, order_type, http_code, expected_code
):
    with tap.plan(3, 'Ошибка из-за статуса заказа'):
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            status=status,
            estatus=estatus,
            type=order_type,
            vars={
                'assembled_products': [
                    {
                        'product_id': 'abcd',
                        'product_type': 'product',
                        'count': 1,
                    }
                ]
            },
        )
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_orders_assembled_products',
            json={
                'store_id': store.store_id,
                'external_id': order.external_id,
            }
        )
        t.status_is(http_code, diag=True)
        t.json_is('code', expected_code)
