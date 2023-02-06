# pylint: disable=cell-var-from-loop
import json

import pytest


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_happy_path(
        taxi_cargo_claims,
        get_default_driver_auth_headers,
        get_current_claim_point,
        mockserver,
        skip_confirmation,
        state_controller,
        get_claim_status,
        get_full_claim,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
):
    state_controller.use_create_version('v2')
    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='performer_found')

    current_point = await get_current_claim_point(claim_info.claim_id)

    for (idx, signature, signer_id) in (
            (0, 'sender_to_driver_{}', '+79999999991_id'),
            (1, 'driver_to_recipient_{}', '+79999999992_id'),
            (2, 'driver_to_recipient_{}', '+79999999993_id'),
    ):

        @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
        def _signature_create(request):
            # Send sms to right point
            assert request.json['signer_id'] == signer_id
            assert request.json['signature_id'] == signature.format(
                current_point,
            )
            return mockserver.make_response('{}', status=200)

        segment_id = await get_segment_id()
        response = await raw_exchange_init(
            segment_id, point_visit_order=current_point,
        )
        assert response.status_code == 200

        if not skip_confirmation:
            assert _signature_create.times_called == 1

        # CONFIRM
        @mockserver.json_handler('/esignature-issuer/v1/signatures/confirm')
        def _signature_confirm(request):
            assert request.json['signature_id'] == signature.format(
                current_point,
            )
            return mockserver.make_response(
                json.dumps({'status': 'ok'}), status=200,
            )

        response = await raw_exchange_confirm(
            segment_id, point_visit_order=current_point,
        )
        response_json = response.json()
        assert response.status_code == 200, response_json

        if not skip_confirmation:
            assert _signature_confirm.times_called == 1

        claim_status = await get_claim_status(claim_info.claim_id)
        current_claim_point = await get_current_claim_point(
            claim_info.claim_id,
        )
        if idx == 2:
            assert (current_claim_point, claim_status) == (4, 'delivered')
        else:
            assert (current_claim_point, claim_status) == (
                current_point + 1,
                'pickuped',
            )

        current_point += 1

    full_claim = await get_full_claim(claim_info.claim_id)

    # TODO: fix in CARGODEV-11356
    # for point in full_claim['route_points']:
    #     assert point['visited_at'] == {'actual': matching.any_string}

    points_visit_statuses = [
        (point['visit_order'], point['visit_status'])
        for point in full_claim['route_points']
    ]
    assert points_visit_statuses == [
        (1, 'visited'),
        (2, 'visited'),
        (3, 'visited'),
        (4, 'skipped'),
    ]


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.experiments3(filename='exp3_esignature_enable_additional.json')
@pytest.mark.parametrize(
    'target_status,times_called',
    [
        ('pickup_arrived', 1),
        ('ready_for_pickup_confirmation', 2),
        ('pickuped', 3),
        ('delivery_arrived', 4),
    ],
)
async def test_create_signature_on_arrive(
        mockserver, state_controller, target_status, times_called,
):
    @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
    def _signature_create(request):
        return mockserver.make_response('{}', status=200)

    await state_controller.apply(target_status=target_status)
    assert _signature_create.times_called == times_called
