import pytest


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
async def test_pickuped_event(
        taxi_cargo_claims,
        state_controller,
        query_processing_events,
        create_segment_with_performer,
        changedestinations,
        mock_create_event,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        check_processing_stats,
        run_processing_events,
        testpoint,
        extract_oldest_event_lag,
        get_default_cargo_order_id,
        get_default_corp_client_id,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    changedestinations(taxi_order_id='taxi_order_id')
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickuped', fresh_claim=False,
    )
    claim_id = claim_info.claim_id
    mock_create_event()

    @testpoint('send-events-from-stq')
    def test_point(data):
        assert data['event_id']

    event = query_processing_events(claim_id)[0]
    assert event.payload == {
        'data': {
            'claim_uuid': claim_info.claim_id,
            'corp_client_id': get_default_corp_client_id,
            'claim_origin': 'api',
            'is_terminal': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }
    event = query_processing_events(claim_id)[6]
    assert event.payload == {
        'data': {
            'corp_client_id': get_default_corp_client_id,
            'claim_origin': 'api',
            'driver_profile_id': 'driver_id1',
            'park_id': 'park_id1',
            'is_terminal': False,
            'claim_revision': 9,
            'phoenix_claim': False,
            'current_point_id': 1,
            'skip_client_notify': False,
            'cargo_order_id': get_default_cargo_order_id,
        },
        'kind': 'status-change-succeeded',
        'status': 'pickuped',
    }
    assert (
        event.idempotency_token
        == 'pickuped_9db1622e-582d-4091-b6fc-4cb2ffdc12c0_'
        'taxi_order_id_driver_id1_1'
    )
    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=7,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
    )
    assert test_point.times_called == 7
    test_point.next_call()
