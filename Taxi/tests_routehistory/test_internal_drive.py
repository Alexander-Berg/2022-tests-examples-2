import pytest

from . import utils


@pytest.mark.parametrize(
    'yandex_uids,min_created,max_records,expected_order_ids',
    [
        ([123456, 20000], None, None, ['order3', 'order1', 'order2']),
        ([20000], None, None, ['order3', 'order2']),
        ([123456], None, None, ['order1']),
        ([44444], None, None, []),
        ([123456, 20000], None, 2, ['order3', 'order2']),
        ([123456, 20000], '2020-04-02T00:00:00+0000', None, ['order3']),
        ([123456, 20000], '2020-05-01T00:00:00+0000', None, []),
    ],
)
@pytest.mark.now('2010-01-01T00:00:00+0000')
async def test_internal_drive_read_write(
        routehistory_internal,
        load_json,
        pgsql,
        yandex_uids,
        min_created,
        max_records,
        expected_order_ids,
):
    orders = load_json('orders.json')
    await routehistory_internal.call('WriteDrive', orders)
    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)

    cursor.execute(
        'SELECT c FROM routehistory.drive_history c ORDER BY '
        'yandex_uid, created',
    )
    drive_orders = utils.convert_pg_result(cursor.fetchall())
    utils.decode_drive_orders(drive_orders)
    assert drive_orders == load_json('expected_db_orders.json')

    result = await routehistory_internal.call(
        'ReadDrive', yandex_uids, min_created, max_records,
    )
    expected_orders = [
        next(order for order in orders if order['order_id'] == order_id)
        for order_id in expected_order_ids
    ]
    assert result == expected_orders


@pytest.mark.parametrize(
    'ttl,max_records,expected_orders',
    [
        (9999, None, ['order2', 'order3', 'order1']),
        (1, None, ['order3']),
        (1, 1, ['order3', 'order1']),
        (12, None, ['order3', 'order1']),
    ],
)
@pytest.mark.now('2020-04-02T00:00:00+0000')
async def test_internal_drive_clean(
        routehistory_internal,
        load_json,
        pgsql,
        ttl,
        max_records,
        expected_orders,
):
    orders = load_json('orders.json')
    await routehistory_internal.call('WriteDrive', orders)
    await routehistory_internal.call('CleanDrive', ttl, max_records)
    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)
    cursor.execute(
        'SELECT c FROM routehistory.drive_history c ORDER BY '
        'yandex_uid, created',
    )
    orders_in_db = utils.convert_pg_result(cursor.fetchall())
    utils.decode_drive_orders(orders_in_db)
    orders_in_db = list(map(lambda x: x['data']['orderId'], orders_in_db))
    assert orders_in_db == expected_orders
