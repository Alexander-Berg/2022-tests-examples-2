import datetime

import tests_dispatch_check_in.utils as utils


def execute_with_args(db, query, *args):
    cursor = db.cursor()
    cursor.execute(query.format(*args))


def delete_order(db, order_id):
    execute_with_args(
        db,
        'DELETE FROM dispatch_check_in.check_in_orders '
        'WHERE order_id = \'{}\';',
        order_id,
    )


def clear_db(db):
    cursor = db.cursor()
    cursor.execute('TRUNCATE dispatch_check_in.check_in_orders;')


async def test_dispatch_check_in_statistics_orders_count(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        mocked_time,
        pgsql,
        load,
):
    now = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    mocked_time.set(now)

    insert_checked_in_order = load('insert_1_checked_in_order.sql')
    check_in_order = load('check_in_order.sql')
    insert_not_checked_in_order = load('insert_1_not_checked_in_order.sql')
    db = pgsql['dispatch_check_in']

    async def run_statistics_periodic():
        await taxi_dispatch_check_in.run_periodic_task(
            'dispatch-check-in-statistics',
        )
        mocked_time.sleep(40)
        await taxi_dispatch_check_in.tests_control(invalidate_caches=False)

    async def check_checked_in_orders(etalon, labels):
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'checked_in_orders_count',
            etalon,
            labels,
        )

    async def check_not_checked_in_orders(etalon, labels):
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'not_checked_in_orders_count',
            etalon,
            labels,
        )

    # Begin: no metrics
    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)
    await run_statistics_periodic()
    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)

    # Insert one not checked in order
    execute_with_args(
        db,
        insert_not_checked_in_order,
        'order_id1',
        'terminal_id1',
        'business',
    )
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(1, ['terminal_id1', 'business'])

    # Insert more not checked in orders
    execute_with_args(
        db, insert_not_checked_in_order, 'order_id2', 'terminal_id2', 'econom',
    )
    execute_with_args(
        db, insert_not_checked_in_order, 'order_id3', 'terminal_id2', 'econom',
    )
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(0, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(1, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(2, ['terminal_id2', 'econom'])

    # Insert some checked in orders
    execute_with_args(
        db, insert_checked_in_order, 'order_id10', 'terminal_id1', 'econom',
    )
    execute_with_args(
        db, insert_checked_in_order, 'order_id11', 'terminal_id2', 'business',
    )
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(1, ['terminal_id1', 'econom'])
    await check_checked_in_orders(0, ['terminal_id2', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'business'])
    await check_not_checked_in_orders(1, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_not_checked_in_orders(2, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'business'])

    # Check-in existing order
    execute_with_args(db, check_in_order, 'order_id2')
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(1, ['terminal_id1', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'business'])
    await check_not_checked_in_orders(1, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_not_checked_in_orders(1, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'business'])

    # Delete some not checked in order
    delete_order(db, 'order_id1')
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(1, ['terminal_id1', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_not_checked_in_orders(1, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'business'])

    # Delete some checked in order
    delete_order(db, 'order_id2')
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(1, ['terminal_id1', 'econom'])
    await check_checked_in_orders(0, ['terminal_id2', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_not_checked_in_orders(1, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'business'])

    # Nothing changed
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(1, ['terminal_id1', 'econom'])
    await check_checked_in_orders(0, ['terminal_id2', 'econom'])
    await check_checked_in_orders(1, ['terminal_id2', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_not_checked_in_orders(1, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'business'])

    # Delete all orders
    clear_db(db)
    await run_statistics_periodic()
    await check_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_checked_in_orders(0, ['terminal_id2', 'econom'])
    await check_checked_in_orders(0, ['terminal_id2', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'business'])
    await check_not_checked_in_orders(0, ['terminal_id1', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'econom'])
    await check_not_checked_in_orders(0, ['terminal_id2', 'business'])
