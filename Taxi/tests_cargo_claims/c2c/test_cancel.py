import pytest


PERFORMER_FOUND_TS = '2020-02-03T07:08:09.00+00:00'


@pytest.fixture(name='cancel_claim')
def _cancel_claim(taxi_cargo_claims, get_default_headers):
    async def wrapper(claim_id):
        response = await taxi_cargo_claims.post(
            '/v2/claims/c2c/cancel',
            params={'claim_id': claim_id},
            json={'version': 1, 'cancel_state': 'paid'},
            headers=get_default_headers(),
        )
        return response

    return wrapper


def assert_cargo_pricing_request(request, claim_id):
    assert request['performer'] == {
        'assigned_at': '2020-02-03T07:08:09+00:00',
        'driver_id': 'driver_id1',
        'park_db_id': 'park_id1',
    }
    assert request['entity_id'] == claim_id
    assert request['origin_uri'] == 'cargo_claims/v2/claims/c2c/cancel/post'
    assert request['calc_kind'] == 'final'


async def test_dragon_order(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_db_segment_ids,
        state_controller,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        mock_create_event,
        cancel_claim,
        assert_segments_cancelled,
):
    mock_create_event()
    order_info = mock_waybill_info.response['execution']['taxi_order_info']
    order_info['last_performer_found_ts'] = PERFORMER_FOUND_TS

    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.set_options(payment_type='card')
    claim_info = await state_controller.apply(target_status='performer_found')
    cancel_response = await cancel_claim(claim_info.claim_id)
    assert cancel_response.status_code == 200

    await assert_segments_cancelled()
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert_cargo_pricing_request(
        mock_cargo_pricing_calc.request, claim_info.claim_id,
    )


@pytest.mark.parametrize(
    'resolution,with_performer',
    [('failed', True), ('performer_not_found', False)],
)
async def test_cancel_resolved_segment(
        taxi_cargo_claims,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        mock_create_event,
        state_controller,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        cancel_claim,
        resolution: str,
        with_performer: bool,
        taxi_order_id='taxi_order_id_1',
):
    """
        Check /cancel returns 409 for resolved segment.
    """
    mock_create_event()
    state_controller.use_create_version('v2_cargo_c2c')
    claim_info = await state_controller.apply(target_status='performer_found')
    segment_id = await get_segment_id()

    # mark segment resolved
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=3,
                    resolution=resolution,
                    with_performer=with_performer,
                ),
            ],
        },
    )
    assert response.status_code == 200

    cancel_response = await cancel_claim(claim_info.claim_id)
    assert cancel_response.status_code == 409
    assert cancel_response.json()['code'] == 'inappropriate_status'


async def test_cancel_with_default(
        taxi_cargo_claims,
        mock_create_event,
        state_controller,
        create_segment_with_performer,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        cancel_claim,
):
    mock_cargo_pricing_calc.pricing_case = 'default'
    segment = await create_segment_with_performer()
    await state_controller.apply(target_status='delivered', fresh_claim=False)
    response = await taxi_cargo_claims.post(
        '/v1/claims/mark/taxi-order-complete',
        params={'claim_id': f'order/{segment.cargo_order_id}'},
        json={
            'taxi_order_id': 'taxi_order_id',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200

    mock_create_event()
    state_controller.use_create_version('v2_cargo_c2c')

    cancel_response = await cancel_claim(segment.claim_id)
    assert cancel_response.status_code == 409
    assert cancel_response.json()['code'] == 'inappropriate_status'


async def test_dragon_order_pricing_dragon_handlers(
        state_controller,
        mock_cargo_pricing_resolve_segment,
        mock_waybill_info,
        mock_create_event,
        mock_cargo_corp_up,
        enable_use_pricing_dragon_handlers_feature,
        cancel_claim,
        assert_segments_cancelled,
):
    mock_create_event()
    order_info = mock_waybill_info.response['execution']['taxi_order_info']
    order_info['last_performer_found_ts'] = PERFORMER_FOUND_TS

    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.set_options(payement_type='card')
    state_controller.set_options(is_phoenix=True)
    claim_info = await state_controller.apply(target_status='performer_found')

    cancel_response = await cancel_claim(claim_info.claim_id)
    assert cancel_response.status_code == 200
    await assert_segments_cancelled()

    assert mock_cargo_pricing_resolve_segment.mock.times_called == 1
    assert_cargo_pricing_request(
        mock_cargo_pricing_resolve_segment.request['v1_request'],
        claim_info.claim_id,
    )
