# pylint: disable=unused-variable
from aiohttp import web
import pytest


@pytest.mark.parametrize(
    'data_path',
    [
        'payments_details_basic.json',
        'payments_details_basic_without_order_number.json',
        'payments_details_empty.json',
        'payments_details_cursor.json',
        'payments_details_cursor_empty.json',
        'payments_details_with_billing_id_no_batch_payments.json',
        'payments_details_with_billing_id.json',
    ],
)
@pytest.mark.servicetest
async def test_park_payments_details(
        web_app_client,
        load_json,
        data_path,
        request_headers,
        mockserver,
        patch,
):
    data = load_json(data_path)

    @patch(
        'billing_bank_orders.generated.service.ydb_client.plugin.'
        'YdbClient.execute',
    )
    async def execute(*args, **kwargs):
        if not data['empty_ydb_response']:
            return [
                {
                    'transaction_id': '77788899915',
                    'payment_id': 123456,
                    'alias_id': '5646546546dsf4s6d54f65sd4f654f6s5d4',
                    'agreement_id': 'Test Agreement #555',
                    'driver_id': '$Wj43oi5ji4j53o4ij5oi34j5oij4543kpo',
                    'park_id': '43543k5oo43pk543pok532k423j4oi23j4',
                    'orig_amount': '125.0000',
                    'credited_amount': '125.0000',
                    'currency': 'RUB',
                    'product': 'park_b2b_trip_payment',
                    'detailed_product': 'park_b2b_trip_payment',
                    'source': 'tlog',
                    'event_time': '2020-04-27T13:13:13.0+03:00',
                    'transaction_time': '2020-04-27T13:13:13.0+03:00',
                    'invoice_time': '2020-04-27T13:13:13.0+03:00',
                },
            ]
        return []

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _docs_select(request):
        return mockserver.make_response(json=data['reports_response'])

    response = await web_app_client.post(
        '/v1/parks/payments/details',
        headers=request_headers,
        json=data['request'],
    )
    assert response.status == data['response_status']
    content = await response.json()
    assert content == data['response']


@pytest.mark.parametrize(
    'request_body',
    [
        # Wrong request body
        None,
        # Empty request body
        {},
        # no clid
        {'payment_id': '0123456', 'limit': 10},
        # no limit
        {'payment_id': '0123456', 'clid': '01234567'},
        # bad limit
        {'payment_id': '0123456', 'clid': '01234567', 'limit': 0},
        # bad cursor
        {
            'payment_id': '0123456',
            'clid': '01234567',
            'cursor': {},
            'limit': 10,
        },
    ],
)
@pytest.mark.servicetest
async def test_park_payments_details_bad_requests(
        web_app_client, request_headers, request_body,
):
    response = await web_app_client.post(
        '/v1/parks/payments/details',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPBadRequest.status_code


@pytest.mark.servicetest
async def test_park_payments_details_auth_payment(
        web_app_client, request_headers, mockserver, patch,
):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _docs_select(request):
        if request.json['cursor'] == {}:
            return mockserver.make_response(
                json={
                    'docs': [
                        {
                            'data': {
                                'amount': '1335.88',
                                'currency': 'RUB',
                                'bank_account_number': 'SOME_BANK_ACCOUNT_0',
                                'created': '2020-01-16T03:43:00.000000+00:00',
                                'payment_target': 'Оплата',
                                'payment_id': '69113930',
                                'payee_name': 'ФИО_0',
                                'bank_name': 'ПАО СУПЕР-БАНК 0',
                                'payment_date': (
                                    '2020-01-15T21:00:00.000000+00:00'
                                ),
                                'details': {
                                    'payment_order_number': '250132',
                                    'payment_status': 'CONFIRMED',
                                    'updated': (
                                        '2020-01-17T11:22:10.000000+00:00'
                                    ),
                                    'void_reason': None,
                                    'history_id': 100774,
                                    'void_date': (
                                        '2020-01-17T11:22:08.000000+00:00'
                                    ),
                                },
                            },
                            'doc_id': 3344556677,
                            'event_at': '2020-01-16T03:43:00.000000+00:00',
                            'created': '2020-01-16T03:50:00.000000+00:00',
                            'process_at': '2020-01-16T03:51:00.000000+00:00',
                            'tags': [],
                            'external_event_ref': '69113930',
                            'external_obj_id': (
                                'v1/billing_bank_orders_payment/clid/01234567'
                            ),
                            'journal_entries': [],
                            'kind': 'billing_bank_orders_payment',
                            'service': 'billing-bank-orders',
                            'status': 'complete',
                        },
                    ],
                    'cursor': {
                        '2020-01-18T03:43:00.000000+00:00': '3344556678',
                    },
                },
            )
        return mockserver.make_response(
            json={'docs': [], 'cursor': request.json['cursor']},
        )

    @patch(
        'billing_bank_orders.generated.service.ydb_client.plugin.'
        'YdbClient.execute',
    )
    async def execute(*args, **kwargs):
        return []

    request_body = {'payment_id': '0123456', 'clid': '01234567', 'limit': 10}
    response = await web_app_client.post(
        '/v1/parks/payments/details',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPNotFound.status_code

    request_body = {'payment_id': '69113930', 'clid': '01234567', 'limit': 10}
    response = await web_app_client.post(
        '/v1/parks/payments/details',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPOk.status_code


@pytest.mark.parametrize('data_path', ['payments_details_with_null.json'])
@pytest.mark.now('2020-02-10T12:00:00')
@pytest.mark.servicetest
async def test_park_payments_details_nullable(
        web_app_client,
        load_json,
        data_path,
        request_headers,
        mockserver,
        patch,
):
    data = load_json(data_path)

    @patch(
        'billing_bank_orders.generated.service.ydb_client.plugin.'
        'YdbClient.execute',
    )
    async def execute(*args, **kwargs):
        return [
            {
                'transaction_id': '77788899915',
                'payment_id': 123456,
                'alias_id': None,
                'agreement_id': 'Test Agreement #555',
                'driver_id': None,
                'park_id': None,
                'orig_amount': '125.0000',
                'credited_amount': '125.0000',
                'currency': 'RUB',
                'product': 'park_b2b_trip_payment',
                'detailed_product': None,
                'source': 'tlog',
                'event_time': None,
                'transaction_time': '2020-04-27T10:13:13Z',
                'invoice_time': None,
            },
        ]

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _docs_select(request):
        return mockserver.make_response(json=data['reports_response'])

    response = await web_app_client.post(
        '/v1/parks/payments/details',
        headers=request_headers,
        json=data['request'],
    )
    assert response.status == data['response_status']
    content = await response.json()
    assert content == data['response']
