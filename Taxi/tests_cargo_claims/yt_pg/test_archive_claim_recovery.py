import os

import pytest


def clear_and_compare(full, expected):
    # audit/log triggers on recovery
    assert len(full['claim_audit']) == 2
    assert len(full['claim_segment_points_change_log']) == 2
    del full['claim_audit']
    del full['claim_segment_points_change_log']
    del expected['claim_audit']
    del expected['claim_segment_points_change_log']

    # update time triggers on recovery
    del full['claim_estimating_results']['updated_ts']
    del full['claims']['last_status_change_ts']
    del full['claims']['updated_ts']
    del full['claim_segments'][0]['resolved_at']

    del expected['claim_estimating_results']['updated_ts']
    del expected['claims']['last_status_change_ts']
    del expected['claims']['updated_ts']
    del expected['claim_segments'][0]['resolved_at']

    assert full == expected


@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.now('2021-01-07T00:00:04+00:00')
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
            'ttl-days': 9999,
        },
    },
)
async def test_full_after_recovery(taxi_cargo_claims, load_json):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/recovery',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200

    response = await taxi_cargo_claims.get(
        '/v1/test/claim/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200
    clear_and_compare(response.json(), load_json('expected_response.json'))
