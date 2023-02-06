from .. import conftest


async def test_point_skipped_notify(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        query_processing_events,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    segment_id = await prepare_state(visit_order=2, pickup_code=None)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, 2)

    json = {
        'point_id': claim_point_id,
        'last_known_status': conftest.TAXIMETER_STATUS_BY_STATUS[
            segment['status']
        ],
        'comment': 'some comment',
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

    event = query_processing_events(str(claim_point_id))[-1]
    assert event.payload == {
        'data': {
            'comment': 'some comment',
            'reasons': ['reason_a', 'reason_b'],
            'corp_client_id': '01234567890123456789012345678912',
            'cargo_claim_id': segment['claim_id'],
        },
        'kind': 'point-visit-status-changed',
        'status': 'skipped',
    }
