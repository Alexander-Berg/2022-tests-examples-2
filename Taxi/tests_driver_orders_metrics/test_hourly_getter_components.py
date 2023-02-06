import datetime

import psycopg2
import pytest


GETTER_CONFIG = {
    'batch_size': 1024,
    'enabled': True,
    'pg_timeout': 1000,
    'work_interval': 1,
}


@pytest.mark.now('2019-12-30T03:05:00+00')
@pytest.mark.config(DRIVER_ORDERS_METRICS_DRIVER_METRICS_GETTER=GETTER_CONFIG)
async def test_driver_getter_component(
        pgsql,
        mockserver,
        taxi_driver_orders_metrics,
        testpoint,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/atlas/v1/parks/drivers/orders/metrics')
    def mock_atlas(request):
        return {
            'drivers': [
                {
                    'park_id': 'park1',
                    'driver_id': 'driver1',
                    'metrics': [
                        {'name': 'metric1', 'value': 1},
                        {'name': 'metric2', 'value': 2},
                    ],
                },
                {
                    'park_id': 'park2',
                    'driver_id': 'driver2',
                    'metrics': [{'name': 'metric3', 'value': 3}],
                },
            ],
        }

    await taxi_driver_orders_metrics.run_task(
        'driver-metrics-getter-component',
    )

    assert mock_atlas.times_called > 0

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(
        'SELECT * FROM metrics.driver_hourly_metrics'
        ' ORDER BY park_id, driver_id, date_at;',
    )
    result = list(cursor.fetchall())

    assert len(result) == 8, result
    assert result == [
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                4,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                5,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                6,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                4,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                5,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                6,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
    ]


@pytest.mark.now('2019-12-30T03:05:00+00')
@pytest.mark.config(
    DRIVER_ORDERS_METRICS_DRIVER_METRICS_GETTER=GETTER_CONFIG,
    DRIVER_ORDERS_METRICS_ATLAS=True,
)
async def test_driver_getter_component_v2(
        pgsql,
        mockserver,
        taxi_driver_orders_metrics,
        testpoint,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/atlas-backend/v1/parks/drivers/orders/metrics')
    def mock_atlas(request):
        return {
            'drivers': [
                {
                    'park_id': 'park1',
                    'driver_id': 'driver1',
                    'metrics': [
                        {'name': 'metric1', 'value': 1},
                        {'name': 'metric2', 'value': 2},
                    ],
                    'tz': 3,
                },
                {
                    'park_id': 'park2',
                    'driver_id': 'driver2',
                    'metrics': [{'name': 'metric3', 'value': 3}],
                    'tz': 3,
                },
            ],
            'last_load_at': '2019-12-30T03:05:00+00',
        }

    await taxi_driver_orders_metrics.run_task(
        'driver-metrics-getter-component',
    )

    assert mock_atlas.times_called > 0

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(
        'SELECT * FROM metrics.driver_hourly_metrics'
        ' ORDER BY park_id, driver_id, date_at;',
    )
    result = list(cursor.fetchall())

    assert len(result) == 8, result
    assert result == [
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                4,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                5,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park1',
            'driver1',
            datetime.datetime(
                2019,
                12,
                30,
                6,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric1': 1, 'metric2': 2},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                4,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                5,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
        (
            'park2',
            'driver2',
            datetime.datetime(
                2019,
                12,
                30,
                6,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
    ]


@pytest.mark.now('2019-12-30T03:05:00+00')
@pytest.mark.config(
    DRIVER_ORDERS_METRICS_DRIVER_METRICS_GETTER=GETTER_CONFIG,
    DRIVER_ORDERS_METRICS_ATLAS=False,
)
async def test_park_getter_component(
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
                    'driver_id': 'driver1',
                    'metrics': [
                        {'name': 'metric1', 'value': 1},
                        {'name': 'metric2', 'value': 2},
                    ],
                },
                {
                    'park_id': 'park2',
                    'driver_id': 'driver2',
                    'metrics': [{'name': 'metric3', 'value': 3}],
                },
            ],
        }

    await taxi_driver_orders_metrics.run_task('park-metrics-getter-component')

    assert mock_atlas.times_called > 0

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(
        'SELECT * FROM metrics.park_hourly_metrics ORDER BY park_id, date_at;',
    )
    result = list(cursor.fetchall())

    assert len(result) == 8, result
    assert result == [
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                30,
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
                30,
                4,
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
                30,
                5,
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
                30,
                6,
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
                30,
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
                30,
                4,
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
                30,
                5,
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
                30,
                6,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
    ]


@pytest.mark.now('2019-12-30T03:05:00+00')
@pytest.mark.config(
    DRIVER_ORDERS_METRICS_DRIVER_METRICS_GETTER=GETTER_CONFIG,
    DRIVER_ORDERS_METRICS_ATLAS=True,
)
async def test_park_getter_component_v2(
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
                    'driver_id': 'driver1',
                    'metrics': [
                        {'name': 'metric1', 'value': 1},
                        {'name': 'metric2', 'value': 2},
                    ],
                    'tz': 3,
                },
                {
                    'park_id': 'park2',
                    'driver_id': 'driver2',
                    'metrics': [{'name': 'metric3', 'value': 3}],
                    'tz': 3,
                },
            ],
            'last_load_at': '2019-12-30T03:05:00+00',
        }

    await taxi_driver_orders_metrics.run_task('park-metrics-getter-component')

    assert mock_atlas.times_called > 0

    cursor = pgsql['driver_orders_metrics'].cursor()
    cursor.execute(
        'SELECT * FROM metrics.park_hourly_metrics ORDER BY park_id, date_at;',
    )
    result = list(cursor.fetchall())

    assert len(result) == 8, result
    assert result == [
        (
            'park1',
            datetime.datetime(
                2019,
                12,
                30,
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
                30,
                4,
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
                30,
                5,
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
                30,
                6,
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
                30,
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
                30,
                4,
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
                30,
                5,
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
                30,
                6,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            {'metric3': 3},
        ),
    ]
