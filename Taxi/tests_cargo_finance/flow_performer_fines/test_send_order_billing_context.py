import pytest


async def test_send_order_billing_context(
        mock_procaas_create,
        procaas_extract_token,
        send_order_billing_context,
        get_event,
):
    context = get_event('order_billing_context')['payload']['data']
    await send_order_billing_context(context)

    expected_token = 'flow_performer_fines_order_billing_context'

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_performer_fines/')
    assert request.query == {'item_id': 'alias_id_1'}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'order_billing_context', 'data': context}


@pytest.fixture(name='send_order_billing_context')
def _send_order_billing_context(taxi_cargo_finance, trucks_order_id):
    url = '/internal/cargo-finance/flow/performer/fines/events/order-billing-context'  # noqa: E501

    async def wrapper(order_billing_context):
        params = {'taxi_alias_id': 'alias_id_1'}
        data = {'context': order_billing_context}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper
