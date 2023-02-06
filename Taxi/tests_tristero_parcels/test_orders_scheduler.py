import datetime

import pytest

ORDERS_SCHEDULER_CONIFG = {
    'enabled': True,
    'period_seconds': 60,
    'deadline_minutes': 20,
    'minutes_before_timeslot': 60,
    'minutes_before_timeslot_end': 60,
    'look_ahead_minutes': 120,
}


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_SCHEDULER_SETTINGS=ORDERS_SCHEDULER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-scheduler-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
async def test_mandatory_order_params(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, mocked_time,
):
    """ Scheduler should skip orders without mandatory order
    parameters and in bad statuses """

    tristero_parcels_db.flush_distlocks()

    should_be_scheduled = set()

    ok_order_params = {
        'status': 'received',
        'timeslot_start': '2021-07-15T17:09:00+03:00',
        'timeslot_end': '2021-07-15T18:09:00+03:00',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
    }

    with tristero_parcels_db as db:
        ok_order = db.add_order(
            1,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        ok_order.add_parcel(11, status='in_depot', updated=mocked_time.now())
        should_be_scheduled.add(ok_order.order_id)

        # order is not it recieved status
        bad_status_order = db.add_order(
            2,
            status='delivered',
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        bad_status_order.add_parcel(
            21, status='delivered', updated=mocked_time.now(),
        )

        # second parcel is not in in_depot status
        bad_status_parcel = db.add_order(
            3,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        bad_status_parcel.add_parcel(
            31, status='in_depot', updated=mocked_time.now(),
        )
        bad_status_parcel.add_parcel(
            32, status='delivered', updated=mocked_time.now(),
        )

        # timeslot_status is null
        no_start_order = db.add_order(
            4,
            status=ok_order_params['status'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        no_start_order.add_parcel(
            41, status='in_depot', updated=mocked_time.now(),
        )

        # timeslot_end is null
        no_end_order = db.add_order(
            5,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        no_end_order.add_parcel(
            51, status='in_depot', updated=mocked_time.now(),
        )

        # personal_phone_id is null
        no_phone_order = db.add_order(
            6,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            customer_address=ok_order_params['customer_address'],
        )
        no_phone_order.add_parcel(
            61, status='in_depot', updated=mocked_time.now(),
        )

        # customer_address is null
        no_address_order = db.add_order(
            7,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
        )
        no_address_order.add_parcel(
            71, status='in_depot', updated=mocked_time.now(),
        )

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-scheduler-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute('SELECT order_id FROM parcels.orders_dispatch_schedule')
    order_ids_scheduled = {row[0] for row in cursor}
    assert order_ids_scheduled == should_be_scheduled


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_SCHEDULER_SETTINGS=ORDERS_SCHEDULER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-scheduler-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
async def test_time_scheduler_settings(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, mocked_time,
):
    """ Scheduler should use minutes_before_timeslot and look_ahead_minutes
    to pick orders for scheduling """

    tristero_parcels_db.flush_distlocks()

    should_be_scheduled = set()

    ok_order_params = {
        'status': 'received',
        'timeslot_start': '2021-07-15T17:00:00+03:00',
        'timeslot_end': '2021-07-15T18:00:00+03:00',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
    }

    with tristero_parcels_db as db:
        ok_order = db.add_order(
            1,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        ok_order.add_parcel(11, status='in_depot', updated=mocked_time.now())
        should_be_scheduled.add(ok_order.order_id)

        # now + look_ahead_minutes shoud be between
        # timeslot_start and timeslot_end
        another_timeslot_order = db.add_order(
            2,
            status=ok_order_params['status'],
            timeslot_start='2021-07-15T16:00:00+03:00',
            timeslot_end='2021-07-15T17:00:00+03:00',
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        another_timeslot_order.add_parcel(
            21, status='in_depot', updated=mocked_time.now(),
        )

        # now + minutes_before_timeslot should be
        # lower than timeslot_start
        too_close_order = db.add_order(
            3,
            status=ok_order_params['status'],
            timeslot_start='2021-07-15T18:00:00+03:00',
            timeslot_end='2021-07-15T19:00:00+03:00',
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        too_close_order.add_parcel(
            31, status='in_depot', updated=mocked_time.now(),
        )

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-scheduler-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute('SELECT order_id FROM parcels.orders_dispatch_schedule')
    order_ids_scheduled = {row[0] for row in cursor}
    assert order_ids_scheduled == should_be_scheduled


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_SCHEDULER_SETTINGS=ORDERS_SCHEDULER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-scheduler-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@pytest.mark.parametrize('same_users_orders', [True, False])
@pytest.mark.parametrize(
    'orders_count, delta',
    [
        (2, datetime.timedelta(0)),
        (12, datetime.timedelta(0)),
        (100, datetime.timedelta(0)),
        (1000, datetime.timedelta(0)),
    ],
)
async def test_scheduler_distribution(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        orders_count,
        delta,
        same_users_orders,
        mocked_time,
):
    """ Orders in one timeslot should be evenly distributed
    between timeslot_start and timeslot_start time """

    tristero_parcels_db.flush_distlocks()

    timeslot_end = '2021-07-15T18:00:00+03:00'
    dispatch_end = timeslot_end

    order_ids = set()

    with tristero_parcels_db as db:
        for i in range(orders_count):
            uid = (
                'some_uid' + str(i % (orders_count / 2))
                if same_users_orders
                else str(i)
            )
            order = db.add_order(
                i + 1,
                user_id=uid,
                status='received',
                timeslot_start='2021-07-15T17:00:00+03:00',
                timeslot_end=timeslot_end,
                personal_phone_id='some-id',
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            )
            order.add_parcel(
                i + 1, status='in_depot', updated=mocked_time.now(),
            )
            order_ids.add(order.order_id)

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-scheduler-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT order_id, dispatch_start, dispatch_end, dispatch_id
        FROM parcels.orders_dispatch_schedule
        ORDER BY dispatch_start""",
    )
    rows = cursor.fetchall()

    assert len(rows) == len(order_ids)
    prev_dispatch_start = rows[0][1]

    prev_dispatch_id = rows[0][3]

    for row in rows[1:]:
        assert row[0] in order_ids
        if row[3] == prev_dispatch_id:
            assert row[1] == prev_dispatch_start
        else:
            assert row[1] - prev_dispatch_start == (
                delta * 2 if same_users_orders else delta
            )

        assert row[2].isoformat() == dispatch_end
        prev_dispatch_start = row[1]
        prev_dispatch_id = row[3]
    assert (
        prev_dispatch_start + (delta * 2 if same_users_orders else delta)
    ).isoformat() == '2021-07-15T17:00:00+03:00'


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_SCHEDULER_SETTINGS=ORDERS_SCHEDULER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-scheduler-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
async def test_scheduler_ingore_already_scheduled(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, mocked_time,
):
    """ Already scheduled orders shoud be ignored """

    tristero_parcels_db.flush_distlocks()

    ok_order_params = {
        'status': 'received',
        'timeslot_start': '2021-07-15T17:00:00+03:00',
        'timeslot_end': '2021-07-15T18:00:00+03:00',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
    }

    with tristero_parcels_db as db:
        ok_order = db.add_order(
            1,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        ok_order.add_parcel(11, status='in_depot', updated=mocked_time.now())

        scheduled_order = db.add_order(
            2,
            status=ok_order_params['status'],
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        scheduled_order.add_parcel(
            21, status='in_depot', updated=mocked_time.now(),
        )

    scheduled_order_dispatch_start = '2021-07-15T17:30:00+03:00'
    scheduled_order_dispatch_end = '2021-07-15T17:30:00+03:00'
    scheduled_order.insert_dispatch_schedule(
        scheduled_order_dispatch_start, scheduled_order_dispatch_end,
    )

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-scheduler-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT order_id, dispatch_start, dispatch_end
        FROM parcels.orders_dispatch_schedule""",
    )

    rows = cursor.fetchall()
    assert len(rows) == 2
    for row in rows:
        if row[0] == scheduled_order.order_id:
            assert row[1].isoformat() == scheduled_order_dispatch_start
            assert row[2].isoformat() == scheduled_order_dispatch_end


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_SCHEDULER_SETTINGS={
        'enabled': True,
        'period_seconds': 60,
        'deadline_minutes': 0,
        'minutes_before_timeslot': 60,
        'look_ahead_minutes': 120,
        'timeslot_start_offset': 15,
        'timeslot_end_offset': 30,
    },
)
@pytest.mark.suspend_periodic_tasks('orders-scheduler-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@pytest.mark.parametrize('same_users_orders', [True, False])
@pytest.mark.parametrize(
    'orders_count, delta',
    [
        (2, datetime.timedelta(seconds=450)),
        (100, datetime.timedelta(seconds=9)),
        (1000, datetime.timedelta(microseconds=900000)),
    ],
)
async def test_scheduler_distribution_offsets(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        orders_count,
        delta,
        same_users_orders,
        mocked_time,
):
    """ Orders in one timeslot should be evenly distributed
    between (timeslot_start - timeslot_start_offset) and
    timeslot_start time """

    tristero_parcels_db.flush_distlocks()

    timeslot_end = '2021-07-15T18:00:00+03:00'
    dispatch_end = timeslot_end

    order_ids = set()

    with tristero_parcels_db as db:
        for i in range(orders_count):
            order = db.add_order(
                i + 1,
                user_id=(
                    'some_uid' + str(i % (orders_count / 2))
                    if same_users_orders
                    else str(i)
                ),
                status='received',
                timeslot_start='2021-07-15T17:00:00+03:00',
                timeslot_end=timeslot_end,
                personal_phone_id='some-id',
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            )
            order.add_parcel(
                i + 1, status='in_depot', updated=mocked_time.now(),
            )
            order_ids.add(order.order_id)

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-scheduler-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT order_id, dispatch_start, dispatch_end, dispatch_id
        FROM parcels.orders_dispatch_schedule
        ORDER BY dispatch_start""",
    )
    rows = cursor.fetchall()
    assert len(rows) == len(order_ids)
    prev_dispatch_start = rows[0][1]
    prev_dispatch_id = rows[0][3]
    assert prev_dispatch_start.isoformat() == '2021-07-15T16:45:00+03:00'

    for row in rows[1:]:
        assert row[0] in order_ids
        if row[3] != prev_dispatch_id:
            assert row[1] - prev_dispatch_start == (
                delta * 2 if same_users_orders else delta
            )
        else:
            assert row[1] == prev_dispatch_start
        assert row[2].isoformat() == dispatch_end
        prev_dispatch_start = row[1]
        prev_dispatch_id = row[3]
    assert (
        prev_dispatch_start + (delta * 2 if same_users_orders else delta)
    ).isoformat() == '2021-07-15T17:00:00+03:00'
