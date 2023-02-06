import pytest


@pytest.mark.pgsql(
    'eats_ordershistory', files=['pg_eats_ordershistory_by_count.sql'],
)
@pytest.mark.config(
    EATS_ORDERSHISTORY_CLEANUP_SETTINGS={
        'orders-cleanup-enabled': True,
        'orders-cleanup-period': 1,
        'orders-ttl-seconds': 1000000000,
        'orders-max-count': 5,
    },
)
@pytest.mark.now('2019-12-31T12:00:00+00:00')
async def test_clear_by_count(taxi_eats_ordershistory, pgsql, testpoint):
    db_expected_order_ids = [
        ('order-id-3',),
        ('order-id-4',),
        ('order-id-5',),
        ('order-id-6',),
        ('order-id-7',),
        ('order-id-8',),
        ('order-id-9',),
        ('order-id-10',),
    ]
    db_expected_cart_ids = [
        ('order-id-3', 1),
        ('order-id-3', 2),
        ('order-id-3', 3),
        ('order-id-8', 1),
        ('order-id-8', 2),
        ('order-id-8', 3),
    ]

    await taxi_eats_ordershistory.run_distlock_task('orders-cleaner')
    _check_db(pgsql, db_expected_order_ids, db_expected_cart_ids)


@pytest.mark.pgsql(
    'eats_ordershistory', files=['pg_eats_ordershistory_by_created.sql'],
)
@pytest.mark.config(
    EATS_ORDERSHISTORY_CLEANUP_SETTINGS={
        'orders-cleanup-enabled': True,
        'orders-cleanup-period': 1,
        'orders-ttl-seconds': 86400,
        'orders-max-count': 1000000,
    },
)
@pytest.mark.now('2019-10-31T12:00:00+00:00')
async def test_clear_by_created(taxi_eats_ordershistory, pgsql, testpoint):
    db_expected_order_ids = [
        ('order-id-2',),
        ('order-id-3',),
        ('order-id-4',),
        ('order-id-5',),
        ('order-id-7',),
        ('order-id-9',),
        ('order-id-10',),
    ]
    db_expected_cart_ids = [
        ('order-id-2', 1),
        ('order-id-2', 2),
        ('order-id-2', 3),
        ('order-id-3', 1),
        ('order-id-3', 2),
        ('order-id-3', 3),
    ]

    await taxi_eats_ordershistory.run_distlock_task('orders-cleaner')
    _check_db(pgsql, db_expected_order_ids, db_expected_cart_ids)


def _check_db(pgsql, db_expected_order_ids, db_expected_cart_ids):
    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id FROM eats_ordershistory.orders ORDER BY created_at;',
    )
    assert list(cursor) == db_expected_order_ids

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute(
        'SELECT order_id, place_menu_item_id '
        'FROM eats_ordershistory.cart_items;',
    )
    assert list(cursor) == db_expected_cart_ids

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute('SELECT order_id FROM eats_ordershistory.feedbacks;')
    assert list(cursor) == db_expected_order_ids

    cursor = pgsql['eats_ordershistory'].cursor()
    cursor.execute('SELECT order_id FROM eats_ordershistory.addresses;')
    assert list(cursor) == db_expected_order_ids
