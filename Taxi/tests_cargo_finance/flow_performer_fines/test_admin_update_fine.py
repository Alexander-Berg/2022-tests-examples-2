async def test_update_idempotency(
        recently,
        get_admin_fines_state,
        inject_events,
        admin_send_request,
        mock_procaas_create,
):
    inject_events()
    state = await get_admin_fines_state()
    decision = state['pending_decisions'][1]
    request_body = {
        'decision': decision['decision'],
        'reason': decision['reason'],
        'operation_token': state['new_decision']['operation_token'],
    }
    await admin_send_request(request_body)

    assert not mock_procaas_create.has_calls


async def test_update_token(
        recently,
        load_json,
        admin_send_request_400_json,
        request_body_from_payload,
        mock_procaas_create,
):
    events = load_json('processing_events.json')
    update_req_event = events[1]
    await admin_send_request_400_json(
        request_body_from_payload(update_req_event['payload']),
    )

    assert not mock_procaas_create.has_calls


async def test_happy_path(
        recently,
        admin_send_request,
        load_json,
        request_body_from_payload,
        mock_procaas_create,
        get_admin_fines_state,
        check_payload,
):
    state = await get_admin_fines_state()
    token = state['new_decision']['operation_token']

    events = load_json('processing_events.json')
    update_req_event = events[1]
    await admin_send_request(
        request_body_from_payload(update_req_event['payload'], token),
    )

    assert mock_procaas_create.times_called == 3

    request = mock_procaas_create.next_call()['request']
    assert request.query['item_id'] == 'alias_id_1'
    check_payload(request.json, events[0]['payload'])

    # skip sum2pay dummy-init
    request = mock_procaas_create.next_call()['request']

    request = mock_procaas_create.next_call()['request']
    assert request.query['item_id'] == 'alias_id_1'
    check_payload(request.json, events[1]['payload'])
