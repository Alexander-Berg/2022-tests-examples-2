import datetime

import pytest

TASK_NAME = 'recent-orders-cleanup'
DB_NAME = 'user-statistics'

NOW = '2020-01-01T23:59:30+0300'
# minus default 32 days then rounding makes 2019-12-01T00:00:00+0300
ROUNDED_BORDER = '2019-12-01T00:00:00+0300'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

DEFAULT_CLEANUP_CONFIG = {
    'cleanup_settings': {'period_sec': 60},
    'save_settings': {'identity_types': [], 'keep_days': 32},
}


async def _get_processed_orders(pgsql):
    db_cursor = pgsql[DB_NAME].cursor()
    db_cursor.execute('SELECT * FROM userstats.recent_orders')
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
                USER_STATISTICS_RECENT_ORDERS={
                    **DEFAULT_CLEANUP_CONFIG,
                    **{
                        'save_settings': {
                            'identity_types': [],
                            'keep_days': days,
                        },
                    },
                },
            ),
            id=f'clean up {days} day(s) old',
        )
        for days, rows_count in [(1, 1), (32, 2), (100, 3)]
    ],
)
async def test_cleanup(
        taxi_user_statistics, testpoint, pgsql, keep_days, expected_rows_count,
):
    rows = await _get_processed_orders(pgsql)
    assert len(rows) == 3

    await taxi_user_statistics.run_periodic_task(TASK_NAME)

    rows = await _get_processed_orders(pgsql)
    now = datetime.datetime.strptime(NOW, DATETIME_FORMAT)
    border_date = now - datetime.timedelta(days=keep_days)
    assert len(rows) == expected_rows_count
    for row in rows:
        assert row['order_created_at'] > border_date


@pytest.mark.now(NOW)
@pytest.mark.pgsql(DB_NAME, files=['test_rounding.sql'])
@pytest.mark.config(USER_STATISTICS_RECENT_ORDERS=DEFAULT_CLEANUP_CONFIG)
async def test_rounding(taxi_user_statistics, pgsql):
    rows = await _get_processed_orders(pgsql)
    assert len(rows) == 4

    await taxi_user_statistics.run_periodic_task(TASK_NAME)

    rows = await _get_processed_orders(pgsql)
    assert len(rows) == 2
    rounded_border = datetime.datetime.strptime(
        ROUNDED_BORDER, DATETIME_FORMAT,
    )
    for row in rows:
        assert row['order_created_at'] > rounded_border
