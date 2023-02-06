import pytest


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
async def test_happy_path(
        taxi_cargo_claims,
        create_segment_with_performer,
        run_processing_events,
        mock_create_event,
        get_default_corp_client_id,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        check_processing_stats,
        pgsql,
        extract_oldest_event_lag,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    claim_info = await create_segment_with_performer()
    mock_create_event()

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT id FROM cargo_claims.processing_events
        WHERE item_id = '{claim_info.claim_id}'
        """,
    )
    assert list(cursor) == [(1,), (2,), (3,), (4,)]

    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=4,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
    )

    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-performer-assigned',
        json={
            'claims_ids': [claim_info.claim_id],
            'driver_profile_id': 'driver_1',
            'park_id': 'park_1',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200

    create_event = mock_create_event(
        item_id=claim_info.claim_id,
        idempotency_token=f'performer_assigned_driver_1_1_1',
        queue='claim',
        event={
            'kind': 'status-change-succeeded',
            'data': {
                'corp_client_id': get_default_corp_client_id,
                'claim_origin': 'api',
                'driver_profile_id': 'driver_1',
                'park_id': 'park_1',
                'lookup_version': 1,
                'is_terminal': False,
                'current_point_id': 1,
                'skip_client_notify': False,
            },
            'status': 'performer_assigned',
        },
    )

    result = await run_processing_events()
    extract_oldest_event_lag(result)
    await check_processing_stats(
        result,
        processed_in_stq=1,
        for_processing_cnt=1,
        failed_cnt=0,
        stq_success=1,
    )
    assert create_event.times_called == 1


async def test_no_claims_for_order(
        taxi_cargo_claims, create_segment_with_performer,
):
    await create_segment_with_performer()

    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-performer-assigned',
        json={
            'claims_ids': ['unknown'],
            'driver_profile_id': 'driver_1',
            'park_id': 'park_1',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 500
