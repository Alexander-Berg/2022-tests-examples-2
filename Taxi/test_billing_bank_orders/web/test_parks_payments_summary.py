# pylint: disable=unused-variable
from aiohttp import web
import pytest


@pytest.mark.parametrize(
    'data_path',
    [
        'payments_summary.json',
        'payments_summary_empty.json',
        'payments_summary_with_billing_id_no_batch_payments.json',
        'payments_summary_with_billing_id.json',
    ],
)
@pytest.mark.servicetest
async def test_park_payments_summary(
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
        assert kwargs['params'] == data['expected_ydb_params']
        return data['ydb_response']

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _docs_select(request):
        return mockserver.make_response(json=data['reports_response'])

    response = await web_app_client.post(
        '/v1/parks/payments/summary',
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
        {'payment_id': '0123456'},
        # no payment_id
        {'clid': '01234567'},
    ],
)
@pytest.mark.servicetest
async def test_park_payments_summary_bad_requests(
        web_app_client, request_headers, request_body,
):
    response = await web_app_client.post(
        '/v1/parks/payments/summary',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPBadRequest.status_code


@pytest.mark.servicetest
async def test_park_payments_summary_auth_payment(
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

    request_body = {'payment_id': '0123456', 'clid': '01234567'}
    response = await web_app_client.post(
        '/v1/parks/payments/summary',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPNotFound.status_code

    request_body = {'payment_id': '69113930', 'clid': '01234567'}
    response = await web_app_client.post(
        '/v1/parks/payments/summary',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPOk.status_code
