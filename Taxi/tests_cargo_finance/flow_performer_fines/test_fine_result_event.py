import pytest


@pytest.mark.parametrize(
    'fail_reason', [None, {'code': '8', 'message': 'm', 'details': {}}],
)
async def test_send_update_result(
        taxi_cargo_finance,
        fail_reason,
        mock_procaas_create,
        item_id='123',
        operation_id='456',
):
    result = {'operation_id': operation_id}
    if fail_reason is not None:
        result['fail_reason'] = fail_reason

    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/flow/performer/fines/func/update-fine-result',
        params={'taxi_alias_id': item_id},
        json=result,
    )
    assert response.status_code == 200

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']

    idempotency_token = result['operation_id'] + '_result'
    assert request.headers['X-Idempotency-Token'] == idempotency_token
    assert request.query['item_id'] == item_id
    assert request.json == {'kind': 'update_fine_result', 'data': result}
