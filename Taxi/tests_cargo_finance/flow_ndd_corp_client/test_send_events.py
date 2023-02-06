async def test_send_order_finalization_started(
        mock_procaas_create,
        procaas_extract_token,
        ndd_order_id,
        send_order_finalization_started,
):
    await send_order_finalization_started()

    expected_token = 'order_finalization_started/{}'.format(ndd_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_ndd_corp_client/')
    assert request.query == {'item_id': ndd_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'order_finalization_started', 'data': {}}


async def test_send_order_billing_context_delivery_client_b2b_logistics_payment(  # noqa: E501
        mock_procaas_create,
        procaas_extract_token,
        ndd_order_id,
        send_order_billing_context,
        get_event,
):
    context = get_event(
        'order_billing_context_delivery_client_b2b_logistics_payment',
    )['payload']['data']
    await send_order_billing_context(context)

    expected_token = (
        'order_billing_context_delivery_client_b2b_logistics_payment/{}'.format(  # noqa: E501
            ndd_order_id,
        )
    )

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_ndd_corp_client/')
    assert request.query == {'item_id': ndd_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {
        'kind': 'order_billing_context_delivery_client_b2b_logistics_payment',
        'data': context,
    }
