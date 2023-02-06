import pytest

from . import conftest
from . import utils_v2


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize(
    'current_status',
    ['new', 'ready_for_approval', 'estimating', 'estimating_failed'],
)
async def test_free_cancel(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        current_status: str,
        url: str,
        state_controller,
):
    claim_info = await state_controller.apply(target_status=current_status)

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'free'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_info.claim_id,
        'status': 'cancelled',
        'version': 1,
        'user_request_revision': '1',
        'skip_client_notify': False,
    }
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'cancelled'


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize('status', ['ready_for_approval', 'performer_lookup'])
async def test_free_cancel_without_order(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        state_controller,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        status,
        url,
):
    claim_info = await state_controller.apply(target_status=status)

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_info.claim_id,
        'status': 'cancelled',
        'version': 1,
        'user_request_revision': '1',
        'skip_client_notify': False,
    }
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'cancelled'


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize(
    'claims_status',
    [
        'accepted',
        'performer_not_found',
        'delivered',
        'delivered_finish',
        'ready_for_return_confirmation',
        'returning',
        'returned',
        'returned_finish',
        'cancelled_by_taxi',
    ],
)
async def test_cancelled_with_payment_forbidden(
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        claims_status,
        url,
):
    claim_info = await state_controller.apply(target_status=claims_status)

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize(
    'status, cancel_state, optional_return', [('cancelled', 'free', False)],
)
async def test_idempotency(
        taxi_cargo_claims,
        get_default_headers,
        mockserver,
        mock_cargo_pricing_calc,
        status,
        cancel_state,
        stq,
        optional_return,
        url,
        state_controller,
):
    state_controller.use_create_version('v2')
    state_controller.handlers().create.request = utils_v2.get_create_request()
    if optional_return:
        state_controller.handlers().create.request['optional_return'] = True
    if status == 'cancelled_with_items_on_hands':
        claim_info = await state_controller.apply(
            target_status=status, next_point_order=2,
        )
    else:
        claim_info = await state_controller.apply(target_status=status)

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': cancel_state},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == status

    if status == 'cancelled_with_payment':
        assert stq.cargo_claims_xservice_change_status.times_called == 0
    if status == 'cancelled_with_items_on_hands':
        assert stq.cargo_claims_xservice_change_status.times_called == 3
    if status == 'cancelled':
        assert stq.cargo_claims_xservice_change_status.times_called == 0


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_dragon_order(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        url,
        assert_segments_cancelled,
):
    creator = await create_segment_with_performer()

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert mock_cargo_pricing_calc.request['entity_id'] == creator.claim_id
    assert mock_cargo_pricing_calc.request[
        'origin_uri'
    ] == 'cargo_claims{}/post'.format(url)
    assert mock_cargo_pricing_calc.request['calc_kind'] == 'final'

    await assert_segments_cancelled()


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize('status', ['ready_for_approval', 'performer_lookup'])
async def test_dragon_no_segment(
        taxi_cargo_claims,
        create_claim_for_segment,
        get_db_segment_ids,
        get_default_headers,
        mock_cargo_pricing_calc,
        get_claim_status,
        mock_waybill_info,
        status: str,
        url: str,
):
    claim_info = await create_claim_for_segment(status=status)
    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'cancelled'

    claim_status = await get_claim_status(claim_info.claim_id)
    assert claim_status == 'cancelled'


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize(
    'cancel_order',
    [('paid', 'free'), ('free', 'paid'), ('free', 'free'), ('paid', 'paid')],
)
async def test_dragon_idempotency(
        taxi_cargo_claims,
        create_claim_for_segment,
        get_db_segment_ids,
        get_default_headers,
        mock_cargo_pricing_calc,
        get_claim_status,
        cancel_order,
        url,
):
    claim_info = await create_claim_for_segment(status='ready_for_approval')
    for cancel_state in cancel_order:
        response = await taxi_cargo_claims.post(
            url,
            params={'claim_id': claim_info.claim_id},
            json={'version': 1, 'cancel_state': cancel_state},
            headers=get_default_headers(),
        )
        assert response.status_code == 200
        assert response.json()['status'] == 'cancelled'


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.parametrize(
    'resolution,with_performer',
    [('failed', True), ('performer_not_found', False)],
)
async def test_cancel_resolved_segment(
        taxi_cargo_claims,
        get_segment_id,
        create_segment,
        get_default_headers,
        build_segment_update_request,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        resolution: str,
        with_performer: bool,
        url: str,
        taxi_order_id='taxi_order_id_1',
):
    """
        Check /cancel returns 409 for resolved segment.
    """
    claim_info = await create_segment()
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

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'inappropriate_status'


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_forbid_cancel_then_delivered_segment(
        taxi_cargo_claims,
        get_segment_id,
        create_segment_with_performer,
        get_default_headers,
        build_segment_update_request,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        url,
        taxi_order_id='taxi_order_id_1',
):
    """
        Check /cancel returns 409 for delivered segment.
    """
    claim_info = await create_segment_with_performer(status='delivered')
    segment_id = await get_segment_id()

    # mark segment complete
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=3,
                    resolution='complete',
                ),
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'inappropriate_status'


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_cancel_state_mismatch(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        url,
):
    """
        Check /cancel returns 409 when cargo_pricing doesn't allowfree cancel.
    """
    claim_info = await create_segment_with_performer(status='performer_found')
    mock_cargo_pricing_calc.pricing_case = 'paid_cancel_in_driving'

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'free'},
        headers=get_default_headers(),
    )

    assert response.status_code == 409
    assert response.json()['code'] == 'free_cancel_is_unavailable'

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/cancel',
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_pricing_default_cancel_case_500(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        url,
):
    """
        Check /cancel returns 500 when cargo_pricing returns default
        pricing-case.
    """
    claim_info = await create_segment_with_performer(status='performer_found')
    mock_cargo_pricing_calc.pricing_case = 'default'

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'free'},
        headers=get_default_headers(),
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
@pytest.mark.config(CARGO_CLAIMS_USE_RETRIEVE_FINAL_CALC_ON_CANCEL=True)
async def test_pricing_retrieve_on_second_recalc(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        mock_cargo_pricing_retrieve,
        url,
):
    claim_info = await create_segment_with_performer(status='performer_found')
    mock_cargo_pricing_calc.pricing_case = 'paid_cancel_in_driving'

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_retrieve.mock.times_called == 0

    mock_cargo_pricing_retrieve.pricing_case = 'paid_cancel_in_driving'

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert mock_cargo_pricing_calc.mock.times_called == 1
    assert mock_cargo_pricing_retrieve.mock.times_called == 1
    assert (
        mock_cargo_pricing_retrieve.request['calc_id']
        == mock_cargo_pricing_calc.calc_id
    )


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_cancel_fallback_with_cargo_pricing_response_500(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mockserver,
        mock_waybill_info,
        mock_cargo_pricing_calc,
        url,
):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _mock(request):
        return mockserver.make_response('{}', status=500)

    claim_info = await create_segment_with_performer(status='performer_found')

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'free'},
        headers=get_default_headers(),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_dragon_order_pricing_dragon_handlers(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        enable_use_pricing_dragon_handlers_feature,
        mock_cargo_pricing_resolve_segment,
        mock_waybill_info,
        url,
        assert_segments_cancelled,
):
    creator = await create_segment_with_performer(is_phoenix=True)

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    await assert_segments_cancelled()
    assert mock_cargo_pricing_resolve_segment.mock.times_called == 1


@pytest.mark.parametrize(
    'url', ['/api/integration/v2/claims/cancel', '/v2/claims/cancel'],
)
async def test_cancel_no_pricing(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_cargo_pricing_retrieve,
        mock_waybill_info,
        url,
        assert_segments_cancelled,
):
    creator = await create_segment_with_performer(
        offer_id=conftest.NO_PRICING_CALC_ID,
    )

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    await assert_segments_cancelled(is_no_pricing=True)
    assert mock_cargo_pricing_calc.mock.times_called == 0

    response = await taxi_cargo_claims.post(
        url,
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert mock_cargo_pricing_calc.mock.times_called == 0
    assert mock_cargo_pricing_retrieve.mock.times_called == 0
