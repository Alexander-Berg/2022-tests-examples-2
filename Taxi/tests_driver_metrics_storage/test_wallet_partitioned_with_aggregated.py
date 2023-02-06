import pytest


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_AGGREGATOR_SETTINGS={
        'is_aggregation_enabled': True,
        'is_selection_enabled': True,
        'fetch_partitions_period_sec': 1,
        'aggregators': {
            'data.logs_64_loyalty_hourly_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '15min',
            },
            'data.logs_64_loyalty_daily_aggregated': {
                'initial_partition_offset': '1hour',
                'data_aggregation_period': '2hours',
            },
        },
    },
)
@pytest.mark.parametrize(
    'is_aggregation_enabled, is_selection_enabled, expected_value',
    (
        pytest.param(False, False, 2160),
        pytest.param(True, False, 2160),
        # expected_value is differ, due to aggregated value is increased
        # by 3 (see +1 and +2 in test.sql) to be sure it is actually selects
        # from aggregated tables.
        pytest.param(True, True, 2163),
    ),
)
@pytest.mark.now('2021-12-25T18:00:03+0000')
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_wallet_with_aggregated(
        taxi_driver_metrics_storage,
        taxi_config,
        pgsql,
        clear_range_partitions,
        is_aggregation_enabled,
        is_selection_enabled,
        expected_value,
):
    taxi_config.set_values(
        {
            'DRIVER_METRICS_STORAGE_AGGREGATOR_SETTINGS': {
                'is_aggregation_enabled': is_aggregation_enabled,
                'is_selection_enabled': is_selection_enabled,
                'fetch_partitions_period_sec': 1,
                'aggregators': {
                    'data.logs_64_loyalty_hourly_aggregated': {
                        'initial_partition_offset': '1hour',
                        'data_aggregation_period': '15min',
                    },
                    'data.logs_64_loyalty_daily_aggregated': {
                        'initial_partition_offset': '1hour',
                        'data_aggregation_period': '2hours',
                    },
                },
            },
        },
    )
    await taxi_driver_metrics_storage.invalidate_caches()

    await taxi_driver_metrics_storage.run_periodic_task(
        'fetcher::dist-loyalty-aggregator',
    )
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2021-12-22T18:00:03+0000',
            'ts_to': '2021-12-25T18:00:03+0000',
            'udids': ['000000000000000000000001', '000000000000000000000002'],
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'count': 480,
            'value': expected_value,
            'last_ts': '2021-12-25T17:57:03+00:00',
            'udid': '000000000000000000000001',
        },
        {'count': 0, 'value': 0, 'udid': '000000000000000000000002'},
    ]
