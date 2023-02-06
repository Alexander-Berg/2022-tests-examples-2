import datetime

import pytest

TASK_NAME = 'processed-orders-cleanup'
DB_NAME = 'user-statistics'

NOW = '2020-08-10T12:10:00+0300'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

DEFAULT_CLEANUP_CONFIG = {'keep_days': 7, 'period_sec': 300}


async def _get_processed_orders(pgsql):
    db_cursor = pgsql[DB_NAME].cursor()
    db_cursor.execute('SELECT * FROM userstats.processed_orders')
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    return [dict(zip(columns, row)) for row in rows]


@pytest.mark.now(NOW)
@pytest.mark.pgsql(DB_NAME, files=['test_cleanup.sql'])
@pytest.mark.parametrize(
    'keep_days,expected_rows_count',
    [
        pytest.param(
            days,
            rows_count,
            marks=pytest.mark.config(
                USER_STATISTICS_PROCESSED_ORDERS_CLEAN_UP_SETTINGS={
                    **DEFAULT_CLEANUP_CONFIG,
                    'keep_days': days,
                },
            ),
            id=f'clean up {days} day(s) old',
        )
        for days, rows_count in [(1, 0), (7, 1), (14, 2)]
    ],
)
async def test_cleanup(
        taxi_user_statistics, testpoint, pgsql, keep_days, expected_rows_count,
):
    await taxi_user_statistics.run_periodic_task(TASK_NAME)

    rows = await _get_processed_orders(pgsql)
    now = datetime.datetime.strptime(NOW, DATETIME_FORMAT)
    border_date = now - datetime.timedelta(days=keep_days)
    assert len(rows) == expected_rows_count
    for row in rows:
        assert row['created_at'] > border_date


@pytest.mark.now(NOW)
@pytest.mark.pgsql(DB_NAME, files=['test_rounding.sql'])
@pytest.mark.config(
    USER_STATISTICS_PROCESSED_ORDERS_CLEAN_UP_SETTINGS={
        **DEFAULT_CLEANUP_CONFIG,
        'period_sec': 1800,
    },
)
async def test_rounding(taxi_user_statistics, pgsql):
    await taxi_user_statistics.run_periodic_task(TASK_NAME)

    rows = await _get_processed_orders(pgsql)
    assert len(rows) == 2
    for row in rows:
        assert row['order_id'] in {'order2', 'order3'}
