import datetime

import pytest


TIME_LEFT = 5400.0
ETA_COEF = 1.3
POINT_STUCK_TIME_SEC = 30


def get_drw_response():
    return {
        'courier': 'park_id1_driver_id1',
        'position': [55, 37],
        'etas': [
            {
                'point': [55.2, 37.3],
                'time_left': 3600.0,
                'distance_left': 2000.0,
                'point_id': '1',
            },
            {
                'point': [55.3, 37.4],
                'time_left': TIME_LEFT,
                'distance_left': 3000.0,
                'point_id': '2',
            },
        ],
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_support_ticket_creator',
    consumers=['cargo-claims/support-ticket-creator'],
    clauses=[],
    default_value={
        'point_status_eta_delay_policies': [
            {
                'policy_name': 'eta_policy',
                'claim_status': 'pickuped',
                'eta_coef': ETA_COEF,
            },
        ],
        'point_status_duration_delay_policies': [
            {
                'policy_name': 'delay_policy',
                'claim_status': 'pickuped',
                'duration_sec': POINT_STUCK_TIME_SEC,
            },
        ],
    },
    is_config=True,
)
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 3,
    },
    CARGO_CLAIMS_ETA_SOURCE_BY_CORP_CLIENT={
        '__default__': 'driver_route_watcher',
    },
)
@pytest.mark.now('2021-01-01T00:00:00.000Z')
async def test_status_changed_notify(
        taxi_cargo_claims,
        taxi_config,
        mockserver,
        state_controller,
        query_processing_events,
        create_segment_with_performer,
        changedestinations,
        mock_create_event,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        run_processing_events,
        get_default_headers,
        mocked_time,
        stq,
        get_default_cargo_order_id,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    changedestinations(taxi_order_id='taxi_order_id')
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickuped', fresh_claim=False,
    )
    claim_id = claim_info.claim_id
    mock_create_event()

    taxi_config.set_values(
        dict(
            CARGO_CLAIMS_GET_ETA_FROM_LOGISTIC_DISPATCHER={
                '__default__': True,
            },
        ),
    )
    await taxi_cargo_claims.invalidate_caches()

    segment = await taxi_cargo_claims.post(
        f'/v1/segments/info?segment_id={claim_info.claim_id}',
        json={},
        headers=get_default_headers(),
    )

    drw_response = get_drw_response()
    for point in segment.json()['points']:
        for plan_point in drw_response['etas']:
            if plan_point['point_id'] == str(point['claim_point_id']):
                plan_point['point_id'] = point['point_id']

    @mockserver.json_handler(
        '/driver-route-responder/cargo/timeleft-by-courier',
    )
    def _mock_drw(request):
        return drw_response

    event = query_processing_events(claim_id)[6]
    assert event.payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'driver_profile_id': 'driver_id1',
            'claim_origin': 'api',
            'park_id': 'park_id1',
            'is_terminal': False,
            'claim_revision': 9,
            'phoenix_claim': False,
            'current_point_id': 1,
            'skip_client_notify': False,
            'cargo_order_id': get_default_cargo_order_id,
        },
        'kind': 'status-change-succeeded',
        'status': 'pickuped',
    }
    await run_processing_events()
    stq.cargo_claims_xservice_change_status.flush()

    response = await taxi_cargo_claims.post(
        '/v2/processing/claim/status-changed-notify',
        params={'claim_id': claim_id},
        json={'driver_profile_id': 'driver_id1', 'park_id': 'park_id1'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    queue = stq.cargo_claims_support_ticket_creator
    assert queue.times_called == 2
    call = queue.next_call()
    assert call['id'] == f'{claim_id}_eta_policy_pickuped_2'
    assert call['eta'] == mocked_time.now() + datetime.timedelta(
        seconds=TIME_LEFT * ETA_COEF,
    )
    kwargs = call['kwargs']
    assert kwargs['driver_id'] == 'driver_id1'
    assert kwargs['park_id'] == 'park_id1'

    call = queue.next_call()
    assert call['id'] == f'{claim_id}_delay_policy_pickuped_2'
    assert call['eta'] == mocked_time.now() + datetime.timedelta(
        seconds=POINT_STUCK_TIME_SEC,
    )
    kwargs = call['kwargs']
    assert kwargs['driver_id'] == 'driver_id1'
    assert kwargs['park_id'] == 'park_id1'

    assert not stq.cargo_claims_xservice_change_status.times_called


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_taxi_statuses_flow',
    consumers=['cargo-claims/taxi-statuses-flow'],
    clauses=[],
    default_value={'enabled': True, 'delay_ms': 1500},
    is_config=True,
)
async def test_change_taxi_status(
        taxi_cargo_claims,
        state_controller,
        create_segment_with_performer,
        get_default_headers,
        stq,
        mocked_time,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickup_arrived', fresh_claim=False,
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/processing/claim/status-changed-notify',
        params={'claim_id': claim_id},
        json={'driver_profile_id': 'driver_id1', 'park_id': 'park_id1'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert stq.cargo_claims_xservice_change_status.times_called == 1
    stq_params = stq.cargo_claims_xservice_change_status.next_call()
    assert stq_params['kwargs']['driver_id'] == 'driver_id1'
    assert stq_params['kwargs']['park_id'] == 'park_id1'
    assert stq_params['kwargs']['new_status'] == 'waiting'
    assert stq_params['eta'] == mocked_time.now() + datetime.timedelta(
        milliseconds=1500,
    )


@pytest.fixture(name='driver_app_profiles')
def driver_app_profile_fixture(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        assert request.json['id_in_set'] == ['park_id1_driver_id1']
        response = [
            {
                'park_driver_profile_id': request.json['id_in_set'][0],
                'data': {
                    'taximeter_version': '9.50',
                    'taximeter_version_type': '',
                    'taximeter_platform': 'uber',
                },
            },
        ]
        return {'profiles': response}

    return _mock_get_driver_app


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_taxi_statuses_flow',
    consumers=['cargo-claims/taxi-statuses-flow'],
    clauses=[],
    default_value={
        'enabled': True,
        'delay_ms': 1500,
        'taximeter_feature': 'unsupported_feature',
    },
    is_config=True,
)
async def test_unsupported_taximeter_feature(
        taxi_cargo_claims,
        state_controller,
        create_segment_with_performer,
        get_default_headers,
        stq,
        mocked_time,
        driver_app_profiles,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickup_arrived', fresh_claim=False,
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/processing/claim/status-changed-notify',
        params={'claim_id': claim_id},
        json={'driver_profile_id': 'driver_id1', 'park_id': 'park_id1'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert not stq.cargo_claims_xservice_change_status.times_called


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_taxi_statuses_flow',
    consumers=['cargo-claims/taxi-statuses-flow'],
    clauses=[],
    default_value={
        'enabled': True,
        'delay_ms': 1500,
        'taximeter_feature': 'supported_feature',
    },
    is_config=True,
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'supported_feature': '9.48'}},
    },
)
async def test_supported_taximeter_feature(
        taxi_cargo_claims,
        state_controller,
        create_segment_with_performer,
        get_default_headers,
        stq,
        mocked_time,
        driver_app_profiles,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickup_arrived', fresh_claim=False,
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/processing/claim/status-changed-notify',
        params={'claim_id': claim_id},
        json={'driver_profile_id': 'driver_id1', 'park_id': 'park_id1'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert stq.cargo_claims_xservice_change_status.times_called == 1


@pytest.mark.parametrize(
    'exp_value',
    [
        (
            {
                'enabled': True,
                'delay_ms': 1500,
                'taximeter_feature': 'unsupported_feature',
            }
        ),
        ({'enabled': True, 'delay_ms': 1500}),
    ],
)
async def test_driver_profiles_error(
        taxi_cargo_claims,
        state_controller,
        create_segment_with_performer,
        get_default_headers,
        stq,
        mocked_time,
        driver_app_profiles,
        mockserver,
        experiments3,
        exp_value,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_taxi_statuses_flow',
        consumers=['cargo-claims/taxi-statuses-flow'],
        clauses=[],
        default_value=exp_value,
    )
    await taxi_cargo_claims.invalidate_caches()

    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='pickup_arrived', fresh_claim=False,
    )
    claim_id = claim_info.claim_id

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_claims.post(
        '/v2/processing/claim/status-changed-notify',
        params={'claim_id': claim_id},
        json={'driver_profile_id': 'driver_id1', 'park_id': 'park_id1'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert stq.cargo_claims_xservice_change_status.times_called == 1
