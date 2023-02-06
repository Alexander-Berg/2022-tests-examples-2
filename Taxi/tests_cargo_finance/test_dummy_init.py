import pytest


async def test_send_dummy_init(
        mock_procaas_create, procaas_extract_token, send_dummy_init,
):
    flow = 'claims'
    entity_id = 'claim_id_123'
    await send_dummy_init(flow, entity_id)

    expected_token = 'dummy_init/{}/{}'.format(flow, entity_id)
    expected_payload = {'kind': 'dummy_init', 'data': {}}
    assert mock_procaas_create.times_called == 4
    for expected_queue, expected_item_id in [
            ('finance_flow_claims', entity_id),
            ('finance_flow_claims_payments', entity_id),
            ('finance_pay_order', '{}/{}'.format(flow, entity_id)),
            ('finance_flow_claims_payments', entity_id),
    ]:
        request = mock_procaas_create.next_call()['request']
        assert request.path.count('/cargo/{}/'.format(expected_queue))
        assert request.query == {'item_id': expected_item_id}
        assert procaas_extract_token(request) == expected_token
        assert request.json == expected_payload


@pytest.fixture(name='send_dummy_init')
def _send_dummy_init(taxi_cargo_finance):
    url = '/internal/cargo-finance/events/dummy-init'

    async def wrapper(flow, entity_id):
        params = {'flow': flow, 'entity_id': entity_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200

    return wrapper
