import datetime
import decimal

import pytest

SYNC_CONFIG = {
    'enabled': True,
    'start_sync_period': '00:00',
    'end_sync_period': '23:59',
    'min_sync_interval': 0,
    'period': 3600,
    'margin_time': 0,
    'storage_time': 48,
    'green_plum': {
        'chunk_size': 2,
        'timeouts': {'statement_timeout': 250, 'network_timeout': 500},
        'table_name': 'snb_eda.agg_place_digests',
    },
}


def check_synchronization_time(pgsql, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-digests-stats\';',
    )
    assert date - cursor.fetchone()[0] < datetime.timedelta(minutes=1)


def check_data_count(pgsql, count):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute('SELECT * FROM eats_report_storage.agg_place_digests;')
    stats = cursor.fetchall()
    assert len(stats) == count


def check_sync_stats(pgsql, data):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT '
        ' place_id, '
        ' period_date, '
        ' place_name, '
        ' place_address, '
        ' delivery_type, '
        ' currency_code, '
        ' orders_total_cnt, '
        ' orders_total_cnt_delta, '
        ' orders_success_cnt, '
        ' orders_success_cnt_delta, '
        ' revenue_earned_lcy, '
        ' revenue_earned_delta_lcy, '
        ' revenue_lost_lcy, '
        ' revenue_lost_delta_lcy, '
        ' fines_lcy, '
        ' fines_delta_lcy, '
        ' delay_min, '
        ' delay_delta_min, '
        ' rating, '
        ' rating_delta, '
        ' fact_work_time_min, '
        ' fact_work_time_delta_min, '
        ' plan_work_time_min, '
        ' plan_work_time_delta_min '
        'FROM eats_report_storage.agg_place_digests '
        'ORDER BY place_id, period_date;',
    )
    stats = cursor.fetchall()
    assert stats == [item for item in data]


@pytest.mark.now('2021-05-01T00:04:00Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_DIGESTS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage_gp',
    files=('eats_report_storage_gp_continue_update.sql',),
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_continue_update.sql',),
)
async def test_sync(taxi_eats_report_storage, pgsql, mocked_time):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-digests-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 3)
    check_sync_stats(
        pgsql,
        [
            (
                1,
                datetime.date(2021, 4, 30),
                'place1',
                'address1',
                'native',
                'RUB',
                0,
                None,
                0,
                None,
                decimal.Decimal('0'),
                None,
                decimal.Decimal('0'),
                None,
                decimal.Decimal('0'),
                None,
                0,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            (
                1,
                datetime.date(2021, 5, 1),
                'place1',
                'address1',
                'native',
                'RUB',
                100,
                10,
                80,
                -10,
                decimal.Decimal('111.1111'),
                decimal.Decimal('-11.1111'),
                decimal.Decimal('1.1235'),
                decimal.Decimal('1.1235'),
                decimal.Decimal('11.0'),
                decimal.Decimal('2.0'),
                100,
                -10,
                decimal.Decimal('4.6'),
                decimal.Decimal('0.1'),
                1000,
                -100,
                1111,
                111,
            ),
            (
                2,
                datetime.date(2021, 5, 1),
                'place2',
                'address2',
                'marketplace',
                'BYN',
                200,
                20,
                60,
                -20,
                decimal.Decimal('222.2222'),
                decimal.Decimal('-22.2222'),
                decimal.Decimal('2.1235'),
                decimal.Decimal('2.1235'),
                decimal.Decimal('21.0'),
                decimal.Decimal('3.0'),
                200,
                -20,
                decimal.Decimal('3.6'),
                decimal.Decimal('0.2'),
                2000,
                -200,
                2222,
                222,
            ),
        ],
    )


@pytest.mark.now('2021-05-01T00:04:00Z')
@pytest.mark.config(EATS_REPORT_STORAGE_SYNC_DIGESTS_STATS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_clear_old_data.sql',),
)
async def test_clear_old_data(taxi_eats_report_storage, pgsql, mocked_time):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-digests-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 1)
    check_sync_stats(
        pgsql,
        [
            (
                1,
                datetime.date(2021, 5, 1),
                'place1',
                'address1',
                'native',
                'RUB',
                100,
                10,
                80,
                -10,
                decimal.Decimal('111.1111'),
                decimal.Decimal('-11.1111'),
                decimal.Decimal('1.1234'),
                decimal.Decimal('1.1234'),
                decimal.Decimal('10.9999'),
                decimal.Decimal('1.9999'),
                100,
                -10,
                decimal.Decimal('4.5'),
                decimal.Decimal('0.1'),
                1000,
                -100,
                1111,
                111,
            ),
        ],
    )
