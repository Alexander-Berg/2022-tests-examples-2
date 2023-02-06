import datetime

import psycopg2
import pytest


CONFIG = {
    'park_component': {
        'enable': False,
        'hour_metrics_select_bulk_size': 5,
        'hours_backward_not_to_compress': 48,
        'fleet_parks_bulk_size': 3,
        'daily_metrics_select_bulk_size': 2,
        'work_interval_seconds': 1,
        'pg_timeout_seconds': 1,
    },
    'driver_component': {
        'enable': True,
        'hour_metrics_select_bulk_size': 1,
        'hours_backward_not_to_compress': 48,
        'fleet_parks_bulk_size': 1,
        'daily_metrics_select_bulk_size': 1,
        'work_interval_seconds': 1,
        'pg_timeout_seconds': 1,
    },
}


@pytest.mark.now('2019-12-30T03:05:00+00')
@pytest.mark.pgsql(
    'driver_orders_metrics', files=['driver_metrics_test_1.sql'],
)
@pytest.mark.config(DRIVER_ORDERS_METRICS_METRICS_COMPRESSION=CONFIG)
async def test_compression_1(
        pgsql, taxi_driver_orders_metrics, testpoint, mock_fleet_parks_list,
):
    @testpoint('driver-hourly-metrics-compression-component-end')
    def compression_done(data):
        pass

    await taxi_driver_orders_metrics.enable_testpoints(
        no_auto_cache_cleanup=False,
    )

    await compression_done.wait_call()

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute('SELECT * FROM metrics.driver_daily_metrics;')
    result = list(cursor.fetchall())

    assert len(result) == 4, result
    assert result == [
        (
            'park1',
            'driver2',
            datetime.datetime(
                2019,
                12,
                28,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 322},
        ),
        (
            'park2',
            'driver1',
            datetime.datetime(
                2019,
                12,
                31,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 223},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {
                'client_cancelled': 1,
                'driver_cancelled': 12,
                'successful': 13,
                'successful_econom': 1,
            },
        ),
        (
            'park2',
            'driver1',
            datetime.datetime(
                2019,
                12,
                12,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 555},
        ),
    ]

    cursor.execute('SELECT * FROM metrics.driver_hourly_metrics;')
    result = list(cursor.fetchall())

    assert len(result) == 1, result
    assert result == [
        (
            'park1',
            'driver2',
            datetime.datetime(
                2025,
                3,
                28,
                16,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 322},
        ),
    ]


@pytest.mark.now('2019-12-31T03:05:00+00')
@pytest.mark.pgsql(
    'driver_orders_metrics', files=['driver_metrics_test_2.sql'],
)
@pytest.mark.config(DRIVER_ORDERS_METRICS_METRICS_COMPRESSION=CONFIG)
async def test_compression_2(
        pgsql, taxi_driver_orders_metrics, testpoint, mock_fleet_parks_list,
):
    @testpoint('driver-hourly-metrics-compression-component-end')
    def compression_done(data):
        pass

    await taxi_driver_orders_metrics.enable_testpoints(
        no_auto_cache_cleanup=False,
    )

    await compression_done.wait_call()

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute('SELECT * FROM metrics.driver_daily_metrics;')
    result = list(cursor.fetchall())
    print('Select len: ', len(result))
    print('Select result: ', result)

    assert len(result) == 3, result
    assert result == [
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                26,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'driver_cancelled': 26},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {
                'client_cancelled': 3,
                'driver_cancelled': 3,
                'successful': 3,
                'successful_econom': 3,
            },
        ),
        (
            'unknown_park',
            'driver1',
            datetime.datetime(
                2018,
                3,
                28,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 123},
        ),
    ]

    cursor.execute('SELECT * FROM metrics.driver_hourly_metrics;')
    result = list(cursor.fetchall())

    assert not result


@pytest.mark.now('2019-12-31T03:05:00+00')
@pytest.mark.pgsql(
    'driver_orders_metrics', files=['driver_metrics_test_park_tz.sql'],
)
@pytest.mark.config(DRIVER_ORDERS_METRICS_METRICS_COMPRESSION=CONFIG)
async def test_park_tz_offset(
        pgsql, taxi_driver_orders_metrics, testpoint, mock_fleet_parks_list,
):
    @testpoint('driver-hourly-metrics-compression-component-end')
    def compression_done(data):
        pass

    await taxi_driver_orders_metrics.enable_testpoints(
        no_auto_cache_cleanup=False,
    )

    await compression_done.wait_call()

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute('SELECT * FROM metrics.driver_daily_metrics;')
    result = list(cursor.fetchall())

    assert len(result) == 2, result
    assert result == [
        (
            'park3',
            'driver1',
            datetime.datetime(
                2019,
                12,
                25,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 25},
        ),
        (
            'park3',
            'driver1',
            datetime.datetime(
                2019,
                12,
                26,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'successful': 26},
        ),
    ]

    cursor.execute('SELECT * FROM metrics.driver_hourly_metrics;')
    result = list(cursor.fetchall())

    assert not result
