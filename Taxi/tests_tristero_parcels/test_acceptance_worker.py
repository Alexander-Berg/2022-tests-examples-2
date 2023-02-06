import pytest


@pytest.mark.suspend_periodic_tasks('acceptance-worker-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@pytest.mark.parametrize(
    'new_acceptance_time,parcel_status,order_status,accepted',
    [
        ('2021-07-15T15:00:00+03:00', 'in_depot', 'received', True),
        ('2021-07-15T16:00:00+03:00', 'created', 'reserved', False),
    ],
)
async def test_basic(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        new_acceptance_time,
        parcel_status,
        order_status,
        accepted,
):
    """ worker should set parcels status to in_depot if
    current time is > new_acceptance_time """

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
            new_acceptance_time=new_acceptance_time,
        )

    await taxi_tristero_parcels.run_periodic_task('acceptance-worker-periodic')

    parcel.update_from_db()
    assert parcel.status == parcel_status

    order.update_from_db()
    assert order.status == order_status

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        """SELECT item_id, accepted
        FROM parcels.deffered_acceptance""",
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == parcel.item_id
    assert rows[0][1] == accepted


@pytest.mark.suspend_periodic_tasks('acceptance-worker-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@pytest.mark.parametrize(
    'parcel_status,order_status',
    [
        ('created', 'reserved'),
        ('in_depot', 'received'),
        ('delivered', 'delivered'),
    ],
)
async def test_no_dobule_acceptance(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        parcel_status,
        order_status,
):
    """ if item already accepted - nothing
    should be done """

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status=order_status,
            personal_phone_id='some-id',
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
        parcel = order.add_parcel(11, status=parcel_status)
        parcel.insert_deffered_acceptance(
            new_acceptance_time='2021-07-15T15:00:00+03:00', accepted=True,
        )

    await taxi_tristero_parcels.run_periodic_task('acceptance-worker-periodic')

    parcel.update_from_db()
    assert parcel.status == parcel_status

    order.update_from_db()
    assert order.status == order_status


@pytest.mark.suspend_periodic_tasks('acceptance-worker-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
async def test_several_parcels(
        taxi_tristero_parcels, tristero_parcels_db, pgsql,
):
    """ worker should update only item
    with new_acceptance_time <= now """

    tristero_parcels_db.flush_distlocks()

    with tristero_parcels_db as db:
        updated_order = db.add_order(
            1,
            status='reserved',
            personal_phone_id='some-id',
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
        updated_parcel = updated_order.add_parcel(11, status='created')
        updated_parcel.insert_deffered_acceptance(
            new_acceptance_time='2021-07-15T15:00:00+03:00',
        )

        not_changed_order = db.add_order(
            2,
            status='reserved',
            personal_phone_id='some-id',
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
        not_changed_parcel = not_changed_order.add_parcel(22, status='created')
        not_changed_parcel.insert_deffered_acceptance(
            new_acceptance_time='2021-07-15T16:00:00+03:00',
        )

    await taxi_tristero_parcels.run_periodic_task('acceptance-worker-periodic')

    updated_parcel.update_from_db()
    assert updated_parcel.status == 'in_depot'

    updated_order.update_from_db()
    assert updated_order.status == 'received'

    not_changed_parcel.update_from_db()
    assert not_changed_parcel.status == 'created'

    not_changed_order.update_from_db()
    assert not_changed_order.status == 'reserved'
