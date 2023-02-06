async def test_send_taxi_order_billing_context(
        mock_procaas_create,
        procaas_extract_token,
        taxi_order_id,
        send_taxi_order_billing_context,
        get_event,
        claim_id,
):
    context = get_event('taxi_order_billing_context')['payload']['data']
    await send_taxi_order_billing_context(context)

    expected_token = 'taxi_order_billing_context/{}'.format(taxi_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_claims/')
    assert request.query == {'item_id': claim_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {
        'kind': 'taxi_order_billing_context',
        'data': context,
    }
