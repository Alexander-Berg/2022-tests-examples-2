import datetime
import json

import pytest


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_AGGREGATOR_SETTINGS={
        'is_aggregation_enabled': True,
        'is_selection_enabled': False,
        'fetch_partitions_period_sec': 1,
        'aggregators': {
            'data.logs_64_loyalty_hourly_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '15min',
            },
            'data.logs_64_loyalty_daily_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '1hour',
            },
        },
    },
)
@pytest.mark.now('2021-12-22T15:00:03+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_wallet_aggregators_stats(
        taxi_driver_metrics_storage,
        metrics_snapshot,
        clear_range_partitions,
        testpoint,
        mocked_time,
):
    await taxi_driver_metrics_storage.invalidate_caches()

    @testpoint('periodic::dist-loyalty-aggregator')
    def testpoint_callback(data):
        pass

    # Do not check statistics first time to skip artefacts after previous tests
    await taxi_driver_metrics_storage.run_task('dist-loyalty-aggregator')
    await testpoint_callback.wait_call()

    now = mocked_time.now()
    mocked_time.set(now + datetime.timedelta(minutes=1))
    await taxi_driver_metrics_storage.invalidate_caches()
    await metrics_snapshot.take_snapshot()

    metrics = await metrics_snapshot.get_metrics_diff()
    assert json.loads(str(metrics['dist-loyalty-aggregator-stats'])) == {}

    now = mocked_time.now()
    mocked_time.set(now + datetime.timedelta(minutes=16))
    await taxi_driver_metrics_storage.invalidate_caches()
    await metrics_snapshot.take_snapshot()

    await taxi_driver_metrics_storage.run_task('dist-loyalty-aggregator')
    await testpoint_callback.wait_call()

    metrics = await metrics_snapshot.get_metrics_diff()
    # Value `2 * 60 + 3` because ignore false-positive try of first filling
    hourly = metrics['dist-loyalty-aggregator-stats'][
        'data.logs_64_loyalty_hourly_aggregated'
    ]
    assert hourly['partition_infilling_delay'].get_diff() == 2 * 60
    assert hourly['aggregated_records_count'].get_diff() == 2

    now = mocked_time.now()
    mocked_time.set(now + datetime.timedelta(minutes=30))
    await taxi_driver_metrics_storage.invalidate_caches()
    await metrics_snapshot.take_snapshot()

    await taxi_driver_metrics_storage.run_task('dist-loyalty-aggregator')
    await testpoint_callback.wait_call()

    metrics = await metrics_snapshot.get_metrics_diff()
    hourly = metrics['dist-loyalty-aggregator-stats'][
        'data.logs_64_loyalty_hourly_aggregated'
    ]
    assert hourly['partition_infilling_delay'].get_diff() == 15 * 60
    assert hourly['aggregated_records_count'].get_diff() == 1
