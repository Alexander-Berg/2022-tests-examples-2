import datetime

import pytest

HEADERS = {'X-Remote-IP': '12.34.56.78'}
CONFIRMATION_CODE = '123456'


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
@pytest.mark.parametrize(
    'skip_confirmation, expected_confirm_code, change_status_count, '
    'signature_create_count, signature_confirm_count',
    [(True, 200, 1, 0, 0), (False, 403, 1, 1, 1)],
)
@pytest.mark.now('2020-04-01T10:35:00+0300')
async def test_skip_confirmation(
        taxi_cargo_claims,
        mockserver,
        get_default_request,
        state_controller,
        stq,
        get_default_headers,
        get_default_driver_auth_headers,
        skip_confirmation,
        expected_confirm_code,
        change_status_count,
        signature_create_count,
        signature_confirm_count,
        now,
        mocker_archive_get_order_proc,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    @mockserver.json_handler('/esignature-issuer/v1/signatures/create')
    def _signature_create(request):
        # Check backward compatibility for signature_id
        assert request.json['signature_id'] == 'sender_to_driver'
        return {}

    @mockserver.json_handler('/esignature-issuer/v1/signatures/confirm')
    def _signature_confirm(request):
        assert request.json['signature_id'] == 'sender_to_driver'
        assert request.json['code'] == CONFIRMATION_CODE
        return {'status': 'ok'}

    # create claim without confirmation
    request = get_default_request()
    request['route_points']['source']['skip_confirmation'] = skip_confirmation

    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(
        target_status='ready_for_pickup_confirmation',
    )
    claim_id = claim_info.claim_id

    # check claim state
    response = await taxi_cargo_claims.post(
        'driver/v1/cargo-claims/v1/cargo/state',
        headers=dict(get_default_driver_auth_headers, **HEADERS),
        json={'cargo_ref_id': claim_id},
    )
    response_json = response.json()
    assert response.status_code == 200, response_json
    response_json.pop('current_route', {})
    assert response_json == {
        'status': 'pickup_confirmation',
        'current_point': {
            'id': 1,
            'label': 'source',
            'phones': [
                {
                    'label': 'phone_label.source',
                    'type': 'source',
                    'view': 'main',
                },
                {
                    'label': 'phone_label.destination',
                    'type': 'destination',
                    'view': 'extra',
                },
                {'label': 'Помощь', 'type': 'emergency', 'view': 'extra'},
            ],
            'actions': [
                {
                    'type': 'pickup',
                    'need_confirmation': not skip_confirmation,
                    'conditions': [],
                },
                {
                    'type': 'cancel',
                    'force_allowed': True,
                    'force_punishments': [
                        {
                            'description': 'Активность ' '-10',
                            'type': 'activity',
                        },
                    ],
                    'free_conditions': [
                        {
                            'type': 'time_after',
                            'value': '2020-04-01T07:50:00.000000Z',
                        },
                        {'type': 'min_call_count', 'value': '3'},
                    ],
                },
                {'type': 'show_act'},
            ],
            'type': 'source',
            'need_confirmation': not skip_confirmation,
            'visit_order': 1,
        },
        'total_point_count': 1,
        'phones': [
            {'label': 'phone_label.source', 'type': 'source', 'view': 'main'},
            {
                'label': 'phone_label.destination',
                'type': 'destination',
                'view': 'extra',
            },
            {'label': 'Помощь', 'type': 'emergency', 'view': 'extra'},
            {'label': 'Помощь', 'type': 'emergency', 'view': 'main'},
        ],
    }

    response = await taxi_cargo_claims.post(
        'driver/v1/cargo-claims/v1/cargo/exchange/confirm',
        headers=dict(get_default_driver_auth_headers, **HEADERS),
        json={
            'cargo_ref_id': claim_id,
            'last_known_status': 'pickup_confirmation',
        },
    )
    response_json = response.json()
    assert response.status_code == expected_confirm_code, response_json
    if response.status_code == 200:
        response_json.pop('new_route', {})
        assert response_json == {
            'new_status': 'delivering',
            'result': 'confirmed',
            'new_point': {
                'id': 2,
                'label': 'destination',
                'phones': [
                    {
                        'label': 'phone_label.source',
                        'type': 'source',
                        'view': 'main',
                    },
                    {
                        'label': 'phone_label.destination',
                        'type': 'destination',
                        'view': 'extra',
                    },
                    {'label': 'Помощь', 'type': 'emergency', 'view': 'extra'},
                ],
                'actions': [
                    {'type': 'arrived_at_point'},
                    {'type': 'show_act'},
                ],
                'type': 'destination',
                'need_confirmation': True,
                'visit_order': 1,
            },
        }
    elif response.status_code == 403:
        assert response.json() == {
            'code': 'confirmation_code_required',
            'message': 'Для подтверждения данной заявки необходим код из смс',
        }

        response = await taxi_cargo_claims.post(
            'driver/v1/cargo-claims/v1/cargo/exchange/confirm',
            headers=dict(get_default_driver_auth_headers, **HEADERS),
            json={
                'cargo_ref_id': claim_id,
                'last_known_status': 'pickup_confirmation',
                'confirmation_code': CONFIRMATION_CODE,
            },
        )
        assert response.status_code == 200

    queue = stq.cargo_claims_xservice_change_status
    assert queue.times_called == change_status_count
    if change_status_count:
        stq_calls = [queue.next_call() for _ in range(queue.times_called)]
        stq_calls = {call['id']: call['kwargs'] for call in stq_calls}
        for call in stq_calls.values():
            call.pop('log_extra')

        assert stq_calls == {
            'taxi_order_id_1_transporting': {
                'taxi_order_id': 'taxi_order_id_1',
                'park_id': 'park_id1',
                'driver_id': 'driver_id1',
                'alias_id': 'order_alias_id_1',
                'reason': 'Automatically',
                'new_status': 'transporting',
                'stq_first_call_ts': {'$date': '2020-04-01T07:35:00.000Z'},
            },
        }

    assert _signature_create.times_called == signature_create_count
    assert _signature_confirm.times_called == signature_confirm_count
