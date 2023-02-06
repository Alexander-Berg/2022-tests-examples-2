import datetime

import pytest


DEFFERED_ACCEPTANCE_SETTINGS = {
    'enabled': True,
    'acceptance_scheduler_period_seconds': 60,
    'acceptance_scheduler_hold_minutes': 15,
    'acceptance_worker_period_seconds': 60,
    'start_time_utc': '07:00',
    'end_time_utc': '12:00',
    'depot_ids': [],
}


@pytest.mark.config(
    TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=DEFFERED_ACCEPTANCE_SETTINGS,
)
@pytest.mark.suspend_periodic_tasks('acceptance-scheduler-periodic')
@pytest.mark.now('2021-07-15T10:00:00+03:00')
async def test_basic(taxi_tristero_parcels, tristero_parcels_db, pgsql):
    """ new_acceptance_time should be added for item in queue
    if it were not set """

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='reserved',
            personal_phone_id='some-id',
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
        parcel = order.add_parcel(11, status='created')
        parcel.insert_deffered_acceptance(
            real_acceptance_time='2021-07-15T09:30:00+03:00',
            new_acceptance_time=None,
            accepted=False,
        )

    await taxi_tristero_parcels.run_periodic_task(
        'acceptance-scheduler-periodic',
    )

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted, new_acceptance_time
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == parcel.item_id
    assert rows[0][1] is False
    assert rows[0][2] is not None


@pytest.mark.config(
    TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=DEFFERED_ACCEPTANCE_SETTINGS,
)
@pytest.mark.suspend_periodic_tasks('acceptance-scheduler-periodic')
@pytest.mark.now('2021-07-15T10:00:00+03:00')
@pytest.mark.parametrize(
    'orders_count, delta',
    [
        (2, datetime.timedelta(seconds=9000)),
        (100, datetime.timedelta(seconds=180)),
        (1000, datetime.timedelta(seconds=18)),
    ],
)
async def test_scheduler_distribution_offsets(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, orders_count, delta,
):
    """ new_acceptance_time should be evenly distributed
    between now and end_time_utc """

    tristero_parcels_db.flush_distlocks()

    parcel_ids = set()

    with tristero_parcels_db as db:
        for i in range(orders_count):
            order = db.add_order(
                i + 1,
                status='reserved',
                personal_phone_id='some-id',
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
                customer_location='(35.1,55.2)',
            )
            parcel = order.add_parcel(i + 1, status='created')
            parcel.insert_deffered_acceptance(
                real_acceptance_time='2021-07-15T09:30:00+03:00',
                new_acceptance_time=None,
                accepted=False,
            )
            parcel_ids.add(parcel.item_id)

    await taxi_tristero_parcels.run_periodic_task(
        'acceptance-scheduler-periodic',
    )

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, new_acceptance_time, accepted
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == len(parcel_ids)
    prev_acceptance_time = rows[0][1]
    assert prev_acceptance_time.isoformat() == '2021-07-15T10:00:00+03:00'

    for row in rows[1:]:
        assert row[0] in parcel_ids
        assert row[1] - prev_acceptance_time == delta
        assert row[2] is False
        prev_acceptance_time = row[1]
    assert (
        prev_acceptance_time + delta
    ).isoformat() == '2021-07-15T15:00:00+03:00'


