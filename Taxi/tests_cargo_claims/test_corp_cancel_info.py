import pytest

from . import conftest
from . import utils_v2


async def test_cancel_info_wrong_claim(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel-info?claim_id=some_id',
        headers=get_default_headers(),
    )
    assert response.status_code == 404


async def test_cancel_info_wrong_corp_client_id(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel-info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers('some_corp_id01234567890123456789'),
    )
    assert response.status_code == 404


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.parametrize(
    'claim_status',
    [
        'failed',
        'delivered_finish',
        'returned_finish',
        'performer_not_found',
        'cancelled',
        'cancelled_with_payment',
        'cancelled_by_taxi',
        'cancelled_with_items_on_hands',
    ],
)
async def test_cancel_info_terminal_claim_status(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        mock_cargo_pricing_calc,
        claim_status: str,
):
    state_controller.use_create_version('v2')
    if claim_status == 'cancelled_with_items_on_hands':
        state_controller.handlers().create.request = (
            utils_v2.get_create_request(optional_return=True)
        )
        claim_info = await state_controller.apply(
            target_status=claim_status, next_point_order=2,
        )
    else:
        claim_info = await state_controller.apply(target_status=claim_status)

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel-info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['cancel_state'] == 'unavailable'


# cp = cargo_pricing
@pytest.mark.parametrize(
    'cp_code, cp_pricing_case, response_code, cancel_state',
    [
        (500, None, 500, None),
        (200, 'default', 500, None),
        (200, 'free_cancel', 200, 'free'),
        (200, 'paid_cancel', 200, 'paid'),
        (200, 'paid_cancel_in_driving', 200, 'paid'),
    ],
)
async def test_cancel_info_fetch_cargo_payments(
        taxi_cargo_claims,
        create_segment,
        get_default_headers,
        mockserver,
        cp_code,
        cp_pricing_case,
        response_code,
        cancel_state,
        mock_waybill_info,
):
    claim_info = await create_segment()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def mock_cargo_pricing(request):
        assert request.json['entity_id'] == claim_info.claim_id
        assert (
            request.json['origin_uri']
            == 'cargo-claims/api/integration/v2/claims/cancel-info'
        )
        assert request.json['calc_kind'] == 'final'
        return mockserver.make_response(
            json={
                'calc_id': 'some_calc_id',
                'details': {
                    'pricing_case': cp_pricing_case,
                    'total_distance': '7082.175781',
                    'total_time': '2154',
                    'paid_waiting_price': '0',
                    'paid_waiting_time': '60',
                    'paid_waiting_in_destination_price': '0',
                    'paid_waiting_in_destination_time': '30',
                    'paid_waiting_in_destination_total_price': '2',
                    'paid_waiting_in_transit_price': '0',
                    'paid_waiting_in_transit_time': '0',
                },
                'price': '499',
                'units': {
                    'currency': 'RUB',
                    'distance': 'kilometer',
                    'time': 'minute',
                },
                'services': [],
            }
            if cp_pricing_case is not None
            else {},
            status=cp_code,
        )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel-info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert mock_cargo_pricing.times_called == 1
    assert response.status_code == response_code
    if cancel_state is not None:
        assert response.json()['cancel_state'] == cancel_state


async def test_cancel_info_pricing_dragon_handlers(
        taxi_cargo_claims,
        create_segment,
        get_default_headers,
        mock_cargo_pricing_resolve_segment,
        enable_use_pricing_dragon_handlers_feature,
        mock_waybill_info,
):
    claim_info = await create_segment(is_phoenix=True)

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel-info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert mock_cargo_pricing_resolve_segment.mock.times_called == 1
    assert response.status_code == 200


async def test_cancel_info_no_pricing(
        taxi_cargo_claims,
        create_segment,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
):
    claim_info = await create_segment(offer_id=conftest.NO_PRICING_CALC_ID)

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel-info',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert mock_cargo_pricing_calc.mock.times_called == 0
