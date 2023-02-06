from tests_tristero_parcels import headers


async def test_order_history(tristero_parcels_db, pgsql):
    statuses = [
        #  'reserved',
        'expecting_delivery',
        'received_partialy',
        'received',
        'delivered_partially',
        'delivered',
    ]

    depot_id = tristero_parcels_db.make_depot_id(1)
    order_id_cnt = 1

    cursor = pgsql['tristero_parcels'].cursor()

    cursor.execute('SELECT count(*) FROM parcels.orders_history')
    res = [row[0] for row in cursor]
    assert res == [0]

    tristero_parcels_db.add_order(
        order_id_cnt, user_id=headers.USER_ID, depot_id=depot_id,
    )

    cursor.execute('SELECT id, status, updated FROM parcels.orders')
    db_orders = [row for row in cursor]
    assert len(db_orders) == 1
    assert db_orders[0][1] == 'reserved'

    order_id = db_orders[0][0]

    cursor.execute(
        'SELECT order_id, status, updated FROM parcels.orders_history',
    )
    db_history = [row for row in cursor]
    assert db_orders == db_history

    for status in statuses:
        cursor.execute(
            'UPDATE parcels.orders SET status = \'{}\''.format(status),
        )
        cursor.execute(
            'SELECT id, status, updated FROM parcels.orders '
            'WHERE id=\'{}\''.format(order_id),
        )
        db_order = [row for row in cursor][0]

        cursor.execute(
            'SELECT order_id, status, updated FROM parcels.orders_history '
            'WHERE order_id = \'{}\' ORDER BY updated'.format(order_id),
        )
        db_history = [row for row in cursor][-1]
        assert db_order[:2] == db_history[:2]

    # dont store transition to the same status
    cursor.execute(
        'UPDATE parcels.orders SET status = \'{}\''.format(statuses[-1]),
    )
    cursor.execute(
        'SELECT count(*) FROM parcels.orders_history WHERE '
        'order_id = \'{}\' AND status=\'{}\''.format(order_id, statuses[-1]),
    )
    res = [row[0] for row in cursor]
    assert res == [1]


async def test_parcels_history(tristero_parcels_db, pgsql):
    statuses = [
        #  'reserved',
        'created',
        'in_depot',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
        'delivered',
    ]

    depot_id = tristero_parcels_db.make_depot_id(1)

    cursor = pgsql['tristero_parcels'].cursor()

    cursor.execute('SELECT count(*) FROM parcels.orders_history')
    res = [row[0] for row in cursor]
    assert res == [0]

    order = tristero_parcels_db.add_order(
        1, user_id=headers.USER_ID, depot_id=depot_id,
    )
    order.add_parcel(1)

    cursor.execute('SELECT id, status, updated FROM parcels.items')
    db_items = [row for row in cursor]
    assert len(db_items) == 1
    assert db_items[0][1] == 'reserved'

    item_id = db_items[0][0]

    cursor.execute(
        'SELECT item_id, status, updated FROM parcels.items_history',
    )
    db_history = [row for row in cursor]
    assert db_items == db_history

    for status in statuses:
        cursor.execute(
            'UPDATE parcels.items SET status = \'{}\''.format(status),
        )
        cursor.execute(
            'SELECT id, status, updated FROM parcels.items '
            'WHERE id=\'{}\''.format(item_id),
        )
        db_item = [row for row in cursor][0]

        cursor.execute(
            'SELECT item_id, status, updated FROM parcels.items_history '
            'WHERE item_id = \'{}\' ORDER BY updated'.format(item_id),
        )
        db_history = [row for row in cursor][-1]
        assert db_item[:2] == db_history[:2]

    # dont store transition to the same status
    cursor.execute(
        'UPDATE parcels.items SET status = \'{}\''.format(statuses[-1]),
    )
    cursor.execute(
        'SELECT count(*) FROM parcels.items_history WHERE '
        'item_id = \'{}\' AND status=\'{}\''.format(item_id, statuses[-1]),
    )
    res = [row[0] for row in cursor]
    assert res == [1]


async def test_parcels_deleted_from_order(tristero_parcels_db, pgsql):

    depot_id = tristero_parcels_db.make_depot_id(1)
    cursor = pgsql['tristero_parcels'].cursor()

    order = tristero_parcels_db.add_order(
        1, user_id=headers.USER_ID, depot_id=depot_id,
    )
    cursor.execute('SELECT id, status, updated FROM parcels.orders')
    db_orders = [row for row in cursor]
    order.add_parcel(1)
    cursor.execute('SELECT id, status, updated FROM parcels.items')

    order_id = db_orders[0][0]
    db_items = [row for row in cursor]
    item_id = db_items[0][0]

    # delete item from order
    cursor.execute(f'DELETE FROM parcels.items WHERE id=\'{item_id}\'')

    # check moving to deleted table
    cursor.execute('SELECT * FROM parcels.deleted_items')
    db_items = [row for row in cursor]
    assert len(db_items) == 1
    assert len(db_items[0][2]['item_history']) == 2

    # check item is deleted
    cursor.execute('SELECT id, status, updated FROM parcels.items')
    assert [row for row in cursor] == []

    # check item history is deleted
    cursor.execute(
        'SELECT item_id, status, updated FROM parcels.items_history '
        'WHERE item_id = \'{}\' ORDER BY updated'.format(item_id),
    )
    assert [row for row in cursor] == []

    # delete order
    cursor.execute(f'DELETE FROM parcels.orders WHERE id=\'{order_id}\'')

    # check item is deleted from from deleted_items
    cursor.execute('SELECT * FROM parcels.deleted_items')
    assert [row for row in cursor] == []

    # check order history is deleted
    cursor.execute(
        'SELECT order_id, status, updated FROM parcels.orders_history '
        'WHERE order_id = \'{}\' ORDER BY updated'.format(item_id),
    )
    assert [row for row in cursor] == []


async def test_parcels_deleted_with_order_cascade(tristero_parcels_db, pgsql):

    depot_id = tristero_parcels_db.make_depot_id(1)
    cursor = pgsql['tristero_parcels'].cursor()

    order = tristero_parcels_db.add_order(
        1, user_id=headers.USER_ID, depot_id=depot_id,
    )
    cursor.execute('SELECT id, status, updated FROM parcels.orders')
    db_orders = [row for row in cursor]
    order.add_parcel(1)
    cursor.execute('SELECT id, status, updated FROM parcels.items')

    order_id = db_orders[0][0]
    db_items = [row for row in cursor]
    item_id = db_items[0][0]

    # delete order
    cursor.execute(f'DELETE FROM parcels.orders WHERE id=\'{order_id}\'')

    # check deleted table is empty
    cursor.execute('SELECT * FROM parcels.deleted_items')
    assert [row for row in cursor] == []

    # check item is deleted
    cursor.execute('SELECT id, status, updated FROM parcels.items')
    assert [row for row in cursor] == []

    # check item history is deleted
    cursor.execute(
        'SELECT item_id, status, updated FROM parcels.items_history '
        'WHERE item_id = \'{}\' ORDER BY updated'.format(item_id),
    )
    assert [row for row in cursor] == []

    # check order history is deleted
    cursor.execute(
        'SELECT order_id, status, updated FROM parcels.orders_history '
        'WHERE order_id = \'{}\' ORDER BY updated'.format(item_id),
    )
    assert [row for row in cursor] == []
