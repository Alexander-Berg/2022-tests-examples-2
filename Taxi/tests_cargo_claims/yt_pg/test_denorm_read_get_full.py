import pytest


@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 0,
        },
    },
)
@pytest.mark.usefixtures('yt_apply')
async def test_get_full_not_found_in_yt(
        taxi_cargo_claims, get_default_headers,
):
    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
        headers=get_default_headers(),
    )
    assert response.status == 404


@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 0,
        },
    },
)
async def test_get_full_not_found_in_pg(
        taxi_cargo_claims, get_default_headers,
):
    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924341'},
        headers=get_default_headers('798838e4b169456eb023595801bbb366'),
    )
    assert response.status == 404
