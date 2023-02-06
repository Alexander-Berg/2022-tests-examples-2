import datetime

import pytest

SYNC_CONFIG = {
    'enabled': True,
    'start_sync_period': '00:00',
    'end_sync_period': '23:59',
    'min_sync_interval': 0,
    'period': 3600,
    'margin_time': 0,
    'storage_time': 4,
    'green_plum': {
        'chunk_size': 2,
        'timeouts': {'statement_timeout': 250, 'network_timeout': 500},
        'table_name': 'snb_eda.rad_dm_client_metric',
    },
}


def check_synchronization_time(pgsql, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-clients-stats\';',
    )
    assert date - cursor.fetchone()[0] < datetime.timedelta(minutes=1)


def check_data_count(pgsql, count):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute('SELECT * FROM eats_report_storage.place_clients_metric;')
    stats = cursor.fetchall()
    assert len(stats) == count


def check_sync_stats(pgsql, data):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT users_with_1_order_cnt '
        'FROM eats_report_storage.place_clients_metric '
        'ORDER BY users_with_1_order_cnt;',
    )
    stats = cursor.fetchall()
    assert stats == [(item,) for item in data]


@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_CLIENTS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp', files=('eats_report_storage_gp_3days.sql',),
)
@pytest.mark.now('2021-06-30T00:03:31Z')
async def test_sync_clients_stats_dont_sync_too_old_data(
        taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-clients-stats-periodic',
    )
    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [1, 11])


@pytest.mark.now('2021-06-30T00:03:30Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_CLIENTS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp',
    files=('eats_report_storage_gp_continue_update.sql',),
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_continue_update.sql',),
)
async def test_sync_clients_continue_update(
        taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-clients-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 6)
    check_sync_stats(pgsql, [1, 11, 21, 41, 51, 61])


@pytest.mark.now('2021-06-30T00:03:28Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_CLIENTS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_clear_old_data.sql',),
)
async def test_clear_old_data(taxi_eats_report_storage, pgsql, mocked_time):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-clients-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [1, 11])
