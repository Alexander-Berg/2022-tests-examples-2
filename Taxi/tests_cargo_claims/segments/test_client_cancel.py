async def test_cancelled_with_items_on_hands(
        taxi_cargo_claims,
        create_segment_with_performer,
        exchange_confirm,
        get_segment_id,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
):
    creator = await create_segment_with_performer(optional_return=True)
    segment_id = await get_segment_id()

    await exchange_confirm(segment_id, point_visit_order=1)

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/cancel',
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        '/v1/segments/info', params={'segment_id': segment_id},
    )
    assert response.status_code == 200

    assert response.json()['status'] == 'cancelled_with_items_on_hands'
