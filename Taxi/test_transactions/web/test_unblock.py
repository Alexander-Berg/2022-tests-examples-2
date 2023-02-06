import pytest

from test_transactions import helpers
from transactions.generated.stq3 import stq_context
from transactions.stq import events_handler


_NUM_ITEMS_OVER_LIMIT = 101


@pytest.mark.parametrize(
    'data_path',
    [
        'duplicate_invoices.json',
        'invoice_does_not_exist.json',
        'no_status_transition.json',
        'transaction_is_in_different_status.json',
        'refund_is_in_different_status.json',
        'transaction_does_not_exist.json',
        'refund_does_not_exist.json',
        'success.json',
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_unblock_check(
        patch, load_py_json, web_app_client, data_path, now,
):
    test_case = load_py_json(data_path)
    invoice_ids = invoice_ids = [
        item['invoice_id'] for item in test_case['request']['items']
    ]
    restore = helpers.patch_safe_restore_invoice(patch, None, invoice_ids)
    response = await web_app_client.post(
        '/v2/invoice/unblock/check', json=test_case['request'],
    )
    assert response.status == test_case['expected_status']
    content = await response.json()
    data = content.pop('data')
    assert data == test_case['request']
    assert content == test_case['expected_content']
    assert len(restore.calls) == test_case.get(
        'expected_num_restore_calls', len(invoice_ids),
    )


@pytest.mark.parametrize('data_path', ['success.json', 'partial_success.json'])
@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.config(
    TRANSACTIONS_UNBLOCK_FAIL_OPERATION_DATE_LIMIT='2021-09-01T14:00:00+00:00',
)
async def test_unblock_apply(
        patch,
        mockserver,
        stq3_context: stq_context.Context,
        load_py_json,
        web_app_client,
        db,
        stq,
        data_path,
        now,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    # pylint: disable=unused-variable
    def mock_experiments(request):
        assert request.json == {
            'consumer': 'transactions',
            'args': [
                {
                    'name': 'transactions_scope',
                    'type': 'string',
                    'value': 'taxi',
                },
                {
                    'name': 'external_payment_id',
                    'type': 'string',
                    'value': '10',
                },
                {'name': 'uid', 'type': 'string', 'value': '31337'},
            ],
        }
        return {
            'items': [
                {
                    'name': 'use_trust_unhold_on_full_cancel',
                    'value': {'enabled': True},
                },
            ],
        }

    @mockserver.json_handler('/trust-payments/v2/payments/10/unhold')
    # pylint: disable=unused-variable
    def mock_trust_unhold(_request):
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    test_case = load_py_json(data_path)

    invoice_ids = [
        item['invoice_id'] for item in test_case['request']['items']
    ]
    restore = helpers.patch_safe_restore_invoice(patch, None, invoice_ids)

    response = await web_app_client.post(
        '/v2/invoice/unblock', json=test_case['request'],
    )
    assert response.status == test_case['expected_status']
    content = await response.json()
    assert content == test_case['expected_content']
    assert len(restore.calls) == len(invoice_ids)
    cursor = db.orders.find(
        {'_id': {'$in': invoice_ids}},
        {
            'billing_tech.transactions.purchase_token': True,
            'billing_tech.transactions.status': True,
            'billing_tech.transactions.refunds.trust_refund_id': True,
            'billing_tech.transactions.refunds.status': True,
            'billing_tech.transactions.basket': True,
            'billing_tech.transactions.sum': True,
            'billing_tech.transactions.cleared': True,
            'billing_tech.transactions.unheld': True,
            'billing_tech.transactions.operation_should_fail': True,
            'invoice_request': True,
        },
    )
    orders = await cursor.to_list(None)
    orders.sort(key=lambda order: order['_id'])
    orders = _flatten_orders(orders)
    assert orders == test_case['expected_orders']
    assert _get_calls(stq) == test_case['expected_process_events_calls']

    if test_case['expected_orders_after_task_1']:
        invoice_ids = []
        for order in test_case['expected_orders_after_task_1']:
            with stq.flushing():
                await _run_task(stq3_context, order['id'])
                invoice_ids.append(order['id'])
        cursor = db.orders.find(
            {'_id': {'$in': invoice_ids}},
            {
                'billing_tech.transactions.purchase_token': True,
                'billing_tech.transactions.status': True,
                'billing_tech.transactions.refunds.trust_refund_id': True,
                'billing_tech.transactions.refunds.status': True,
                'billing_tech.transactions.sum': True,
                'billing_tech.transactions.cleared': True,
                'billing_tech.transactions.unheld': True,
                'billing_tech.transactions.operation_should_fail': True,
                'invoice_request': True,
            },
        )
        orders = await cursor.to_list(None)
        orders.sort(key=lambda order: order['_id'])
        orders = _flatten_orders(orders)
        assert orders == test_case['expected_orders_after_task_1']
    if test_case['expected_orders_after_task_2']:
        invoice_ids = []
        for order in test_case['expected_orders_after_task_2']:
            with stq.flushing():
                await _run_task(stq3_context, order['id'])
                invoice_ids.append(order['id'])
        cursor = db.orders.find(
            {'_id': {'$in': invoice_ids}},
            {
                'billing_tech.transactions.purchase_token': True,
                'billing_tech.transactions.status': True,
                'billing_tech.transactions.refunds.trust_refund_id': True,
                'billing_tech.transactions.refunds.status': True,
                'billing_tech.transactions.sum': True,
                'billing_tech.transactions.cleared': True,
                'billing_tech.transactions.unheld': True,
                'billing_tech.transactions.operation_should_fail': True,
                'invoice_request': True,
            },
        )
        orders = await cursor.to_list(None)
        orders.sort(key=lambda order: order['_id'])
        orders = _flatten_orders(orders)
        assert orders == test_case['expected_orders_after_task_2']


@pytest.mark.now('2020-01-01T00:00:00')
async def test_unblock_check_over_limit(web_app_client, now):
    items = [
        {
            'invoice_id': str(i),
            'transaction_type': 'payment',
            'transaction_id': str(i),
            'current_status': 'clear_pending',
            'new_status': 'clear_fail',
        }
        for i in range(_NUM_ITEMS_OVER_LIMIT)
    ]
    body = {'items': items}
    response = await web_app_client.post(
        '/v2/invoice/unblock/check', json=body,
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'message': 'Too many items, got 101 > 100',
        'code': 'too_many_items',
        'data': body,
        'details': '{\"errors\": []}',
    }


def _get_calls(stq):
    calls = []
    while stq.transactions_events.has_calls:
        call = stq.transactions_events.next_call()
        calls.append({'id': call['id']})
    return calls


async def _run_task(stq3_context, invoice_id, queue='transactions_events'):
    await events_handler.task(
        stq3_context,
        helpers.create_task_info(queue=queue),
        invoice_id,
        log_extra=None,
    )


def _flatten_orders(orders):
    result = []
    for order in orders:
        flat_order = {
            'id': order['_id'],
            'transactions': order['billing_tech']['transactions'],
        }
        invoice_request = order.get('invoice_request', {})
        if 'is_processing_halted' in invoice_request:
            flat_order['is_processing_halted'] = invoice_request[
                'is_processing_halted'
            ]
        if 'operations' in invoice_request:
            flat_order['operations'] = invoice_request['operations']
        result.append(flat_order)
    return result
