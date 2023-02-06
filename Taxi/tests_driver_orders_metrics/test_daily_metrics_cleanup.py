import datetime

import psycopg2
import pytest


def get_pg_rows(pgsql, query):
    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(query)
    return list(cursor.fetchall())


@pytest.mark.now('2020-03-17T10:30:00+00')
async def test_ok(taxi_driver_orders_metrics, testpoint, taxi_config, pgsql):
    @testpoint('daily-metrics-cleanup-component-finished')
    def finished(data):
        pass

    taxi_config.set_values(
        {
            'DRIVER_ORDERS_METRICS_DAILY_METRICS_CLEANUP': {
                'enabled': True,
                'work_interval': 1,
                'metrics_ttl': 366,
                'max_deleted_metrics': 2,
                'pg_timeout': 500,
            },
        },
    )

    await taxi_driver_orders_metrics.enable_testpoints()
    await finished.wait_call()

    query = 'SELECT park_id, date_at FROM metrics.park_daily_metrics'
    result = get_pg_rows(pgsql, query)

    assert len(result) == 1
    assert result == [
        (
            'park_id_1',
            datetime.datetime(
                2019,
                3,
                18,
                0,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]

    query = (
        'SELECT park_id, driver_id, date_at FROM metrics.driver_daily_metrics '
        'ORDER BY date_at'
    )
    result = get_pg_rows(pgsql, query)

    assert len(result) == 2
    assert result == [
        (
            'park_id_1',
            'driver_id_1',
            datetime.datetime(
                2019,
                3,
                17,
                0,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            'park_id_1',
            'driver_id_1',
            datetime.datetime(
                2019,
                3,
                18,
                0,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]