@pytest.mark.config(
    TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=DEFFERED_ACCEPTANCE_SETTINGS,
)
@pytest.mark.suspend_periodic_tasks('acceptance-scheduler-periodic')
@pytest.mark.now('2021-07-15T10:00:00+03:00')
@pytest.mark.parametrize(
    'real_acceptance_time, should_be_scheduled',
    [
        ('2021-07-15T09:30:00+03:00', True),
        ('2021-07-15T09:50:00+03:00', False),
    ],
)
async def test_hold_scheduling(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        real_acceptance_time,
        should_be_scheduled,
):
    """ items will be scheduled only when
    any item in depot real_acceptance_time is lower
    then now - acceptance_scheduler_hold_minutes """

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='reserved',
            personal_phone_id='some-id',
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
        parcel1 = order.add_parcel(11, status='created')
        parcel1.insert_deffered_acceptance(
            real_acceptance_time=real_acceptance_time,
            new_acceptance_time=None,
            accepted=False,
        )

        # this item real_acceptance_time is always greater
        # then now - acceptance_scheduler_hold_minutes
        # but it should be scheduled with previos
        parcel2 = order.add_parcel(12, status='created')
        parcel2.insert_deffered_acceptance(
            real_acceptance_time='2021-07-15T09:59:00+03:00',
            new_acceptance_time=None,
            accepted=False,
        )

    await taxi_tristero_parcels.run_periodic_task(
        'acceptance-scheduler-periodic',
    )

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted, new_acceptance_time
        FROM parcels.deffered_acceptance ORDER BY item_id""",
    )
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert rows[0][0] == parcel1.item_id
    assert rows[0][1] is False
    assert (rows[0][2] is None) == (not should_be_scheduled)

    assert rows[1][0] == parcel2.item_id
    assert rows[1][1] is False
    assert (rows[1][2] is None) == (not should_be_scheduled)


@pytest.mark.config(
    TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=DEFFERED_ACCEPTANCE_SETTINGS,
)
@pytest.mark.suspend_periodic_tasks('acceptance-scheduler-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
async def test_no_distribution_out_of_range(
        taxi_tristero_parcels, tristero_parcels_db, pgsql,
):
    """ new_acceptance_time should be set to
    now if now now between start and end time """

    tristero_parcels_db.flush_distlocks()

    parcel_ids = set()

    with tristero_parcels_db as db:
        for i in range(1000):
            order = db.add_order(
                i + 1,
                status='reserved',
                personal_phone_id='some-id',
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
                customer_location='(35.1,55.2)',
            )
            parcel = order.add_parcel(i + 1, status='created')
            parcel.insert_deffered_acceptance(
                real_acceptance_time='2021-07-15T15:25:00+03:00',
            )
            parcel_ids.add(parcel.item_id)

    await taxi_tristero_parcels.run_periodic_task(
        'acceptance-scheduler-periodic',
    )

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, new_acceptance_time, accepted
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == len(parcel_ids)

    for row in rows:
        assert row[0] in parcel_ids
        assert row[1].isoformat() == '2021-07-15T15:30:00+03:00'
        assert row[2] is False


@pytest.mark.config(
    TRISTERO_PARCELS_DEFFERED_ACCEPTANCE_SETTINGS=DEFFERED_ACCEPTANCE_SETTINGS,
)
@pytest.mark.suspend_periodic_tasks('acceptance-scheduler-periodic')
@pytest.mark.now('2021-07-15T10:00:00+03:00')
async def test_scheduler_distribution_offsets_perdepot(
        taxi_tristero_parcels, tristero_parcels_db, pgsql,
):
    """ new_acceptance_time should be evenly distributed
    between now and end_time_utc per depot """

    tristero_parcels_db.flush_distlocks()

    first_depot_parcel_ids = set()
    second_depot_parcel_ids = set()

    first_depot_orders_count = 10
    first_depot_delta = datetime.timedelta(seconds=1800)
    second_depot_orders_count = 5
    second_depot_delta = datetime.timedelta(seconds=3600)

    with tristero_parcels_db as db:
        for i in range(first_depot_orders_count):
            order = db.add_order(
                i + 1,
                status='reserved',
                personal_phone_id='some-id',
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
                customer_location='(35.1,55.2)',
                depot_id='1',
            )
            parcel = order.add_parcel(i + 1, status='created')
            parcel.insert_deffered_acceptance(
                real_acceptance_time='2021-07-15T09:30:00+03:00',
                new_acceptance_time=None,
                accepted=False,
            )
            first_depot_parcel_ids.add(parcel.item_id)

        for i in range(second_depot_orders_count):
            order = db.add_order(
                i + first_depot_orders_count + 1,
                status='reserved',
                personal_phone_id='some-id',
                customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
                customer_location='(35.1,55.2)',
                depot_id='2',
            )
            parcel = order.add_parcel(
                i + first_depot_orders_count + 1, status='created',
            )
            parcel.insert_deffered_acceptance(
                real_acceptance_time='2021-07-15T09:30:00+03:00',
                new_acceptance_time=None,
                accepted=False,
            )
            second_depot_parcel_ids.add(parcel.item_id)

    await taxi_tristero_parcels.run_periodic_task(
        'acceptance-scheduler-periodic',
    )

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, new_acceptance_time, accepted
        FROM parcels.deffered_acceptance ORDER BY new_acceptance_time""",
    )
    rows = cursor.fetchall()
    assert len(rows) == len(first_depot_parcel_ids) + len(
        second_depot_parcel_ids,
    )
    firs_depot_prev = None
    second_depot_prev = None

    for row in rows:
        if row[0] in first_depot_parcel_ids:
            if firs_depot_prev is None:
                firs_depot_prev = row[1]
                assert (
                    firs_depot_prev.isoformat() == '2021-07-15T10:00:00+03:00'
                )
            else:
                assert row[1] - firs_depot_prev == first_depot_delta
                firs_depot_prev = row[1]
        elif row[0] in second_depot_parcel_ids:
            if second_depot_prev is None:
                second_depot_prev = row[1]
                assert (
                    second_depot_prev.isoformat()
                    == '2021-07-15T10:00:00+03:00'
                )
            else:
                assert row[1] - second_depot_prev == second_depot_delta
                second_depot_prev = row[1]
        else:
            assert False
        assert row[2] is False
