from datetime import timedelta

from libstall.util import time2time
from stall.model.analytics.revenue_tlog import (
    RevenueTlog,
    REVENUE_TLOG_SOURCES,
)


async def test_list_no_company(tap, api):
    with tap.plan(3, 'запрещаем ходить без токена компании'):
        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_revenues_list',
            json={'cursor': None},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_list_company(tap, dataset, api, now):
    with tap.plan(15, 'забор выручки по компанейскому токену'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store = await dataset.store(company=company1)

        rows = []

        for _ in range(2):
            order = await dataset.order(store=store)
            product = await dataset.product()
            rows.append(
                {
                    'company_id': store.company_id,
                    'store_id': store.store_id,
                    'order_id': order.order_id,
                    'source': REVENUE_TLOG_SOURCES[0],
                    'transaction_id': int(now().timestamp() * 1000_000),
                    'transaction_dttm': now(),
                    'raw_data': {
                        'transaction_type': 'payment',
                        'transaction_product': 'smth',
                        'transaction_detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'product_id': product.product_id,
                        'quantity': '300',
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                        'courier_id': order.courier_id,
                    }
                }
            )

        tap.ok(await RevenueTlog.insert_batch(rows), 'вставили пачку')

        t1 = await api(token=company1.token)
        await t1.post_ok(
            'api_integration_revenues_list',
            json={'cursor': None},
        )
        t1.status_is(200, diag=True)
        t1.json_is('code', 'OK')
        t1.json_has('cursor')
        t1.json_has('revenues')
        t1.json_has('revenues.0')
        t1.json_has('revenues.1')
        t1.json_hasnt('revenues.2')

        t2 = await api(token=company2.token)

        await t2.post_ok(
            'api_integration_revenues_list',
            json={'cursor': None},
        )

        t2.status_is(200, diag=True)
        t2.json_is('code', 'OK')
        t2.json_has('cursor')
        t2.json_has('revenues')
        t2.json_hasnt('revenues.0')


async def test_list_ordering(tap, dataset, api, now):
    with tap.plan(16, 'логи в корректном порядке'):
        company = await dataset.company()
        store = await dataset.store(company=company)

        rows = []

        for _ in range(3):
            order = await dataset.order(store=store)
            product = await dataset.product()
            rows.append(
                {
                    'company_id': store.company_id,
                    'store_id': store.store_id,
                    'order_id': order.order_id,
                    'source': REVENUE_TLOG_SOURCES[0],
                    'transaction_id': int(now().timestamp() * 1000_000),
                    'transaction_dttm': now(),
                    'raw_data': {
                        'transaction_type': 'payment',
                        'transaction_product': 'smth',
                        'transaction_detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'product_id': product.product_id,
                        'quantity': '300',
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                        'courier_id': order.courier_id,
                    }
                }
            )

        tap.ok(await RevenueTlog.insert_batch(rows), 'вставили пачку')

        t = await api(token=company.token)

        await t.post_ok(
            'api_integration_revenues_list',
            json={'cursor': None},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_has('revenues')

        cursor = t.res['json']['cursor']
        tap.ok(cursor, 'курсор не пустой')

        revenues = t.res['json']['revenues']
        tap.eq(len(revenues), 3, 'три записи')
        tap.eq(
            [i['transaction_id'] for i in revenues],
            sorted([i['transaction_id'] for i in revenues]),
            'корректный порядок',
        )

        await t.post_ok(
            'api_integration_revenues_list',
            json={'cursor': cursor},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', cursor)
        t.json_has('revenues')
        t.json_hasnt('revenues.0')


async def test_list_filters(tap, dataset, api, now):
    with tap.plan(38, 'фильтры для удобства выгрузки'):
        company = await dataset.company()
        store = await dataset.store(company=company)

        rows = []

        start_id = int(now().timestamp() * 1000_000)
        start_date = time2time('1970-01-01')

        for i in range(3):
            order = await dataset.order(store=store)
            product = await dataset.product()
            rows.append(
                {
                    'company_id': store.company_id,
                    'store_id': store.store_id,
                    'order_id': order.order_id,
                    'source': REVENUE_TLOG_SOURCES[0],
                    'transaction_id': start_id + i,
                    'transaction_dttm': start_date + timedelta(days=i),
                    'raw_data': {
                        'transaction_type': 'payment',
                        'transaction_product': 'smth',
                        'transaction_detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'product_id': product.product_id,
                        'quantity': '300',
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                        'courier_id': order.courier_id,
                    }
                }
            )

        tap.ok(await RevenueTlog.insert_batch(rows), 'вставили пачку')

        t = await api(token=company.token)

        await t.post_ok(
            'api_integration_revenues_list',
            json={
                'from_transaction_date': start_date.date(),
                'cursor': None,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('revenues')
        t.json_has('revenues.0')
        t.json_has('revenues.1')
        t.json_has('revenues.2')
        t.json_hasnt('revenues.3')

        await t.post_ok(
            'api_integration_revenues_list',
            json={
                'from_transaction_date': (
                    (start_date + timedelta(days=2)).date()
                ),
                'cursor': None,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('revenues')
        t.json_has('revenues.0')
        t.json_hasnt('revenues.1')

        await t.post_ok(
            'api_integration_revenues_list',
            json={
                'from_transaction_id': start_id,
                'cursor': None,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('revenues')
        t.json_has('revenues.0')
        t.json_has('revenues.1')
        t.json_is('revenues.0.transaction_id', start_id)
        t.json_has('revenues.2')
        t.json_hasnt('revenues.3')

        await t.post_ok(
            'api_integration_revenues_list',
            json={
                'from_transaction_id': start_id + 2,
                'cursor': None,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('revenues')
        t.json_has('revenues.0')
        t.json_is('revenues.0.transaction_id', start_id + 2)
        t.json_hasnt('revenues.1')

        await t.post_ok(
            'api_integration_revenues_list',
            json={
                'order_id': order.order_id,
                'cursor': None,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('revenues')
        t.json_has('revenues.0')
        t.json_is('revenues.0.order_id', order.order_id)
        t.json_hasnt('revenues.1')


async def test_list_fields(tap, dataset, api, now):
    with tap.plan(25, 'отдаем все нужные поля'):
        company = await dataset.company()
        store = await dataset.store(company=company)

        rows = []

        for _ in range(3):
            courier = await dataset.courier(store=store)
            order = await dataset.order(
                store=store, courier_id=courier.courier_id
            )
            product = await dataset.product()
            rows.append(
                {
                    'company_id': store.company_id,
                    'store_id': store.store_id,
                    'order_id': order.order_id,
                    'source': REVENUE_TLOG_SOURCES[0],
                    'transaction_id': int(now().timestamp() * 1000_000),
                    'transaction_dttm': now(),
                    'raw_data': {
                        'transaction_type': 'payment',
                        'transaction_product': 'smth',
                        'transaction_detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'product_id': product.product_id,
                        'quantity': '300',
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                        'courier_id': order.courier_id,
                    }
                }
            )

        tap.ok(await RevenueTlog.insert_batch(rows), 'вставили пачку')

        t = await api(token=company.token)

        await t.post_ok(
            'api_integration_revenues_list',
            json={'cursor': None},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_isnt('cursor', None, 'потому-что walk')
        t.json_has('revenues')
        t.json_has('revenues.0')
        t.json_has('revenues.0.company_id')
        t.json_has('revenues.0.store_id')
        t.json_has('revenues.0.order_id')
        t.json_has('revenues.0.transaction_id')
        t.json_has('revenues.0.transaction_dttm')
        t.json_has('revenues.0.transaction_type')
        t.json_has('revenues.0.transaction_product')
        t.json_has('revenues.0.transaction_detailed_product')
        t.json_has('revenues.0.product_id')
        t.json_has('revenues.0.quantity')
        t.json_has('revenues.0.amount_with_vat')
        t.json_has('revenues.0.amount_without_vat')
        t.json_has('revenues.0.vat_amount')
        t.json_has('revenues.0.vat_rate')
        t.json_has('revenues.0.aggregation_sign')
        t.json_has('revenues.0.aggregation_sign')
        t.json_has('revenues.0.courier_id')
