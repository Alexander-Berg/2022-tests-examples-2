import datetime

import pytest

PARK_ID = 'park_1'
SESSION = 'test_session'


def _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc):
    mocker_archive_get_order_proc(
        {
            '_id': 'taxi_order_id_1',
            'order': {'nz': 'moscow', 'city': 'Москва'},
            'performer': {'candidate_index': 0},
            'order_link': '8f6802e601b2179177df4a8e89c54b97',
            'aliases': [
                {
                    'generation': 1,
                    'due_optimistic': None,
                    'id': 'order_alias_1',
                    'due': now + datetime.timedelta(minutes=5),
                },
            ],
            'candidates': [
                {'dp_values': {'a': -10}, 'alias_id': 'order_alias_1'},
            ],
            'order_info': {
                'statistics': {'status_updates': [{'c': now, 't': 'waiting'}]},
            },
        },
    )


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.config(FREE_WAITING_TIME_RULES={'__default__': 600})
@pytest.mark.now('2020-04-20T00:00:00Z')
@pytest.mark.parametrize(
    [
        'claim_status',
        'taximeter_status',
        'taximeter_point',
        'retries',
        'pickup_code',
        'expected_new_status',
        'expected_error',
        'next_point_order',
    ],
    [
        pytest.param(
            'performer_found',
            'new',
            1,
            2,
            None,
            'pickup_arrived',
            None,
            1,
            id='performer_found',
        ),
        pytest.param(
            'pickup_arrived',
            'new',
            1,
            2,
            None,
            'pickup_arrived',
            None,
            1,
            id='pickup_arrived',
        ),
        pytest.param(
            'pickup_arrived',
            'new',
            1,
            2,
            'code',
            'pickup_arrived',
            None,
            1,
            id='pickup_arrived_with_code',
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            'pickup_confirmation',
            1,
            1,
            'code',
            'ready_for_pickup_confirmation',
            {
                'code': 'state_mismatch',
                'message': (
                    'Invalid claim action, refresh the page (state_mismatch)'
                ),
            },
            1,
            id='invalid_status_1',
        ),
        pytest.param(
            'pickuped',
            'delivering',
            2,
            2,
            None,
            'delivery_arrived',
            None,
            2,
            id='pickuped',
        ),
        pytest.param(
            'ready_for_delivery_confirmation',
            'droppof_confirmation',
            2,
            2,
            None,
            'ready_for_delivery_confirmation',
            None,
            2,
            id='delivery_confirmation',
        ),
    ],
)
async def test_cargo_arrive_at_point(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        now,
        get_default_c2c_request_v2_full,
        get_default_cargo_order_id,
        mocker_archive_get_order_proc,
        get_segment_id,
        stq,
        claim_status: str,
        taximeter_status: str,
        taximeter_point: int,
        retries: int,
        pickup_code: str,
        expected_new_status: str,
        expected_error: str,
        next_point_order: int,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)
    request = get_default_c2c_request_v2_full(cargo=True)
    request['claim']['route_points'][0]['pickup_code'] = pickup_code
    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.handlers().create.request = request
    await state_controller.apply(
        next_point_order=next_point_order, target_status=claim_status,
    )

    segment_id = await get_segment_id()
    for _ in range(retries):
        response = await taxi_cargo_claims.post(
            '/v1/segments/arrive_at_point',
            params={'segment_id': segment_id},
            json={
                'cargo_order_id': get_default_cargo_order_id,
                'last_known_status': taximeter_status,
                'point_id': taximeter_point,
                'idempotency_token': '100500',
                'driver': {
                    'park_id': 'park_id1',
                    'driver_profile_id': 'driver_id1',
                },
            },
            headers={
                **get_default_driver_auth_headers,
                'X-Real-IP': '0.0.0.0',
            },
        )
        assert response.status_code == 200

        response_json = response.json()
        if expected_error:
            assert response.status_code == 409, response_json
            assert response_json == expected_error
        else:
            assert response.status_code == 200, response_json

            new_claim_info = await state_controller.get_claim_info()
            assert new_claim_info.current_state.status == expected_new_status

        if not pickup_code:
            assert stq.cargo_claims_pickup_code_driver_sms.times_called == 0
