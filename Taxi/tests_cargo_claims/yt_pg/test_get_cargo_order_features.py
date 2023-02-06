import os

import pytest


@pytest.mark.parametrize(
    '',
    (
        pytest.param(
            marks=pytest.mark.pgsql(
                'cargo_claims', files=['pg_raw_denorm.sql'],
            ),
            id='pg only',
        ),
        pytest.param(
            marks=[
                pytest.mark.xfail(
                    os.getenv('IS_TEAMCITY'),
                    strict=False,
                    reason='some problems in CI with YT',
                ),
                pytest.mark.yt(
                    dyn_table_data=['yt_raw_denorm.yaml', 'yt_index.yaml'],
                ),
            ],
            id='yt only',
        ),
        pytest.param(
            marks=[
                pytest.mark.xfail(
                    os.getenv('IS_TEAMCITY'),
                    strict=False,
                    reason='some problems in CI with YT',
                ),
                pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql']),
                pytest.mark.yt(
                    dyn_table_data=['yt_raw_denorm.yaml', 'yt_index.yaml'],
                ),
            ],
            id='yt pg',
        ),
    ),
)
@pytest.mark.usefixtures('yt_apply')
async def test_cargo_order_features(taxi_cargo_claims, load_json):
    response = await taxi_cargo_claims.post(
        '/v1/test/cargo-order/features',
        json={
            'cargo_order_ids': [
                '25705ef6-e3e7-46fc-8126-863fc4e88ff6',
                '2901eaff-9a7a-4799-9cdd-e6a8d0a727ad',
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()['features'] == [
        {
            'cargo_order_id': '25705ef6-e3e7-46fc-8126-863fc4e88ff6',
            'claim_id': '9756ae927d7b42dc9bbdcbb832924343',
            'features': load_json('expected_response.json')['claim_features'],
        },
    ]
