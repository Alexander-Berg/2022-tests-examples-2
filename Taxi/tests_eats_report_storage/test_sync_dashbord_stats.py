import datetime
import decimal

import pytest

SYNC_CONFIG = {
    'enabled': True,
    'start_sync_period': '00:00',
    'end_sync_period': '23:59',
    'min_sync_interval': 0,
    'period': 3600,
    'green_plum': {
        'chunk_size': 2,
        'timeouts': {'statement_timeout': 250, 'network_timeout': 500},
        'rad_quality_table_name': 'snb_eda.rad_quality',
        'rad_suggests_table_name': 'snb_eda.rad_suggests',
    },
}

SUGGEST_RESULT = [
    (1, 1.1, 'cancels'),
    (1, 2.2, 'pict_share'),
    (2, 4.4, 'pict_share'),
]

QUALITY_RESULT = [(1, 2977.167), (2, 2.2), (4, 4.4)]


def check_synchronization_time(pgsql, date, sync_name):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-' + sync_name + '-stats\';',
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


@pytest.mark.now('2021-06-30T00:03:30Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_DASHBORD_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp', files=('eats_report_storage_gp.sql',),
)
@pytest.mark.pgsql('eats_report_storage', files=('eats_report_storage.sql',))
async def test_sync_dashbord_stats(
        taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-dashbord-stats-periodic',
    )
    check_synchronization_time(pgsql, mocked_time.now(), 'dashbord_quality')
    check_synchronization_time(pgsql, mocked_time.now(), 'dashbord_suggests')
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT place_id, prioriy::float, suggest '
        'FROM eats_report_storage.rad_suggests '
        'ORDER BY place_id, suggest, prioriy;',
    )
    assert cursor.fetchall() == SUGGEST_RESULT
    cursor.execute(
        'SELECT place_id, rating::float '
        'FROM eats_report_storage.rad_quality '
        'ORDER BY place_id, rating;',
    )
    assert cursor.fetchall() == QUALITY_RESULT
