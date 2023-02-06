import pytest


@pytest.mark.parametrize(
    'fail_reason', [None, {'code': '8', 'message': 'm', 'details': {}}],
)
async def test_send_update_result(
        taxi_order_fines,
        processing_create_event_handler,
        fail_reason,
        item_id='123',
        operation_id='456',
):
    result = {'operation_id': operation_id}
    if fail_reason is not None:
        result['fail_reason'] = fail_reason

    response = await taxi_order_fines.post(
        '/procaas/fines/send-update-result',
        params={'item_id': item_id},
        json=result,
    )
    assert response.status_code == 200

    assert processing_create_event_handler.times_called == 1
    request = processing_create_event_handler.next_call()['request']

    idempotency_token = result['operation_id'] + '_result'
    assert request.headers['X-Idempotency-Token'] == idempotency_token
    assert request.query['item_id'] == item_id
    assert request.json == {'kind': 'update_fine_result', 'data': result}
