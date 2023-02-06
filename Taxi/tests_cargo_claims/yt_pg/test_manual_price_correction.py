import datetime
import os

import pytest


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.now('2020-12-01T00:00:04+00:00')
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
async def test_manual_correction(taxi_cargo_claims, pgsql):
    request = {
        'claim_id': '9756ae927d7b42dc9bbdcbb832924343',
        'source': 'test',
        'sum_to_pay': '123.123',
        'currency': 'RUB',
        'last_known_corrections_count': 11,
        'reason': 'TICKET-123',
        'comment': 'test_comment',
    }

    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 200
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        SELECT updated_ts
        FROM cargo_claims.claims
        WHERE uuid_id='9756ae927d7b42dc9bbdcbb832924343'
        """,
    )
    assert (
        list(cursor)[0][0].replace(tzinfo=None) - datetime.datetime(1970, 1, 1)
    ).total_seconds() > 1612137600  # 2021-02-01 00:00:00
    request['claim_id'] = '123'
    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 404


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.now('2022-01-01T00:00:04+00:00')
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
async def test_too_old_claim_to_recover(
        taxi_cargo_claims, pgsql, taxi_cargo_claims_monitor,
):
    await taxi_cargo_claims.tests_control(reset_metrics=True)
    request = {
        'claim_id': '9756ae927d7b42dc9bbdcbb832924343',
        'source': 'test',
        'sum_to_pay': '123.123',
        'currency': 'RUB',
        'last_known_corrections_count': 11,
        'reason': 'TICKET-123',
        'comment': 'test_comment',
    }

    response = await taxi_cargo_claims.post(
        'v2/claims/manual-price-correction',
        json=request,
        headers={
            'X-Yandex-Login': 'yandex_login',
            'X-Yandex-Uid': 'yandex_uid',
        },
    )
    assert response.status == 400
    assert response.json()['code'] == 'claim_too_old_to_change_price'

    metrics = await taxi_cargo_claims_monitor.get_metric(
        'cargo-claims-claim-change-price',
    )
    assert metrics == {
        'success-count': 0,
        'not-found-claims-count': 0,
        'old-claims-count': 1,
    }
