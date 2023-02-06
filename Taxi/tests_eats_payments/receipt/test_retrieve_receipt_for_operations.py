import json

import pytest

from tests_eats_payments import db_order
from tests_eats_payments import helpers

ORDER_ID = 'test_order'
OPERATION_ID = 'create:100500'
REFUND_OPERATION_ID = 'refund:13022-1234'
PERSONAL_WALLET_TYPE = 'personal_wallet'


NOW = '2020-03-31T07:20:00+00:00'


def make_order(order_nr='test_order'):
    return {
        'country_code': 'RU',
        'order_nr': order_nr,
        'payment_method': 'card',
    }


def make_user_info():
    return {'personal_email_id': 'mail_id', 'personal_phone_id': 'phone_id'}


@pytest.fixture(name='mock_customer_service_retrieve')
def _mock_customer_service_retrieve(mockserver, load_json):
    def _inner():
        @mockserver.json_handler(
            '/eats-core-order-revision/internal-api/v1'
            '/order-revision/customer-services/details',
        )
        @mockserver.json_handler(
            '/eats-order-revision/v1'
            '/order-revision/customer-services/details',
        )
        def _transactions_invoice_retrieve(request):
            revision_id = ''
            if 'revision_id' in request.json:
                revision_id = request.json['revision_id']
            if 'origin_revision_id' in request.json:
                revision_id = request.json['origin_revision_id']
            revision_file = 'revision_' + revision_id + '.json'
            return mockserver.make_response(
                json.dumps(load_json(revision_file)), 200,
            )

    return _inner


def make_eats_payments_receipts_operations_switch_experiment(  # noqa: E501 pylint: disable=invalid-name,line-too-long
        enabled,
) -> dict:
    return {
        'name': 'eats_payments_receipts_operations_switch',
        'consumers': ['eats-payments/receipts_operations_switch'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    }


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    [['transaction_client_response.json', 'test_order']],
    indirect=True,
)
@pytest.mark.parametrize(
    'receipt_response, response_code, document_id, plus_map',
    [
        pytest.param(
            '',
            400,
            'test_order:abracadabra::1',
            {},
            id='400 for unprovided product type',
        ),
        pytest.param(
            '',
            500,
            'test_order:products::1',
            {},
            id='500 for create operation',
        ),
        pytest.param(
            '',
            500,
            'test_order:products::2',
            {},
            id='500 for update before close operation',
        ),
        pytest.param(
            'receipt_close_products.json',
            200,
            'test_order:products::3',
            {},
            id='products receipt for close operation',
        ),
        pytest.param(
            'receipt_close_products_with_plus.json',
            200,
            'test_order:products::3',
            {'close': {'pizza': 5}},
            id='products receipt for close operation with plus',
        ),
        pytest.param(
            'receipt_close_delivery.json',
            200,
            'test_order:delivery::3',
            {},
            id='delivery receipt for close operation',
        ),
        pytest.param(
            'receipt_update_tips.json',
            200,
            'test_order:tips::4',
            {},
            id='tips receipt for update operation',
        ),
        pytest.param(
            'receipt_update_tips_with_plus.json',
            200,
            'test_order:tips::4',
            {'update2': {'tips-1': 9}},
            id='delivery receipt for close operation with plus',
        ),
        pytest.param(
            '',
            404,
            'test_order:products::4',
            {},
            id='404 for receipt without items',
        ),
        pytest.param(
            'receipt_refund_tips.json',
            200,
            'test_order:tips:refund:5',
            {},
            id='tips refund receipt for refund operation',
        ),
        pytest.param(
            'receipt_refund_products.json',
            200,
            'test_order:products:refund:6',
            {},
            id='products refund receipt for refund operation',
        ),
        pytest.param(
            'receipt_refund_products_with_plus.json',
            200,
            'test_order:products:refund:6',
            {'refund1': {'pizza': 5}, 'refund2': {'pizza': 4}},
            id='products refund receipt for refund operation with plus',
        ),
        pytest.param(
            'receipt_refund_service_fee.json',
            200,
            'test_order:service_fee:refund:6',
            {},
            id='service_fee refund receipt for refund operation',
        ),
        pytest.param(
            '',
            404,
            'test_order:tips:refund:6',
            {},
            id='404 fro tips in other refund operation',
        ),
    ],
)
async def test_handle_retrieve_all_receipts(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        mock_customer_service_retrieve,
        insert_operations,
        upsert_items_payment,
        load_json,
        receipt_response,
        response_code,
        document_id,
        plus_map,
):
    mock_transactions_invoice_retrieve(
        file_to_load='transaction_client_response.json',
    )
    mock_customer_service_retrieve()
    insert_operations(1, ORDER_ID, 'create', 'create', 'create')
    insert_operations(2, ORDER_ID, 'update1', 'create', 'update')
    insert_operations(3, ORDER_ID, 'close', 'update1', 'close')
    insert_operations(4, ORDER_ID, 'update2', 'close', 'update')
    insert_operations(5, ORDER_ID, 'refund1', 'update2', 'refund')
    insert_operations(6, ORDER_ID, 'refund2', 'refund1', 'refund')

    for revision_id in plus_map:
        for item_id in plus_map[revision_id]:
            upsert_items_payment(
                item_id,
                ORDER_ID,
                'trust',
                plus_map[revision_id][item_id],
                revision_id,
            )

    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': document_id},
    )
    assert response.status_code == response_code
    if response_code == 200:
        assert response.json() == load_json(receipt_response)


@pytest.mark.now(NOW)
async def test_send_purchase_stq(
        mock_transactions_invoice_retrieve,
        mock_customer_service_retrieve,
        check_transactions_callback_task,
        insert_operations,
        experiments3,
        pgsql,
        stq,
):
    mock_customer_service_retrieve()
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id=ORDER_ID,
        currency='RUB',
        service='eats',
        api_version=2,
    )
    order.upsert()
    mock_transactions_invoice_retrieve(
        file_to_load='transaction_client_response.json',
    )
    insert_operations(
        3, ORDER_ID, 'update1', 'update1', 'close', status='in_progress',
    )
    experiments3.add_config(
        **make_eats_payments_receipts_operations_switch_experiment(True),
    )

    await check_transactions_callback_task(
        operation_id='create:update1',
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    assert stq.eats_payments_send_receipt.times_called == 0
    assert stq.eats_send_receipts_requests.times_called == 3
    next_call = stq.eats_send_receipts_requests.next_call()
    assert next_call['kwargs']['document_id'] == 'test_order:products::3'
    next_call = stq.eats_send_receipts_requests.next_call()
    assert next_call['kwargs']['document_id'] == 'test_order:delivery::3'
    next_call = stq.eats_send_receipts_requests.next_call()
    assert next_call['kwargs']['document_id'] == 'test_order:service_fee::3'
