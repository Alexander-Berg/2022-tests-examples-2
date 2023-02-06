import json

import pytest


CORP_CLIENT_ID = '01234567890123456789012345678912'


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_verify_corp_id_create_accepted',
    consumers=['cargo-claims/estimation_result'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'value': 'grocery',
                    'arg_name': 'employer_name',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'is_allowed': True},
        },
    ],
    default_value={'is_allowed': False},
    is_config=True,
)
async def test_happy_path(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
        get_v2_estimation_result,
        get_default_corp_client_id,
        testpoint,
):
    @testpoint('try_localize_addresses')
    async def try_localize_addresses(data):
        return data

    request_id = get_default_idempotency_token
    request_v2 = get_create_request_v2()
    request = {
        'claim': request_v2,
        'estimation_result': get_v2_estimation_result,
        'client': {'corp_client_id': CORP_CLIENT_ID},
    }
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create-accepted?request_id={request_id}',
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    points_count = (await try_localize_addresses.wait_call())['data']['count']
    assert points_count == len(request_v2['route_points'])


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_verify_corp_id_create_accepted',
    consumers=['cargo-claims/estimation_result'],
    clauses=[],
    default_value={'is_allowed': True},
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_mock_estimation_result',
    consumers=['cargo-claims/estimation_result'],
    clauses=[],
    default_value={
        'estimation_result': json.dumps(
            {
                'price': {
                    'offer': {
                        'offer_id': (
                            'cargo-pricing/v1/67574397'
                            '-d44b-4dbe-8542-c6f0d310ef9e'
                        ),
                        'price': {'total': '0'},
                    },
                    'currency_code': 'RUB',
                },
                'vehicle': {
                    'taxi_class': 'lavka',
                    'taxi_requirements': {
                        'door_to_door': True,
                        'fake_middle_point_express': [1],
                    },
                },
                'trip': {
                    'distance_meters': 0.0,
                    'eta': 0.0,
                    'zone_id': 'fake_zone_id',
                },
            },
        ),
    },
    is_config=True,
)
async def test_without_estimating_result(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
        get_v2_estimation_result,
        get_claim_v2,
        get_default_corp_client_id,
):
    request_id = get_default_idempotency_token
    request = {
        'claim': get_create_request_v2(taxi_class='lavka'),
        'client': {'corp_client_id': CORP_CLIENT_ID},
    }
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create-accepted?request_id={request_id}',
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    claim = await get_claim_v2(response.json()['id'])
    # Check that zone_id from experiment was rewrited by real zone
    assert claim['zone_id'] == 'moscow'


@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_verify_corp_id_create_accepted',
    consumers=['cargo-claims/estimation_result'],
    clauses=[],
    default_value={'is_allowed': False},
    is_config=True,
)
async def test_bad_corp_id(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
        get_v2_estimation_result,
        get_default_corp_client_id,
):
    request_id = get_default_idempotency_token
    request = {
        'claim': get_create_request_v2(),
        'estimation_result': get_v2_estimation_result,
        'client': {'corp_client_id': 'bad_corp_client_id'},
    }
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create-accepted?request_id={request_id}',
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'validation_error',
        'message': (
            'Method is not allowed for corp_client_id : ' + CORP_CLIENT_ID
        ),
    }


@pytest.mark.parametrize(
    'status_filter_default, status_filter_clauses',
    [
        (
            False,
            [
                {
                    'title': 'title',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': 'accepted',
                            'arg_name': 'claim_status',
                            'arg_type': 'string',
                        },
                    },
                    'value': {'enabled': True},
                },
            ],
        ),
        (True, []),
    ],
)
@pytest.mark.config(
    CARGO_CLAIMS_EMPLOYER_NAME_MAPPING={CORP_CLIENT_ID: 'grocery'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_verify_corp_id_create_accepted',
    consumers=['cargo-claims/estimation_result'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'value': 'grocery',
                    'arg_name': 'employer_name',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'is_allowed': True},
        },
    ],
    default_value={'is_allowed': False},
    is_config=True,
)
async def test_create_accepted_processing(
        taxi_cargo_claims,
        get_default_headers,
        get_default_idempotency_token,
        get_create_request_v2,
        mock_create_event,
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        get_v2_estimation_result,
        set_up_processing_exp,
        get_default_accept_language,
        get_default_corp_client_id,
        status_filter_default,
        status_filter_clauses,
):
    await procaas_send_settings(is_async=False)
    await procaas_claim_status_filter(
        enabled=status_filter_default, clauses=status_filter_clauses,
    )
    await procaas_event_kind_filter()

    await set_up_processing_exp(processing_flow='enabled', zone_id='moscow')

    mock_create_event(
        idempotency_token='accept_1',
        event={
            'kind': 'status-change-requested',
            'status': 'accepted',
            'data': {
                'claim_version': 1,
                'accept_language': get_default_accept_language,
                'corp_client_id': get_default_corp_client_id,
                'accept_as_create_event': (not status_filter_default),
                'claim_revision': 2,
                'is_terminal': False,
                'phoenix_claim': False,
                'skip_client_notify': False,
                'claim_accepted': False,
                'offer_id': 'taxi_offer_id_1',
                'notify_pricing_claim_accepted': True,
            },
        },
    )

    request_id = get_default_idempotency_token
    request = {
        'claim': get_create_request_v2(),
        'estimation_result': get_v2_estimation_result,
        'client': {'corp_client_id': CORP_CLIENT_ID},
    }
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/create-accepted?request_id={request_id}',
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 200
