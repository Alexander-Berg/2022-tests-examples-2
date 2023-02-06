async def test_send_pay_shipping_contract(
        mock_procaas_create,
        procaas_extract_token,
        trucks_order_id,
        trucks_order_doc,
        send_pay_shipping_contract,
        get_event,
):
    context = get_event('pay_shipping_contract_1')['payload']['data']
    await send_pay_shipping_contract(context)

    expected_token = 'pay_shipping_contract_{}'.format(
        trucks_order_doc['contract_version'],
    )

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_trucks/')
    assert request.query == {'item_id': trucks_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'pay_shipping_contract', 'data': context}


async def test_send_trucks_order_billing_context(
        mock_procaas_create,
        procaas_extract_token,
        trucks_order_id,
        trucks_order_doc,
        send_trucks_order_billing_context,
        get_event,
):
    context = get_event('trucks_order_billing_context_1')['payload']['data']
    await send_trucks_order_billing_context(context)

    expected_token = 'trucks_order_billing_context_{}'.format(
        trucks_order_doc['contract_version'],
    )

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_trucks/')
    assert request.query == {'item_id': trucks_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {
        'kind': 'trucks_order_billing_context',
        'data': context,
    }
