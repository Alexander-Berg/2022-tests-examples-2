async def test_send_agent_ref(
        mock_procaas_create,
        procaas_extract_token,
        taxi_order_id,
        send_agent_ref,
        get_event,
):
    await send_agent_ref()

    expected_token = 'agent_ref/{}'.format(taxi_order_id)
    context = get_event('agent_ref')['payload']['data']

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_taxi_park/')
    assert request.query == {'item_id': taxi_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'agent_ref', 'data': context}


async def test_send_taxi_order_finished(
        mock_procaas_create,
        procaas_extract_token,
        taxi_order_id,
        send_taxi_order_finished,
):
    await send_taxi_order_finished()

    expected_token = 'taxi_order_finished/{}'.format(taxi_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_taxi_park/')
    assert request.query == {'item_id': taxi_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'taxi_order_finished', 'data': {}}


async def test_send_taxi_order_context(
        mock_procaas_create,
        procaas_extract_token,
        taxi_order_id,
        send_taxi_order_context,
        get_event,
):
    context = get_event('taxi_order_context')['payload']['data']
    await send_taxi_order_context(context)

    expected_token = 'taxi_order_context/{}'.format(taxi_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_taxi_park/')
    assert request.query == {'item_id': taxi_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'taxi_order_context', 'data': context}


async def test_send_waybill_billing_context(
        mock_procaas_create,
        procaas_extract_token,
        taxi_order_id,
        send_waybill_billing_context,
        get_event,
):
    context = get_event('waybill_billing_context')['payload']['data']
    await send_waybill_billing_context(context)

    expected_token = 'waybill_billing_context/{}'.format(taxi_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_taxi_park/')
    assert request.query == {'item_id': taxi_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'waybill_billing_context', 'data': context}
