import copy

from aiohttp import web
import pytest

DEFAULT_RESPONSE_DATA = {
    'invoice': {
        'id': 'my-order',
        'invoice_due': '2019-05-01T06:00:00+03:00',
        'currency': 'RUB',
        'status': 'cleared',
        'payment_type': 'card',
        'sum_to_pay': {},
        'held': {},
        'cleared': {},
        'debt': {},
        'operation_info': {
            'originator': 'processing',
            'priority': 0,
            'version': 1,
        },
        'transactions': [
            {
                'created': '2019-09-01T18:00:00+03:00',
                'initial_sum': {},
                'payment_method_id': 'card-x8b7bb229fa9eb2a1d692b878',
                'payment_type': 'card',
                'refunds': [
                    {
                        'created': '2019-09-01T18:00:00+03:00',
                        'status': 'refund_success',
                        'sum': {'ride': '10', 'tips': '0'},
                        'updated': '2019-09-01T18:00:00+03:00',
                        'refunded': '2019-09-01T18:00:00+03:00',
                    },
                ],
                'status': 'clear_success',
                'sum': {},
                'updated': '2019-09-01T18:00:00+03:00',
                'wait_for_cvn': False,
                'external_payment_id': 'xxx',
                'terminal_id': '42',
            },
        ],
    },
}

DEFAULT_RESPONSE_DATA_WITH_FAIL_REASON = copy.deepcopy(DEFAULT_RESPONSE_DATA)
DEFAULT_RESPONSE_DATA_WITH_FAIL_REASON['invoice'].update(
    {'fail_reason': {'code': 'not_enough_funds'}},
)

OPERATIONS = {
    'operations': [
        {'id': 'id1', 'status': 'done', 'sum_to_pay': []},
        {'id': 'id2', 'status': 'failed', 'sum_to_pay': []},
    ],
}

RESPONSE_DATA_WITH_OPERATIONS = copy.deepcopy(DEFAULT_RESPONSE_DATA)
RESPONSE_DATA_WITH_OPERATIONS['invoice'].update(
    {
        'operations': [
            {'id': 'id1', 'status': 'done', 'sum_to_pay': {}},
            {'id': 'id2', 'status': 'failed', 'sum_to_pay': {}},
        ],
    },
)


VALIDATION_ERROR_RESPONSE = {
    'code': 'no-order-id',
    'message': (
        'Either order_id or a pair of (external_ref, service) has to '
        'be provided'
    ),
}


MULTIPLE_PAYMENT_TYPES_ERROR_RESPONSE = {
    'code': 'multiple-payment-types',
    'message': (
        'Response from `transactions` contains multiple payment types'
        ' that cannot be represented in current API'
    ),
}


