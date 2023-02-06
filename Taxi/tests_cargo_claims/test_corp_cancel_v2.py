import pytest


@pytest.mark.parametrize(
    'current_status',
    ['performer_found', 'pickup_arrived', 'ready_for_pickup_confirmation'],
)
async def test_phoenix_cancel(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        current_status: str,
        create_segment_with_performer,
        state_controller,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        get_claim_v2,
):
    segment = await create_segment_with_performer(
        autoreorder_flow='newway',
        target_status=current_status,
        is_phoenix=True,
    )

    response = await taxi_cargo_claims.post(
        '/v2/claims/cancel',
        params={'claim_id': segment.claim_id},
        json={
            'version': 1,
            'cancel_state': 'paid',
            'cancel_reason': {'error_code': 'payment_failed'},
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': segment.claim_id,
        'status': 'cancelled',
        'version': 1,
        'user_request_revision': '1',
        'skip_client_notify': False,
    }

    claim = await get_claim_v2(segment.claim_id)
    assert claim['status'] == 'cancelled'
    assert claim['error_messages'] == [
        {
            'code': 'errors.cancel_reason_payment_failed',
            'message': 'Не удалось провести платёж',
        },
    ]


async def test_corp_cancel_v2_pricing_dragon_handlers(
        taxi_cargo_claims,
        get_default_headers,
        create_segment_with_performer,
        mock_cargo_pricing_resolve_segment,
        enable_use_pricing_dragon_handlers_feature,
        mock_waybill_info,
):
    segment = await create_segment_with_performer(
        autoreorder_flow='newway',
        target_status='performer_found',
        is_phoenix=True,
    )
    response = await taxi_cargo_claims.post(
        '/v2/claims/cancel',
        params={'claim_id': segment.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert mock_cargo_pricing_resolve_segment.mock.times_called == 1
