import os

import pytest


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.usefixtures('yt_apply')
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
async def test_yt_denorm_read(taxi_cargo_claims, load_json):
    response = await taxi_cargo_claims.get(
        '/v1/test/claim/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_pg_denorm_read(taxi_cargo_claims, load_json):
    response = await taxi_cargo_claims.get(
        '/v1/test/claim/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
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
async def test_yt_cut_denorm_read(taxi_cargo_claims, load_json, cut_response):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/cut',
        json={'uuids': ['9756ae927d7b42dc9bbdcbb832924343']},
    )
    assert response.status == 200
    assert response.json()['claims'] == [
        cut_response(load_json('expected_response.json')),
    ]


@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_pg_cut_denorm_read(taxi_cargo_claims, load_json, cut_response):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/cut',
        json={'uuids': ['9756ae927d7b42dc9bbdcbb832924343']},
    )
    assert response.status == 200
    assert response.json()['claims'] == [
        cut_response(load_json('expected_response.json')),
    ]
