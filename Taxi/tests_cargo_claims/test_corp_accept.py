import copy

import pytest

from . import utils_v2

CORP_CLIENT_ID = '01234567890123456789012345678912'


@pytest.mark.config(CARGO_CLAIMS_FEATURES_VALIDATION_ENABLED=True)
@pytest.mark.parametrize(
    ('claim_features', 'expected_features'),
    (
        pytest.param(
            None,
            ['limited_paid_waiting'],
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='limit_paid_waiting_point_ready',
                    consumers=['cargo-claims/accept'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
            id='limited_paid_waiting_enabled',
        ),
        pytest.param(
            None,
            None,
            marks=[
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='limit_paid_waiting_point_ready',
                    consumers=['cargo-claims/accept'],
                    clauses=[],
                    default_value={'enabled': False},
                ),
            ],
            id='limited_paid_waiting_disabled',
        ),
        pytest.param(
            ['partial_delivery'],
            ['partial_delivery', 'limited_paid_waiting'],
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={
                        '01234567890123456789012345678912': [
                            'partial_delivery',
                        ],
                    },
                ),
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='limit_paid_waiting_point_ready',
                    consumers=['cargo-claims/accept'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
            id='partial_delivery_and_limited_paid_waiting',
        ),
        pytest.param(
            ['partial_delivery'],
            ['partial_delivery'],
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={
                        '__default__': ['partial_delivery'],
                    },
                ),
            ],
            id='partial_delivery_allowed_default',
        ),
    ),
)
async def test_accept(
        taxi_cargo_claims,
        state_controller,
        get_create_request_v2,
        get_default_headers,
        claim_features,
        expected_features,
):
    if claim_features:
        state_controller.use_create_version('v2')
        create_request = copy.deepcopy(get_create_request_v2())
        create_request['features'] = [{'id': f} for f in claim_features]
        state_controller.handlers().create.request = create_request

    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/accept',
        params={'claim_id': claim_id},
        json={'version': 1},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_id,
        'status': 'accepted',
        'version': 1,
        'user_request_revision': '1',
        'skip_client_notify': False,
    }
    claim = await utils_v2.get_claim(claim_id, taxi_cargo_claims)
    if expected_features:
        assert (
            sorted(claim['features'], key=lambda feature: feature['id'])
            == sorted(
                [{'id': f} for f in expected_features],
                key=lambda feature: feature['id'],
            )
        )
    else:
        assert claim['features'] == []
