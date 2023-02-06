import pytest


async def test_call_rebill_order(
        mockserver, taxi_order_fines, order_proc, iso8601, operation_id='123',
):
    @mockserver.json_handler('billing-orders/v1/rebill_order')
    def handler(request):
        return {'doc': {'id': 5258550208}}

    response = await taxi_order_fines.post(
        '/procaas/call-rebill-order',
        params={'item_id': order_proc['_id']},
        json={'operation_id': operation_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert handler.times_called == 1
    assert handler.next_call()['request'].json == {
        'idempotency_token': operation_id,
        'reason': {'kind': 'fine_decision_modified', 'data': {}},
        'order': {
            'id': order_proc['_id'],
            'alias_id': order_proc['candidates'][-1]['alias_id'],
            'version': order_proc['lookup']['version'],
            'zone_name': order_proc['order']['nz'],
            'due': iso8601(order_proc['order']['request']['due']),
        },
    }


async def test_call_rebill_order_fail(
        mockserver,
        taxi_order_fines,
        order_proc,
        operation_id='123',
        message='some message from billing',
):
    @mockserver.json_handler('billing-orders/v1/rebill_order')
    def _handler(request):
        data = {'code': 'rebill_order_is_not_allowed', 'message': message}
        return mockserver.make_response(status=400, json=data)

    response = await taxi_order_fines.post(
        '/procaas/call-rebill-order',
        params={'item_id': order_proc['_id']},
        json={'operation_id': operation_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'fail_reason': {
            'code': 'billing_reject',
            'message': 'billing rejected operation',
            'details': {'billing_response': {'message': message}},
        },
    }


async def test_call_rebill_order_error(
        mockserver, taxi_order_fines, order_proc, operation_id='123',
):
    @mockserver.json_handler('billing-orders/v1/rebill_order')
    def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_order_fines.post(
        '/procaas/call-rebill-order',
        params={'item_id': order_proc['_id']},
        json={'operation_id': operation_id},
    )
    assert response.status_code == 500


@pytest.fixture(name='iso8601')
def _iso8601():
    def _wrapper(dt_stamp):
        return dt_stamp.strftime('%Y-%m-%dT%H:%M:%S+00:00')

    return _wrapper
