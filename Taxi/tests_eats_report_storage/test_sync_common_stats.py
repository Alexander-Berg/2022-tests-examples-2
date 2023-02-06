import datetime
import decimal

import pytest

SYNC_CONFIG = {
    'enabled': True,
    'start_sync_period': '00:00',
    'end_sync_period': '23:59',
    'min_sync_interval': 0,
    'period': 3600,
    'margin_time': 1,
    'storage_time': 4,
    'green_plum': {
        'chunk_size': 2,
        'table_name': 'eda_cdm_supply.agg_place_metric',
        'timeouts': {'statement_timeout': 250, 'network_timeout': 500},
    },
}


def check_synchronization_time(pgsql, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-common-stats\';',
    )
    assert date - cursor.fetchone()[0] < datetime.timedelta(minutes=1)


def check_data_count(pgsql, count):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute('SELECT * FROM eats_report_storage.agg_place_metric;')
    stats = cursor.fetchall()
    assert len(stats) == count


def check_sync_stats(pgsql, data):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT order_per_place_avg '
        'FROM eats_report_storage.agg_place_metric '
        'ORDER BY order_per_place_avg;',
    )
    stats = cursor.fetchall()
    assert stats == [
        (decimal.Decimal(str(item)) if item else None,) for item in data
    ]


def check_timezone_is_utc(pgsql):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT utc_period_start_dttm '
        'FROM eats_report_storage.agg_place_metric '
        'LIMIT 1;',
    )
    import pytz
    tz_em = pytz.timezone('Europe/Moscow')
    assert cursor.fetchone()[0] == datetime.datetime(
        2021, 9, 9, 3, 0, 0, 0,
    ).astimezone(tz_em)


@pytest.mark.now('2021-06-30T00:03:30Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_COMMON_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp',
    files=('eats_report_storage_gp_sync_periodic.sql',),
)
async def test_sync_common_stats(taxi_eats_report_storage, pgsql, mocked_time):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-common-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [122.6, None])


@pytest.mark.now('2021-06-30T00:03:30Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_COMMON_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp',
    files=('eats_report_storage_clear_old_data_common_stats.sql',),
)
async def test_clear_old_data(taxi_eats_report_storage, pgsql, mocked_time):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-common-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [122.6, 123.6])


@pytest.mark.now('2021-09-09T03:00:00Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_COMMON_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp', files=('eats_report_storage_gp_timezone.sql',),
)
async def test_timezone_is_utc(taxi_eats_report_storage, pgsql):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-common-stats-periodic',
    )

    check_timezone_is_utc(pgsql)
