import pytest


def get_all_order_ids(db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT order_id ' 'FROM dispatch_check_in.check_in_orders;',
    )
    return sorted([r[0] for r in cursor])


@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
async def test_check_in_orders_cleanup(
        taxi_dispatch_check_in, pgsql, mocked_time,
):
    db = pgsql['dispatch_check_in']

    assert get_all_order_ids(db) == ['order_id1', 'order_id2']

    # Clear only staled events
    await taxi_dispatch_check_in.run_task('distlock/psql-cleaner')
    assert get_all_order_ids(db) == ['order_id1']

    # Nothing changed
    mocked_time.sleep(60)
    await taxi_dispatch_check_in.run_task('distlock/psql-cleaner')
    assert get_all_order_ids(db) == ['order_id1']

    # Clear all events
    mocked_time.sleep(7200)
    await taxi_dispatch_check_in.run_task('distlock/psql-cleaner')
    assert get_all_order_ids(db) == []
