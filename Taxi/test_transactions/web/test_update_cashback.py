import pytest

from test_transactions import helpers


@pytest.mark.parametrize(
    'data_path',
    [
        # http 404
        'not-found.json',
        # http 404
        pytest.param(
            'not-found.json',
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_ARCHIVE_ENABLED={'__default__': 1},
                ),
            ],
            id='it should return 404 when invoice was not found anywhere',
        ),
        # Operation not planned and not created, http 409
        'version-conflict.json',
        # Operation not planned and not created, b2b, http 409
        'version-conflict-b2b.json',
        # Operation planned but not created, http 200
        'same-operation-id.json',
        # Operation planned and created, http 200
        'new-operation.json',
        # Operation planned and created, restored from archive, http 200
        pytest.param(
            'new-operation-archive.json',
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_ARCHIVE_ENABLED={'__default__': 1},
                ),
            ],
            id='it should restore invoice from archive when enabled by config',
        ),
        # Operation planned and created, b2b, http 200
        'new-operation-b2b.json',
        # Operation not planned and not created, http 400
        'negative-reward.json',
        # Operation not planned and not created, http 400
        'sources-missing-source.json',
        # Operation planned and created, http 200
        'sources-missing-payload.json',
        # Operation planned and created, http 200
        'sources-arbitrary-source.json',
        # Operation planned and created, http 200
        'sources-arbitrary-source-fiscal.json',
        # Operation not planned and not created, http 400
        'sources-no-product-id-provided.json',
        # Operation planned and created, http 200
        'sources-no-product-id-provided-for-zero-source.json',
    ],
)
@pytest.mark.config(
    TRANSACTIONS_TOPUP_PRODUCTS=[
        {
            'billing_service': 'card',
            'product_id': 'user-product-id',
            'source': 'user',
        },
    ],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_update_cashback(
        patch, load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    helpers.patch_fetch_invoice(
        patch,
        result=data.get('fetch_invoice_result'),
        expected_invoice_id=data['request']['invoice_id'],
    )
    response = await web_app_client.post(
        '/v2/cashback/update', json=data['request'],
    )
    assert response.status == data['expected_status']
    assert stq.transactions_cashback_events.times_called == 0
    calls = _get_plan_operation_calls(stq.transactions_plan_operation)
    assert calls == data['expected_calls']
    if data['expected_status'] != 404:
        order = await db.orders.find_one(data['request']['invoice_id'])
        request = order.get('invoice_request', {})
        cashback_operations = request.get('cashback_operations', [])
        assert cashback_operations == data['expected_operations']
        cashback_version = request.get('cashback_version', 1)
        assert cashback_version == data['expected_cashback_version']
        if data['expected_status'] != 200:
            expected_error_message = data.get('expected_error_message')
            if expected_error_message is not None:
                response_body = await response.json()
                assert response_body['message'] == expected_error_message
    else:
        assert not data['expected_operations']


def _get_plan_operation_calls(queue):
    calls = []
    while queue.has_calls:
        call = queue.next_call()
        calls.append(
            {
                'id': call['id'],
                'args': call['args'],
                'kwargs': {
                    k: v
                    for k, v in call['kwargs'].items()
                    if k not in ['log_extra', 'created']
                },
                'eta': call['eta'],
            },
        )
    return calls
