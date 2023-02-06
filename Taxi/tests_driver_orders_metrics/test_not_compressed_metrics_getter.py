import datetime

import psycopg2
import pytest


CONFIG = {
    'batch_size': 1,
    'enabled': True,
    'pg_timeout': 1000,
    'work_interval': 1,
}


@pytest.mark.pgsql('driver_orders_metrics', files=['park_metrics.sql'])
@pytest.mark.config(DRIVER_ORDERS_METRICS_NOT_COMPRESSED_METRICS_GETTER=CONFIG)
@pytest.mark.now('2019-12-27T12:00:00+0000')
async def test_get_not_compressed_metrics(
        pgsql,
        mockserver,
        taxi_driver_orders_metrics,
        testpoint,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/atlas/v1/parks/orders/metrics')
    def mock_atlas(request):
        return {
            'parks': [
                {
                    'park_id': 'park1',
                    'metrics': [
                        {'name': 'metric1', 'value': 1},
                        {'name': 'metric2', 'value': 2},
                    ],
                },
                {
                    'park_id': 'park2',
                    'metrics': [{'name': 'metric3', 'value': 3}],
                },
            ],
        }

    await taxi_driver_orders_metrics.run_task(
        'not-compressed-metrics-daily-getter-component',
    )

    assert mock_atlas.times_called > 0

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(
        'SELECT * FROM metrics.park_daily_metrics ORDER BY park_id, date_at;',
    )
    result = list(cursor.fetchall())

    assert len(result) == 6, result
    assert result == [
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                26,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2, 'successful': 4},
        ),
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                28,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park2',
            datetime.datetime(
                2019,
                12,
                26,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            datetime.datetime(
                2019,
                12,
                28,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
    ]


@pytest.mark.pgsql('driver_orders_metrics', files=['park_metrics.sql'])
@pytest.mark.config(
    DRIVER_ORDERS_METRICS_NOT_COMPRESSED_METRICS_GETTER=CONFIG,
    DRIVER_ORDERS_METRICS_ATLAS=True,
)
@pytest.mark.now('2019-12-27T12:00:00+0000')
async def test_get_not_compressed_metrics_v2(
        pgsql,
        mockserver,
        taxi_driver_orders_metrics,
        testpoint,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/atlas-backend/v1/parks/orders/metrics')
    def mock_atlas(request):
        return {
            'parks': [
                {
                    'park_id': 'park1',
                    'metrics': [
                        {'name': 'metric1', 'value': 1},
                        {'name': 'metric2', 'value': 2},
                    ],
                    'tz': 3,
                },
                {
                    'park_id': 'park2',
                    'metrics': [{'name': 'metric3', 'value': 3}],
                    'tz': 3,
                },
            ],
            'last_load_at': '2019-12-30T03:05:00+00',
        }

    await taxi_driver_orders_metrics.run_task(
        'not-compressed-metrics-daily-getter-component',
    )

    assert mock_atlas.times_called > 0

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(
        'SELECT * FROM metrics.park_daily_metrics ORDER BY park_id, date_at;',
    )
    result = list(cursor.fetchall())

    assert len(result) == 6, result
    assert result == [
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                26,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2, 'successful': 4},
        ),
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                28,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park2',
            datetime.datetime(
                2019,
                12,
                26,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            datetime.datetime(
                2019,
                12,
                27,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            datetime.datetime(
                2019,
                12,
                28,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
    ]
