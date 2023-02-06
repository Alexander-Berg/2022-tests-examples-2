import pytest

DEFAULT_HEADERS = {'X-Real-IP': '12.34.56.78'}


# status:       pickuped,
# next point:   B1 (first destination point)
# post-payment: enabled
@pytest.fixture(name='state_ready_for_init')
def _state_ready_for_init(
        enable_payment_on_delivery,
        mock_payments_check_token,
        mock_payment_create,
        create_segment_with_performer,
        do_prepare_segment_state,
):
    async def _wrapper(payment_method='card', **kwargs):
        segment = await create_segment_with_performer(
            payment_method=payment_method, **kwargs,
        )
        return await do_prepare_segment_state(
            segment, visit_order=2, last_exchange_init=False,
        )

    return _wrapper


def build_init_request(*, claim_point_id):
    return {
        'last_known_status': 'delivering',
        'point_id': claim_point_id,
        'idempotency_token': '100500',
        'park_id': 'some_park',
        'driver_profile_id': 'some_driver',
    }


async def test_init_is_not_allowed(
        taxi_cargo_claims,
        state_ready_for_init,
        get_current_claim_point,
        mock_payment_status,
        payment_method='card',
):
    """
        exchange/init is not allowed until payment received.
    """
    mock_payment_status.is_paid = False

    segment = await state_ready_for_init()

    current_point_id = await get_current_claim_point(segment.claim_id)

    response = await taxi_cargo_claims.post(
        '/v1/segments/exchange/init',
        params={'segment_id': segment.id},
        json=build_init_request(claim_point_id=current_point_id),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 409
    assert response.json()['code'] == 'payment_required'


async def test_init_after_paid(
        taxi_cargo_claims,
        state_ready_for_init,
        get_current_claim_point,
        mock_payment_status,
        payment_method='card',
):
    """
        exchange/init is allowed after payment received.
    """
    segment = await state_ready_for_init()

    current_point_id = await get_current_claim_point(segment.claim_id)

    response = await taxi_cargo_claims.post(
        '/v1/segments/exchange/init',
        params={'segment_id': segment.id},
        json=build_init_request(claim_point_id=current_point_id),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {
        'new_status': 'droppof_confirmation',
        'new_claim_status': 'ready_for_delivery_confirmation',
    }
