# pylint: disable=C0103
import re

import pytest

from atlas_backend.generated.cron import run_cron

WEEK = 7 * 24 * 60 * 60  # seconds
PIVOT_LENGTH = 15 * 60  # seconds


@pytest.mark.config(
    ATLAS_GRANULARITY_MAPPING={'plot': {'7': None, '10': 60}},
    ATLAS_BACKEND_ANOMALY_LOSS_METRICS={'all': 'anomaly_trips_taxi_all'},
    ATLAS_BACKEND_ANOMALY_LEVEL_METRICS={
        'all': {
            'cancel_metrics': ['anomaly_trips_taxi_all'],
            'total_metrics': ['anomaly_trips_taxi_all'],
            'level_threshold': 15,
        },
    },
    ATLAS_BACKEND_SERVICE_CRON_CONTROL={
        'atlas_backend': {
            'anomalies.calculate_losses': {'run_permission': True},
        },
    },
)
async def test_anomaly_calculate_losses(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    START_TS = 1593181500
    END_TS = 1593186539
    BASE_VALUE = 2000

    def _ch_data():
        def _inner(start, end):
            shift = _inner.calls // 3

            result = [(('atlas_ts', 'UInt64'), ('value', 'UInt64'))]
            if _inner.calls == 1:  # anomaly region has halved value
                for timestamp in range(start, end, 60):
                    result.append((timestamp, BASE_VALUE / (shift + 5) / 2))
            else:
                for timestamp in range(start, end, 60):
                    result.append((timestamp, BASE_VALUE / (shift + 5)))

            _inner.calls += 1
            return result

        _inner.calls = 0
        return _inner

    data_generator = _ch_data()

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute(*args, **kwargs):
        start, end = map(
            int,
            re.findall(r'ts_1_min BETWEEN (\d{10}) AND (\d{10})', args[0])[0],
        )

        async def _result():
            for item in data_generator(start, end):
                yield item

        return _result()

    response_before = await web_app_client.get(
        '/api/v1/anomalies/5e00b661954de74d8a6af7c7',
    )
    assert response_before.status == 200
    anomaly_before = await response_before.json()
    assert anomaly_before['losses'].get('orders') is None
    assert anomaly_before['level'] == 'minor'

    await run_cron.main(
        ['atlas_backend.crontasks.anomalies.calculate_losses', '-t', '0'],
    )

    response_after = await web_app_client.get(
        '/api/v1/anomalies/5e00b661954de74d8a6af7c7',
    )
    assert response_after.status == 200
    anomaly_after = await response_after.json()

    expected = (END_TS - START_TS + 59) // 60 * BASE_VALUE / 10
    assert anomaly_after['losses']['orders'] == expected
    assert anomaly_after['level'] == 'major'


@pytest.mark.config(
    ATLAS_BACKEND_SERVICE_CRON_CONTROL={
        'atlas_backend': {
            'anomalies.calculate_losses': {'run_permission': False},
        },
    },
)
async def test_no_run_permission(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    response_before = await web_app_client.get(
        '/api/v1/anomalies/5e00b661954de74d8a6af7c7',
    )
    assert response_before.status == 200
    anomaly_before = await response_before.json()
    assert anomaly_before['losses'].get('orders') is None

    await run_cron.main(
        ['atlas_backend.crontasks.anomalies.calculate_losses', '-t', '0'],
    )

    response_after = await web_app_client.get(
        '/api/v1/anomalies/5e00b661954de74d8a6af7c7',
    )
    assert response_after.status == 200
    anomaly_after = await response_after.json()
    assert anomaly_after['losses'].get('orders') is None
