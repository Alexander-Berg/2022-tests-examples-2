from .. import conftest


async def test_pickuped_event(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        query_processing_events,
        changedestinations,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        mock_create_event,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    mock_create_event()

    segment_id = await prepare_state(visit_order=2, pickup_code=None)

    segment = await get_segment(segment_id)

    claim_point_id = conftest.get_claim_point_id_by_order(segment, 2)

    json = {
        'point_id': claim_point_id,
        'last_known_status': conftest.TAXIMETER_STATUS_BY_STATUS[
            segment['status']
        ],
        'reasons': ['reason_a', 'reason_b'],
    }
    json['driver'] = conftest.DRIVER_INFO
    json['need_return_items'] = True
    segment = await get_segment(segment_id)

    await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=json,
        headers=conftest.get_headers(),
    )

    event = query_processing_events(segment['claim_id'])[-1]
    assert event.payload == {
        'data': {
            'claim_revision': 12,
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'current_point_id': 2,
            'phoenix_claim': False,
            'is_terminal': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'returning',
    }
