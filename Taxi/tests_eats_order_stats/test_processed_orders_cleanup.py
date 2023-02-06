import datetime

import pytest
import pytz

NOW = '2021-07-01T12:10:00+0300'
TASK_NAME = 'processed-orders-cleanup-periodic-periodic'
DB_NAME = 'eats_order_stats'
SCHEMA = 'eats_order_stats'
SCHEMA_V2 = 'eats_order_stats_v2'

CLEANUP_CONFIG = {'keep_days': 14, 'period_sec': 3600, 'max_rows_to_clean': 2}


async def _get_processed_orders(pgsql, schema):
    db_cursor = pgsql[DB_NAME].cursor()
    db_cursor.execute('SELECT * FROM {}.processed_orders'.format(schema))
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    return [dict(zip(columns, row)) for row in rows]


# Под условие попадают все 6 записей
# Лимит 2 записи, остаться должно 4 записи
@pytest.mark.now(NOW)
@pytest.mark.parametrize('schema', [SCHEMA, SCHEMA_V2])
@pytest.mark.config(
    EATS_ORDER_STATS_PROCESSED_ORDERS_CLEAN_UP_SETTINGS=CLEANUP_CONFIG,
)
async def test_cleanup_max_row_less(pgsql, taxi_eats_order_stats, schema):
    await taxi_eats_order_stats.run_periodic_task(TASK_NAME)

    rows = await _get_processed_orders(pgsql, schema)

    assert len(rows) == 4
    threshold = datetime.datetime(2021, 5, 31, 15, 32, tzinfo=pytz.utc)
    assert all(r['created_at'].astimezone(pytz.utc) > threshold for r in rows)


# Под условие попадают все 6 записей
# Лимит 6 записей, не должно остаться ни одной
@pytest.mark.now(NOW)
@pytest.mark.parametrize('schema', [SCHEMA, SCHEMA_V2])
@pytest.mark.config(
    EATS_ORDER_STATS_PROCESSED_ORDERS_CLEAN_UP_SETTINGS=dict(
        CLEANUP_CONFIG, max_rows_to_clean=6,
    ),
)
async def test_cleanup_max_row_greater(pgsql, taxi_eats_order_stats, schema):
    await taxi_eats_order_stats.run_periodic_task(TASK_NAME)

    rows = await _get_processed_orders(pgsql, schema)

    assert not rows


@pytest.mark.now(NOW)
@pytest.mark.parametrize('schema', [SCHEMA, SCHEMA_V2])
@pytest.mark.config(
    EATS_ORDER_STATS_PROCESSED_ORDERS_CLEAN_UP_SETTINGS=dict(
        CLEANUP_CONFIG, keep_days=1, max_rows_to_clean=100,
    ),
)
async def test_cleanup_updates_last_order_at_archive(
        taxi_eats_order_stats, pgsql, schema,
):
    await taxi_eats_order_stats.run_periodic_task(TASK_NAME)

    db_cursor = pgsql[DB_NAME].cursor()
    db_cursor.execute(
        'SELECT last_order_at_archive FROM {}.orders_counters'.format(schema),
    )

    expected = datetime.datetime(
        year=2021, month=6, day=2, hour=15, minute=32, tzinfo=pytz.utc,
    )
    received = {x[0].astimezone(pytz.utc) for x in db_cursor.fetchall()}
    assert received == {expected}
