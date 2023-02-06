import pytest


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
        '/v1/test/claim/redis-full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200

    expected_result = {
        key: value
        for key, value in load_json('expected_response.json').items()
        if key
        in (
            'additional_info',
            'claim_points',
            'claims',
            'claim_segments',
            'points',
            'taxi_performer_info',
            'uuid_id',
        )
    }

    assert response.json() == expected_result
