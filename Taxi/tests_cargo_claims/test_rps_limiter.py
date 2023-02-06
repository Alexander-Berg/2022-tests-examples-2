import pytest


@pytest.mark.config(
    CARGO_CLAIMS_RPS_LIMITER_QUOTAS={
        '/api/integration/v1/claims/info/post': {
            '__default__': {'limit': 2, 'burst': 1},
        },
    },
)
async def test_rps_limiter(
        taxi_cargo_claims, rps_limiter, state_controller, get_default_headers,
):
    rps_limiter.set_budget('/api/integration/v1/claims/info/post:default', 2)
    claim_info = await state_controller.apply(target_status='new')

    for expected_code in [200] * 2 + [429]:
        response = await taxi_cargo_claims.post(
            f'/api/integration/v1/claims/info?claim_id={claim_info.claim_id}',
            headers=get_default_headers(),
        )
        assert response.status_code == expected_code


async def test_rps_limiter_no_quotas(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(target_status='new')

    for expected_code in [200] * 10:
        response = await taxi_cargo_claims.post(
            f'/api/integration/v1/claims/info?claim_id={claim_info.claim_id}',
            headers=get_default_headers(),
        )
        assert response.status_code == expected_code


@pytest.mark.config(
    CARGO_CLAIMS_RPS_LIMITER_QUOTAS={
        '/api/integration/v1/claims/info/post': {
            '__default__': {'limit': 2, 'burst': 1},
            'some_quota': {'limit': 4, 'burst': 1},
        },
    },
    CARGO_CLAIMS_RPS_LIMITER_MAPPING={
        '01234567890123456789012345678912': 'some_quota',
        '__default__': 'default',
    },
)
async def test_rps_limiter_personal_quota(
        taxi_cargo_claims, rps_limiter, state_controller, get_default_headers,
):
    rps_limiter.set_budget('/api/integration/v1/claims/info/post:default', 2)
    rps_limiter.set_budget(
        '/api/integration/v1/claims/info/post:some_quota', 4,
    )
    claim_info = await state_controller.apply(target_status='new')

    for expected_code in [400] * 2 + [429]:
        response = await taxi_cargo_claims.post(
            f'/api/integration/v1/claims/info?claim_id={claim_info.claim_id}',
            headers=get_default_headers('someothercorpsomeothercorpaaaaaa'),
        )
        assert response.status_code == expected_code

    for expected_code in [200] * 4 + [429]:
        response = await taxi_cargo_claims.post(
            f'/api/integration/v1/claims/info?claim_id={claim_info.claim_id}',
            headers=get_default_headers(),
        )
        assert response.status_code == expected_code
