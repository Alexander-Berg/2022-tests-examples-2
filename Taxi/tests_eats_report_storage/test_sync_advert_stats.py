import datetime

import pytest

SYNC_CONFIG = {
    'enabled': True,
    'start_sync_period': '00:00',
    'end_sync_period': '23:59',
    'min_sync_interval': 0,
    'period': 3600,
    'margin_time': 1,
    'storage_time': 7,
    'yt': {
        'chunk_size': 2,
        'table_name': '//home/eda/restapp/testing/advert_clients/advert_data',
        'timeouts': {'operation_timeout': 500},
    },
}


def check_synchronization_time(pgsql, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-advert-stats\';',
    )
    assert date - cursor.fetchone()[0] < datetime.timedelta(minutes=1)


def check_data_count(pgsql, count):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute('SELECT * FROM eats_report_storage.place_advert_metric;')
    stats = cursor.fetchall()
    assert len(stats) == count


def check_sync_stats(pgsql, data):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT ad_orders '
        'FROM eats_report_storage.place_advert_metric '
        'ORDER BY ad_orders;',
    )
    stats = cursor.fetchall()
    assert stats == [(item,) for item in data]


@pytest.mark.now('2021-09-10T05:01:00Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_ADVERT_STATS=SYNC_CONFIG)
@pytest.mark.yt(
    static_table_data=['yt_old_data.yaml'], schemas=['yt_schema.yaml'],
)
async def test_sync_advert_stats_sync_all_data(
        yt_apply, taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-advert-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 3)
    check_sync_stats(pgsql, [1, 2, 3])


@pytest.mark.now('2021-09-10T04:01:00Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_ADVERT_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_continue_update.sql',),
)
@pytest.mark.yt(
    static_table_data=['yt_update_data.yaml'], schemas=['yt_schema.yaml'],
)
async def test_sync_advert_continue_update(
        yt_apply, taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-advert-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 4)
    check_sync_stats(pgsql, [1, 4, 5, 6])


@pytest.mark.now('2021-09-10T04:00:00Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_ADVERT_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_clear_old_data.sql',),
)
@pytest.mark.yt(
    static_table_data=['yt_empty_data.yaml'], schemas=['yt_schema.yaml'],
)
async def test__sync_advert_clear_old_data(
        yt_apply, taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-advert-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 2)
    check_sync_stats(pgsql, [1, 2])
