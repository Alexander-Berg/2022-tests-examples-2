import os

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
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
async def test_integration_info_not_found_in_yt(
        taxi_cargo_claims, get_default_headers, api_version,
):
    response = await taxi_cargo_claims.post(
        f'/api/integration/{api_version}/claims/info',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
        headers=get_default_headers('798838e4b169456eb023595801bbb366'),
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
@pytest.mark.parametrize('api_version', ['v1', 'v2'])
async def test_integration_info_not_found_in_pg(
        taxi_cargo_claims, get_default_headers, api_version,
):
    response = await taxi_cargo_claims.post(
        f'/api/integration/{api_version}/claims/info',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924341'},
        headers=get_default_headers('798838e4b169456eb023595801bbb366'),
    )
    assert response.status == 404


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
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.parametrize(
    'api_version, expected_code', (('v1', 400), ('v2', 404)),
)
async def test_integration_info_yt_pg_bad_client(
        taxi_cargo_claims, get_default_headers, api_version, expected_code,
):
    response = await taxi_cargo_claims.post(
        f'/api/integration/{api_version}/claims/info',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
        headers=get_default_headers('798838e4b169456eb023595801bbb361'),
    )
    assert response.status == expected_code
