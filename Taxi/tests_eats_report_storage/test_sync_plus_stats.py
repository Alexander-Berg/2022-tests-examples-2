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
        'timeouts': {'statement_timeout': 250, 'network_timeout': 500},
        'table_name': 'eda_cdm_supply.agg_place_plus_metric',
    },
}


def check_synchronization_time(pgsql, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-plus-stats\';',
    )
    assert date - cursor.fetchone()[0] < datetime.timedelta(minutes=1)


def check_data_count(pgsql, count):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute('SELECT * FROM eats_report_storage.place_plus_metric;')
    stats = cursor.fetchall()
    assert len(stats) == count


def check_sync_stats(pgsql, data):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT user_w_plus_gmv_lcy '
        'FROM eats_report_storage.place_plus_metric '
        'ORDER BY user_w_plus_gmv_lcy;',
    )
    stats = cursor.fetchall()
    assert stats == [(decimal.Decimal(str(item)),) for item in data]


@pytest.mark.now('2021-06-30T00:03:29Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_PLUS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp', files=('eats_report_storage_gp_3days.sql',),
)
@pytest.mark.xfail(reason='flaky test, will be fixed in EDAPARTNERS-181')
async def test_sync_plus_stats_dont_sync_too_old_data(
        taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-plus-stats-periodic',
    )
    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [0.1, 1.1])


@pytest.mark.now('2021-06-30T00:03:29Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_PLUS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp',
    files=('eats_report_storage_gp_continue_update.sql',),
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_continue_update.sql',),
)
async def test_sync_plus_continue_update(
        taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-plus-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 7)
    check_sync_stats(pgsql, [0.1, 1.1, 2.1, 3.1, 4.1, 5.1, 10.1])


@pytest.mark.now('2021-06-30T00:03:29Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_PLUS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_clear_old_data.sql',),
)
async def test_clear_old_data(taxi_eats_report_storage, pgsql, mocked_time):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-plus-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [0.1, 1.1])
