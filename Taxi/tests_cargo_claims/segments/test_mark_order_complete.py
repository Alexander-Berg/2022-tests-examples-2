async def test_dragon_order(
        taxi_cargo_claims, get_segment, prepare_segment_state, pgsql,
):
    segment = await prepare_segment_state(visit_order=3)

    # TODO: write test for multiple claims per taxi_order, see CARGODEV-2082
    response = await taxi_cargo_claims.post(
        '/v1/claims/mark/taxi-order-complete',
        params={'claim_id': segment.claim_id, 'segment_id': segment.id},
        json={
            'taxi_order_id': 'taxi_order_id',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200

    segment_doc = await get_segment(segment.id)
    assert segment_doc['status'] == 'delivered_finish'
