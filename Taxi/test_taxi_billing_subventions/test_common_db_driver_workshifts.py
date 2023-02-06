import datetime as dt

import pytest

from taxi_billing_subventions import common


@pytest.mark.filldb(driver_workshifts='for_test_fetch_workshifts')
async def test_fetch_workshifts(db):
    shift_start = dt.datetime(2018, 5, 10, 0, 0, 0, 0, dt.timezone.utc)
    shift_end = dt.datetime(2018, 5, 11, 0, 0, 0, 0, dt.timezone.utc)

    order_created = shift_start - dt.timedelta(minutes=1)
    order_due = shift_end
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == []

    order_created = shift_start + dt.timedelta(minutes=1)
    order_due = shift_end - dt.timedelta(minutes=1)
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == ['id1']

    order_created = shift_start - dt.timedelta(minutes=2)
    order_due = shift_start - dt.timedelta(minutes=1)
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == []

    order_created = shift_start - dt.timedelta(minutes=2)
    order_due = shift_start
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == ['id1']

    order_created = shift_end
    order_due = shift_end + dt.timedelta(minutes=1)
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == []

    order_created = shift_start - dt.timedelta(minutes=1)
    order_due = shift_end - dt.timedelta(minutes=1)
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == ['id1']

    order_created = shift_start + dt.timedelta(minutes=1)
    order_due = shift_end
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert workshifts == ['id1']

    order_created = shift_start
    order_due = shift_end + dt.timedelta(days=1.5)
    workshifts = await common.db.fetch_workshifts(
        db, 'moscow', 'driver1', order_created, order_due,
    )
    assert sorted(workshifts) == ['id1', 'id2']
