import json

import pytest


@pytest.mark.parametrize(
    (
        'current_claim_status',
        'esignature_response',
        'expected_response_code',
        'expect_esignature_called',
        'custom_tanker_key',
    ),
    (
        pytest.param('new', None, 404, 0, False, id='invalid_status'),
        pytest.param(
            'ready_for_pickup_confirmation',
            None,
            404,
            2,
            False,
            id='no_signature',
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            {'code': '1234', 'attempts': 3},
            200,
            2,
            False,
            id='ok',
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            {'code': '1234', 'attempts': 3},
            200,
            2,
            True,
            id='ok_custom_key',
            marks=pytest.mark.config(
                CARGO_CLAIMS_CUSTOM_CORP_MESSAGES={
                    '01234567890123456789012345678912': {
                        'cargo_sender_to_driver_without_id_verification': (
                            'some_tanker_key'
                        ),
                    },
                },
            ),
        ),
        pytest.param(
            'ready_for_return_confirmation',
            {'code': '1234', 'attempts': 3},
            200,
            2,
            False,
            id='return_ok',
        ),
    ),
)
async def test_confirmation_code(
        mockserver,
        taxi_cargo_claims,
        esignature_issuer,
        state_controller,
        get_default_headers,
        current_claim_status,
        esignature_response,
        expected_response_code,
        expect_esignature_called,
        custom_tanker_key,
):
    @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
    def _signature_create(request):
        assert request.headers['Accept-language']
        send_properties = request.json['properties']['send_properties'][0]
        assert send_properties['intent'] == 'cargo_verification'
        if custom_tanker_key:
            assert send_properties['tanker_key'] == 'some_tanker_key'
        else:
            assert send_properties['tanker_key'] in (
                'cargo_sender_to_driver_without_id_verification',
                'cargo_driver_to_return_without_id_verification',
            )
        assert send_properties['extra_data'] == {
            'points_number': '1',
            'external_order_id': '',
        }
        return mockserver.make_response('{}', status=200)

    claim_info = await state_controller.apply(
        target_status=current_claim_status,
    )
    claim_id = claim_info.claim_id

    @mockserver.json_handler(
        '/esignature-issuer/v1/signatures/confirmation-code',
    )
    def _esignature_confirmation_code(request):
        if esignature_response is None:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'Not found'}),
                status=404,
            )
        return esignature_response

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/confirmation_code',
        headers=get_default_headers(),
        json={'claim_id': claim_id},
    )
    assert response.status_code == expected_response_code

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/confirmation_code',
        headers=get_default_headers(),
        json={'claim_id': claim_id},
    )
    assert response.status_code == expected_response_code

    assert (
        _esignature_confirmation_code.times_called == expect_esignature_called
    )
