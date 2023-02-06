import pytest

from .. import conftest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_check_points_ready_on_confirm',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[
        {
            'title': 'feature',
            'predicate': {
                'init': {
                    'arg_name': 'claim_features',
                    'set_elem_type': 'string',
                    'value': 'picker',
                },
                'type': 'contains',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={
        '01234567890123456789012345678912': ['picker'],
    },
)
@pytest.mark.parametrize(
    'features,set_point_ready,expected_code',
    (
        pytest.param(['picker'], False, 409, id='point is not ready'),
        pytest.param(['picker'], True, 200, id='point is ready'),
        pytest.param(None, False, 200, id='exp mismatch'),
    ),
)
async def test_exchange_confirm(
        taxi_cargo_claims,
        get_default_headers,
        exchange_confirm,
        prepare_state,
        query_processing_events,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        get_segment,
        features,
        set_point_ready,
        expected_code,
        get_default_cargo_order_id,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    def _make_features(features):
        if features:
            return [{'id': f} for f in features]
        return None

    segment_id = await prepare_state(
        visit_order=1, use_create_v2=True, features=_make_features(features),
    )
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, 1)
    claim_id = segment['diagnostics']['claim_id']

    if set_point_ready:
        response = await taxi_cargo_claims.post(
            '/api/integration/v1/claims/set-points-ready',
            params={'claim_id': segment['diagnostics']['claim_id']},
            headers=get_default_headers(),
            json={},
        )
        assert response.status_code == 200

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id, response_code=expected_code,
    )

    if expected_code == 409:
        assert response.json() == {
            'code': 'claim_point_not_ready',
            'message': 'Заказ ещё не собран',
        }
        return

    event = query_processing_events(claim_id)[0]
    assert event.payload == {
        'data': {
            'claim_uuid': claim_id,
            'claim_origin': 'api',
            'corp_client_id': '01234567890123456789012345678912',
            'is_terminal': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }
    event = query_processing_events(claim_id)[6]
    assert event.payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'driver_profile_id': 'driver_id1',
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


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_check_points_ready_on_confirm',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[
        {
            'title': 'feature',
            'predicate': {
                'init': {
                    'arg_name': 'claim_features',
                    'set_elem_type': 'string',
                    'value': 'picker',
                },
                'type': 'contains',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={
        '01234567890123456789012345678912': ['picker'],
    },
)
async def test_picker_happy_path(
        taxi_cargo_claims,
        get_default_headers,
        exchange_init,
        exchange_confirm,
        prepare_state,
        get_segment,
):
    segment_id = await prepare_state(
        visit_order=1, use_create_v2=True, features=[{'id': 'picker'}],
    )
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, 1)

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id, response_code=409,
    )
    assert response.json() == {
        'code': 'claim_point_not_ready',
        'message': 'Заказ ещё не собран',
    }

    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/set-points-ready',
        params={'claim_id': segment['diagnostics']['claim_id']},
        headers=get_default_headers(),
        json={},
    )
    assert response.status_code == 200

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )

    claim_point_id = conftest.get_claim_point_id_by_order(segment, 2)
    await exchange_init(segment_id, 2)
    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
