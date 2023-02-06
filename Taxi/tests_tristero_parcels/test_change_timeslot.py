import datetime

import pytest

from tests_tristero_parcels import headers


def _convert_db_datetime(time):
    return time.astimezone(datetime.timezone.utc).strftime(
        '%Y-%m-%dT%H:%M:%S.%fZ',
    )


@pytest.mark.parametrize(
    'handler',
    [
        'internal/v1/parcels/cancel-timeslot-dispatch',
        'admin/parcels/v1/cancel-timeslot-dispatch',
        'internal/v1/parcels/v1/change-timeslot',
    ],
)
async def test_dispatcher_cancel_404(
        taxi_tristero_parcels, tristero_parcels_db, handler,
):
    response = await taxi_tristero_parcels.post(
        handler,
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': '00000000-89ab-cdef-000a-000000002020'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'handler',
    [
        'internal/v1/parcels/cancel-timeslot-dispatch',
        'admin/parcels/v1/cancel-timeslot-dispatch',
        'internal/v1/parcels/v1/change-timeslot',
    ],
)
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@pytest.mark.parametrize('status', [409, 200])
async def test_dispatcher_cancel(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, status, handler,
):
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
        ok_order.add_parcel(11, status='in_depot')

    sql_query = """INSERT INTO parcels.orders_dispatch_schedule
        (order_id, dispatch_start, dispatch_end, dispatched, updated, created)
        VALUES (%s, %s, %s, %s, %s, %s)"""

    values_to_insert = (
        ok_order.order_id,
        '2021-07-15T15:09:00+03:00',
        '2021-07-15T16:09:00+03:00',
        'TRUE' if status == 409 else 'FALSE',
        '2021-07-15T17:09:00+03:00',
        '2021-07-15T17:09:00+03:00',
    )

    await taxi_tristero_parcels.invalidate_caches()
    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(sql_query, values_to_insert)

    response = await taxi_tristero_parcels.post(
        handler,
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': ok_order.order_id},
    )
    assert response.status_code == status
    cursor.execute('SELECT count(*) from parcels.orders_dispatch_schedule')

    assert [row[0] for row in cursor][0] == (1 if status == 409 else 0)


@pytest.mark.now('2021-07-15T15:30:00+03:00')
async def test_timeslot_changed(
        taxi_tristero_parcels, tristero_parcels_db, pgsql,
):
    order_params = {
        'status': 'received',
        'timeslot_start': '2021-07-15T17:09:00+03:00',
        'timeslot_end': '2021-07-15T18:09:00+03:00',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
    }
    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status=order_params['status'],
            timeslot_start=order_params['timeslot_start'],
            timeslot_end=order_params['timeslot_end'],
            personal_phone_id=order_params['personal_phone_id'],
            customer_address=order_params['customer_address'],
        )
        order.add_parcel(11, status='in_depot')

    sql_query = """INSERT INTO parcels.orders_dispatch_schedule
        (order_id, dispatch_start, dispatch_end, dispatched, updated, created)
        VALUES (%s, %s, %s, %s, %s, %s)"""

    values_to_insert = (
        order.order_id,
        '2021-07-15T15:09:00+03:00',
        '2021-07-15T16:09:00+03:00',
        'FALSE',
        '2021-07-15T17:09:00+03:00',
        '2021-07-15T17:09:00+03:00',
    )

    await taxi_tristero_parcels.invalidate_caches()
    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(sql_query, values_to_insert)

    new_timeslot_start = '2021-07-15T20:00:00.000000Z'
    new_timeslot_end = '2021-07-15T21:00:00.000000Z'

    response = await taxi_tristero_parcels.post(
        'internal/v1/parcels/v1/change-timeslot',
        headers=headers.DEFAULT_HEADERS,
        json={
            'order_id': order.order_id,
            'timeslot': {'start': new_timeslot_start, 'end': new_timeslot_end},
        },
    )
    assert response.status_code == 200
    cursor.execute('SELECT count(*) from parcels.orders_dispatch_schedule')

    assert [row[0] for row in cursor][0] == 0

    order.update_from_db()
    assert _convert_db_datetime(order.timeslot_start) == new_timeslot_start
    assert _convert_db_datetime(order.timeslot_end) == new_timeslot_end


@pytest.mark.parametrize('status', [200, 409])
async def test_update_timeslot(
        taxi_tristero_parcels, tristero_parcels_db, mockserver, pgsql, status,
):
    depot_id = tristero_parcels_db.make_depot_id(1)
    new_timeslot = {
        'start': '2021-12-16T14:09:00.000000Z',
        'end': '2021-12-16T15:09:00.000000Z',
    }
    log_platform_timeslot = {
        'from': '2021-12-16T14:09:00+0000',
        'to': '2021-12-16T15:09:00+0000',
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            user_id=headers.YANDEX_UID,
            depot_id=depot_id,
            timeslot_start='2021-12-15T17:09:00+03:00',
            timeslot_end='2021-12-15T18:09:00+03:00',
        )
        order.add_parcel(1, status='in_depot')

    @mockserver.json_handler(
        '/logistic-platform-market/api/'
        + 'platform/request/update_delivery_hour_slot',
    )
    def platform_delivery_hour_slots(request):
        assert request.query['request_id'] == order.token
        assert request.json['timeslot'] == log_platform_timeslot
        return {}

    sql_query = """INSERT INTO parcels.orders_dispatch_schedule
        (order_id, dispatch_start, dispatch_end, dispatched, updated, created)
        VALUES (%s, %s, %s, %s, %s, %s)"""

    values_to_insert = (
        order.order_id,
        '2021-07-15T15:09:00+03:00',
        '2021-07-15T16:09:00+03:00',
        'FALSE' if status == 200 else 'TRUE',
        '2021-07-15T17:09:00+03:00',
        '2021-07-15T17:09:00+03:00',
    )

    await taxi_tristero_parcels.invalidate_caches()
    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(sql_query, values_to_insert)

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/update-timeslot',
        headers=headers.DEFAULT_HEADERS,
        json={
            'ref_order': order.ref_order,
            'vendor': order.vendor,
            'token': order.token,
            'timeslot': new_timeslot,
        },
    )

    assert response.status_code == status

    cursor.execute('SELECT count(*) from parcels.orders_dispatch_schedule')

    assert [row[0] for row in cursor][0] == (0 if status == 200 else 1)

    order.update_from_db()
    assert _convert_db_datetime(order.timeslot_start) == new_timeslot['start']
    assert _convert_db_datetime(order.timeslot_end) == new_timeslot['end']
    assert platform_delivery_hour_slots.times_called == 1


async def test_update_timeslot_404(taxi_tristero_parcels, tristero_parcels_db):
    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/update-timeslot',
        headers=headers.DEFAULT_HEADERS,
        json={
            'ref_order': 'some-ref-order',
            'vendor': 'some-vendor',
            'token': 'some-token',
        },
    )
    assert response.status_code == 404