@pytest.mark.parametrize(
    [
        'request_data',
        'status_code',
        'response_data',
        'transactions_eda_times_called',
        'extra_invoice_fields',
    ],
    [
        pytest.param(
            {'order_id': 'my-order'},
            200,
            DEFAULT_RESPONSE_DATA,
            1,
            {},
            id='request with order_id',
        ),
        pytest.param(
            {'order_id': 'my-order'},
            200,
            DEFAULT_RESPONSE_DATA_WITH_FAIL_REASON,
            1,
            {'fail_reason': {'code': 'not_enough_funds'}},
            id='request with order_id with fail_reason',
        ),
        pytest.param(
            {'external_ref': 'my-order', 'service': 'eats'},
            200,
            DEFAULT_RESPONSE_DATA,
            1,
            {},
            id='request with (external_ref and service)',
        ),
        pytest.param(
            {'order_id': 'my-order'},
            200,
            RESPONSE_DATA_WITH_OPERATIONS,
            1,
            OPERATIONS,
            id='invoice with operations',
        ),
        pytest.param(
            {
                'external_ref': 'my-order',
                'service': 'eats',
                'order_id': 'my-order',
            },
            400,
            VALIDATION_ERROR_RESPONSE,
            0,
            {},
            id='request with both order_id and (external_ref and service)',
        ),
        pytest.param(
            {},
            400,
            VALIDATION_ERROR_RESPONSE,
            0,
            {},
            id='request with neither order_id nor (external_ref and service)',
        ),
        pytest.param(
            {'order_id': 'my-order'},
            500,
            MULTIPLE_PAYMENT_TYPES_ERROR_RESPONSE,
            1,
            {
                'debt': [
                    {
                        'items': [{'amount': '123.00', 'item_id': 'ride'}],
                        'payment_type': 'card',
                    },
                    {
                        'items': [{'amount': '20.00', 'item_id': 'ride'}],
                        'payment_type': 'personal_wallet',
                    },
                ],
                'payment_types': ['card', 'personal_wallet'],
            },
            id='multiple payment types error',
        ),
    ],
)
async def test_get_order_info(
        web_app_client,
        mockserver,
        load_json,
        request_data,
        status_code,
        response_data,
        transactions_eda_times_called,
        extra_invoice_fields,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def handler(request):  # pylint: disable=unused-variable
        return {
            **load_json('transactions_eda_invoice_retrieve.json'),
            **extra_invoice_fields,
        }

    resp = await web_app_client.post('/v1/orders/retrieve', json=request_data)

    assert resp.status == status_code
    assert await resp.json() == response_data
    assert handler.times_called == transactions_eda_times_called


@pytest.mark.parametrize(
    'originator', ['admin', 'antifraud', 'processing', 'eats_payments'],
)
async def test_originator(web_app_client, mockserver, load_json, originator):
    operation_info = {'originator': originator, 'priority': 0, 'version': 1}

    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def handler(request):  # pylint: disable=unused-variable
        return {
            **load_json('transactions_eda_invoice_retrieve.json'),
            'operation_info': operation_info,
        }

    resp = await web_app_client.post(
        '/v1/orders/retrieve', json={'order_id': 'my-order'},
    )

    assert resp.status == 200
    response_data = copy.deepcopy(DEFAULT_RESPONSE_DATA)
    response_data['invoice']['operation_info'] = operation_info
    assert await resp.json() == response_data


@pytest.mark.parametrize(
    ['extra_invoice_fields', 'extra_response_data'],
    [
        pytest.param(
            {
                'sum_to_pay': [
                    {
                        'items': [{'amount': '123.00', 'item_id': 'ride'}],
                        'payment_type': 'card',
                    },
                ],
            },
            {'sum_to_pay': {'ride': '123.00'}},
            id='request with aggregated `sum_to_pay`',
        ),
        pytest.param(
            {
                'held': [
                    {
                        'items': [{'amount': '123.00', 'item_id': 'ride'}],
                        'payment_type': 'card',
                    },
                ],
            },
            {'held': {'ride': '123.00'}},
            id='request with aggregated `held`',
        ),
        pytest.param(
            {
                'cleared': [
                    {
                        'items': [{'amount': '123.00', 'item_id': 'ride'}],
                        'payment_type': 'card',
                    },
                ],
            },
            {'cleared': {'ride': '123.00'}},
            id='request with aggregated `cleared`',
        ),
        pytest.param(
            {
                'debt': [
                    {
                        'items': [{'amount': '123.00', 'item_id': 'ride'}],
                        'payment_type': 'card',
                    },
                ],
            },
            {'debt': {'ride': '123.00'}},
            id='request with aggregated `debt`',
        ),
        pytest.param(
            {
                'operations': [
                    {
                        'id': 'id',
                        'status': 'done',
                        'sum_to_pay': [
                            {
                                'items': [
                                    {'amount': '123.00', 'item_id': 'ride'},
                                ],
                                'payment_type': 'card',
                            },
                        ],
                    },
                ],
            },
            {
                'operations': [
                    {
                        'id': 'id',
                        'status': 'done',
                        'sum_to_pay': {'ride': '123.00'},
                    },
                ],
            },
            id='request with aggregated `operations[*].sum_to_pay`',
        ),
        pytest.param(
            {
                'transactions': [
                    {
                        'created': '2019-09-01T18:00:00+03:00',
                        'external_payment_id': 'xxx',
                        'initial_sum': [
                            {'amount': '150.00', 'item_id': 'ride'},
                        ],
                        'payment_method_id': 'card-x8b7bb229fa9eb2a1d692b878',
                        'payment_type': 'card',
                        'refunds': [
                            {
                                'created': '2019-09-01T18:00:00+03:00',
                                'status': 'refund_success',
                                'sum': [
                                    {'amount': '10', 'item_id': 'ride'},
                                    {'amount': '0', 'item_id': 'tips'},
                                ],
                                'updated': '2019-09-01T18:00:00+03:00',
                            },
                        ],
                        'status': 'hold_success',
                        'sum': [{'amount': '123.00', 'item_id': 'ride'}],
                        'updated': '2019-09-01T18:00:00+03:00',
                        'wait_for_cvn': False,
                    },
                ],
            },
            {
                'transactions': [
                    {
                        'created': '2019-09-01T18:00:00+03:00',
                        'initial_sum': {'ride': '150.00'},
                        'payment_method_id': 'card-x8b7bb229fa9eb2a1d692b878',
                        'payment_type': 'card',
                        'refunds': [
                            {
                                'created': '2019-09-01T18:00:00+03:00',
                                'status': 'refund_success',
                                'sum': {'ride': '10', 'tips': '0'},
                                'updated': '2019-09-01T18:00:00+03:00',
                            },
                        ],
                        'status': 'hold_success',
                        'sum': {'ride': '123.00'},
                        'updated': '2019-09-01T18:00:00+03:00',
                        'wait_for_cvn': False,
                        'external_payment_id': 'xxx',
                    },
                ],
            },
            id='request with aggregated transactions[*].sum, '
            'transactions[*].initial_sum '
            'and transactions[*].refunds[*].sum',
        ),
    ],
)
async def test_get_order_info_aggregation(
        web_app_client,
        mockserver,
        load_json,
        extra_invoice_fields,
        extra_response_data,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def handler(request):  # pylint: disable=unused-variable
        return {
            **load_json('transactions_eda_invoice_retrieve.json'),
            **extra_invoice_fields,
        }

    resp = await web_app_client.post(
        '/v1/orders/retrieve', json={'order_id': 'my-order'},
    )

    assert resp.status == 200
    response_data = copy.deepcopy(DEFAULT_RESPONSE_DATA)
    response_data['invoice'] = {
        **response_data['invoice'],
        **extra_response_data,
    }
    assert await resp.json() == response_data
    assert handler.times_called == 1


async def test_get_order_transactions_error(web_app_client, mockserver):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def handler(request):  # pylint: disable=unused-variable
        return web.Response(
            status=404, body='{"code": "not-found", "message": "not found"}',
        )

    resp = await web_app_client.post(
        '/v1/orders/retrieve', json={'order_id': 'my-order'},
    )

    assert resp.status == 404
    assert await resp.json() == {
        'code': 'not-found',
        'message': f'order_id: my-order not found',
    }


async def test_get_rosneft_invoice(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def handler(request):
        return {**load_json('rosneft_invoice.json')}

    resp = await web_app_client.post(
        '/v1/orders/retrieve', json={'order_id': '200814-125127'},
    )

    assert resp.status == 200
    assert handler.times_called == 1
