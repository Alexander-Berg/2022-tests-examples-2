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
    'storage_time': 7,
    'yt': {
        'chunk_size': 2,
        'table_name': '//home/eda/restapp/testing/digests/fallback_data',
        'timeouts': {'operation_timeout': 500},
    },
}


def check_synchronization_time(pgsql, date):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT last_sync_time AT TIME ZONE \'UTC\' '
        'FROM eats_report_storage.greenplum_sync '
        'WHERE sync_name = \'sync-digests-fallback-stats\';',
    )
    assert date - cursor.fetchone()[0] < datetime.timedelta(minutes=1)


def check_data_count(pgsql, count):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        """
        SELECT * FROM eats_report_storage.agg_place_digests_fallback;
    """,
    )
    stats = cursor.fetchall()
    assert len(stats) == count


def check_sync_stats(pgsql, data):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        """
        SELECT place_id,
            period_date,
            orders_total_cnt,
            orders_total_cnt_delta,
            orders_success_cnt,
            orders_success_cnt_delta,
            revenue_earned_lcy,
            revenue_earned_delta_lcy,
            revenue_lost_lcy,
            revenue_lost_delta_lcy
        FROM eats_report_storage.agg_place_digests_fallback
        ORDER BY place_id, period_date;
    """,
    )
    stats = cursor.fetchall()
    assert stats == data


@pytest.mark.now('2021-09-10T05:01:00Z')
@pytest.mark.config(
    EATS_REPORT_STORAGE_SYNC_DIGESTS_FALLBACK_STATS=SYNC_CONFIG,
)
@pytest.mark.yt(static_table_data=['yt_data.yaml'], schemas=['yt_schema.yaml'])
async def test_sync_all_data(
        yt_apply, taxi_eats_report_storage, pgsql, mocked_time,
):
    await taxi_eats_report_storage.run_periodic_task(
        'sync-digests-fallback-stats-periodic',
    )

    check_synchronization_time(pgsql, mocked_time.now())
    check_data_count(pgsql, 3)
    check_sync_stats(
        pgsql,
        [
            (
                11,
                datetime.date(2022, 7, 19),
                110,
                -10,
                100,
                -10,
                decimal.Decimal('1000.50'),
                decimal.Decimal('50.50'),
                decimal.Decimal('100.0'),
                decimal.Decimal('0.0'),
            ),
            (
                12,
                datetime.date(2022, 7, 17),
                220,
                20,
                200,
                -20,
                decimal.Decimal('2000.0'),
                decimal.Decimal('0.50'),
                decimal.Decimal('200.0'),
                decimal.Decimal('10.0'),
            ),
            (
                12,
                datetime.date(2022, 7, 18),
                300,
                -30,
                300,
                -20,
                decimal.Decimal('3000.3333'),
                decimal.Decimal('30.7778'),
                decimal.Decimal('300.0'),
                decimal.Decimal('0.0'),
            ),
        ],
    )
