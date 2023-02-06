import json

import pytest

INVALID_DRIVER_HEADER = {'X-YaTaxi-Driver-Profile-Id': 'invalid'}
INVALID_PARK_HEADER = {'X-YaTaxi-Park-Id': 'invalid'}


@pytest.mark.parametrize(
    'locale,expected_msg',
    [
        ('ru', 'Превышен лимит смс'),
        # TODO: fix in CARGODEV-11356
        # ('en', 'Sms limit exceeded')
    ],
)
@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_esignature_error_translation_init(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        locale,
        expected_msg,
        mockserver,
        get_segment_id,
        raw_exchange_init,
):
    await state_controller.apply(target_status='ready_for_pickup_confirmation')

    @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
    def _signature_create(request):
        return mockserver.make_response(
            json.dumps({'code': 'too_many_requests', 'message': ''}),
            status=429,
        )

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=1)

    assert response.status_code == 429
    assert response.json() == {
        'code': 'esignature_too_many_requests',
        'message': expected_msg,
    }


@pytest.mark.parametrize(
    'locale,expected_msg',
    [
        ('ru', 'Превышен лимит подтверждений'),
        # TODO: fix in CARGODEV-11356
        # ('en', 'Confirmations limit exceeded'),
    ],
)
@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_esignature_error_translation_confirm(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        locale,
        expected_msg,
        mockserver,
        get_segment_id,
        raw_exchange_confirm,
):
    @mockserver.json_handler('/esignature-issuer/v1/signatures/confirm')
    def _signature_create(request):
        return mockserver.make_response(
            json.dumps({'code': 'too_many_requests', 'message': ''}),
            status=429,
        )

    await state_controller.apply(target_status='ready_for_pickup_confirmation')

    segment_id = await get_segment_id()
    response = await raw_exchange_confirm(segment_id, point_visit_order=1)

    assert response.status_code == 429
    assert response.json() == {
        'code': 'esignature_too_many_requests',
        'message': expected_msg,
    }
