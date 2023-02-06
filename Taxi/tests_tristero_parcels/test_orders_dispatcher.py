import json

import pytest

ORDERS_DISPATCHER_CONIFG = {'enabled': True, 'period_seconds': 60}


@pytest.fixture(name='grocery_orders_make')
def mock_grocery_orders_make(mockserver):
    status = 200
    check_request = False
    expected_request_body = {}

    request_application = 'app_name=tristero_dispatch'

    @mockserver.json_handler('/grocery-orders/internal/v1/orders/v1/make')
    def orders_make(request):
        if check_request:
            assert (
                request.headers['X-Request-Application'] == request_application
            )
            assert request.json == expected_request_body
        if status == 200:
            return {'order_id': '12345-grocery'}
        return mockserver.make_response(status=status)

    class Context:
        def set_response_status(self, new_status):
            nonlocal status
            status = new_status

        def check_request(self, expected_request):
            nonlocal check_request, expected_request_body
            check_request = True
            expected_request_body = expected_request

        @property
        def times_called(self):
            return orders_make.times_called

        @property
        def has_calls(self):
            return orders_make.has_calls

    context = Context()
    return context


def parametrize_dispatch_exp(
        depot_id=None, uid=None, vendor=None, personal_phone_id=None,
):
    predicate = {'type': 'true'}
    if depot_id is not None:
        predicate['depot_id'] = depot_id
    if uid is not None:
        predicate['yandex_uid'] = uid
    if vendor is not None:
        predicate['vendor'] = vendor
    if personal_phone_id is not None:
        predicate['personal_phone_id'] = personal_phone_id

    return pytest.mark.experiments3(
        name='tristero_enable_dispatch',
        consumers=['tristero-parcels/orders-scheduler'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': predicate,
                'value': {'enabled': True},
            },
        ],
        is_config=True,
    )


def _convert_customer_meta_to_pos(customer_meta):
    position = {}
    position['left_at_door'] = customer_meta['left_at_door']
    position['floor'] = customer_meta['floor']
    position['flat'] = customer_meta['room']
    position['entrance'] = customer_meta['porch']
    position['comment'] = customer_meta['courier_comment']
    position['doorcode'] = customer_meta['intercom']
    return position


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_DISPATCHER_SETTINGS=ORDERS_DISPATCHER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-dispatcher-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@parametrize_dispatch_exp()
async def test_mandatory_order_params(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, grocery_orders_make,
):
    """ Dispatched should skip orders without mandatory order
    parameters, in bad statuses and without geo """

    tristero_parcels_db.flush_distlocks()

    should_be_dispatched = set()

    ok_order_params = {
        'status': 'received',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
        'customer_location': '(35.1,55.2)',
    }

    dispatch_start = '2021-07-15T15:00:00+03:00'
    dispatch_end = '2021-07-15T16:00:00+03:00'

    with tristero_parcels_db as db:
        ok_order = db.add_order(
            1,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        ok_order.add_parcel(11, status='in_depot')
        should_be_dispatched.add(ok_order.order_id)
        ok_order.insert_dispatch_schedule(dispatch_start, dispatch_end)

        # order is not it recieved status
        bad_status_order = db.add_order(
            2,
            status='delivered',
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        bad_status_order.add_parcel(21, status='delivered')
        bad_status_order.insert_dispatch_schedule(dispatch_start, dispatch_end)

        # second parcel is not in in_depot status
        bad_status_parcel = db.add_order(
            3,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        bad_status_parcel.add_parcel(31, status='in_depot')
        bad_status_parcel.add_parcel(32, status='delivered')
        bad_status_parcel.insert_dispatch_schedule(
            dispatch_start, dispatch_end,
        )

        # personal_phone_id is null
        no_phone_order = db.add_order(
            4,
            status=ok_order_params['status'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        no_phone_order.add_parcel(41, status='in_depot')
        no_phone_order.insert_dispatch_schedule(dispatch_start, dispatch_end)

        # customer_address is null
        no_address_order = db.add_order(
            5,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_location=ok_order_params['customer_location'],
        )
        no_address_order.add_parcel(51, status='in_depot')
        no_address_order.insert_dispatch_schedule(dispatch_start, dispatch_end)

        # customer_address has no geo
        no_geo_order = db.add_order(
            6,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address='ymapsbm1://geo?some_text',
            customer_location=ok_order_params['customer_location'],
        )
        no_geo_order.add_parcel(61, status='in_depot')
        should_be_dispatched.add(no_geo_order.order_id)
        no_geo_order.insert_dispatch_schedule(dispatch_start, dispatch_end)

        # customer_location is null
        no_location_order = db.add_order(
            7,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
        )
        no_location_order.add_parcel(51, status='in_depot')
        no_location_order.insert_dispatch_schedule(
            dispatch_start, dispatch_end,
        )

    orders_count = 7

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-dispatcher-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        'SELECT order_id, dispatched FROM parcels.orders_dispatch_schedule',
    )
    rows = cursor.fetchall()
    assert grocery_orders_make.times_called == len(should_be_dispatched)
    assert len(rows) == orders_count
    for row in rows:
        assert row[1] == (row[0] in should_be_dispatched)


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_DISPATCHER_SETTINGS=ORDERS_DISPATCHER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-dispatcher-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@parametrize_dispatch_exp()
async def test_dispatch_boundaries(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, grocery_orders_make,
):
    """ Scheduler should get orders only if now is between
    dispatch_start and dispatch_end and order was not already dispatched """

    tristero_parcels_db.flush_distlocks()

    should_be_dispatched = set()

    ok_order_params = {
        'status': 'received',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
        'customer_location': '(35.1,55.2)',
    }
    with tristero_parcels_db as db:
        ok_order = db.add_order(
            1,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        ok_order.add_parcel(11, status='in_depot')
        should_be_dispatched.add(ok_order.order_id)
        ok_order.insert_dispatch_schedule(
            '2021-07-15T15:00:00+03:00', '2021-07-15T16:00:00+03:00',
        )

        # now < dispatch_start
        order_too_early = db.add_order(
            2,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        order_too_early.add_parcel(21, status='in_depot')
        order_too_early.insert_dispatch_schedule(
            '2021-07-15T16:00:00+03:00', '2021-07-15T17:00:00+03:00',
        )

        # now > dispatch_end
        order_too_late = db.add_order(
            3,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        order_too_late.add_parcel(21, status='in_depot')
        order_too_late.insert_dispatch_schedule(
            '2021-07-15T14:00:00+03:00', '2021-07-15T15:00:00+03:00',
        )

        # personal_phone_id is null
        already_dispatched_order = db.add_order(
            4,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
        )
        already_dispatched_order.add_parcel(21, status='in_depot')
        already_dispatched_order.insert_dispatch_schedule(
            '2021-07-15T15:00:00+03:00',
            '2021-07-15T16:00:00+03:00',
            dispatched=True,
        )

    orders_count = 4

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-dispatcher-periodic')

    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        'SELECT order_id, dispatched FROM parcels.orders_dispatch_schedule',
    )
    rows = cursor.fetchall()
    assert len(rows) == orders_count
    assert grocery_orders_make.times_called == len(should_be_dispatched)
    for row in rows:
        assert row[1] == (row[0] in should_be_dispatched) or (
            row[0] == already_dispatched_order.order_id
        )


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_DISPATCHER_SETTINGS=ORDERS_DISPATCHER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-dispatcher-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@parametrize_dispatch_exp(personal_phone_id='some-id')
@pytest.mark.parametrize(
    'request_kind, timeslot_start, timeslot_end',
    [
        (None, '2021-07-15T17:09:00+00:00', '2021-07-15T18:09:00+00:00'),
        ('hour_slot', None, None),
    ],
)
async def test_order_make_request_kind_or_timeslots_is_none(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        grocery_orders_make,
        request_kind,
        timeslot_start,
        timeslot_end,
):
    """ items, personal_phone_id, position and yandex_uid should be
    in /grocery-orders/internal/v1/orders/v1/make request """

    tristero_parcels_db.flush_distlocks()

    personal_phone_id = 'some-id'
    customer_address = 'ymapsbm1://geo?some_text&ll=35.1%2C55.2'
    customer_meta = {
        'floor': 'floor_field',
        'room': 'room_field',
        'porch': 'porch_field',
        'courier_comment': 'courier_comment_field',
        'left_at_door': True,
        'intercom': '51К7307',
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id=personal_phone_id,
            customer_address=customer_address,
            customer_location='(35.1,55.2)',
            customer_meta=json.dumps(customer_meta),
            timeslot_start=timeslot_start,
            timeslot_end=timeslot_end,
            request_kind=request_kind,
        )
        parcel = order.add_parcel(11, status='in_depot')
        order.insert_dispatch_schedule(
            '2021-07-15T15:00:00+03:00', '2021-07-15T16:00:00+03:00',
        )

    position = _convert_customer_meta_to_pos(customer_meta)
    position['location'] = [35.1, 55.2]
    position['place_id'] = customer_address

    grocery_orders_make.check_request(
        {
            'items': [{'id': parcel.product_key, 'quantity': '1'}],
            'locale': '',
            'personal_phone_id': personal_phone_id,
            'position': position,
            'yandex_uid': order.uid,
        },
    )

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-dispatcher-periodic')

    assert grocery_orders_make.times_called == 1

    parcel.update_from_db()
    assert parcel.status == 'auto_ordered'


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_DISPATCHER_SETTINGS=ORDERS_DISPATCHER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-dispatcher-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@parametrize_dispatch_exp(personal_phone_id='some-id')
async def test_order_make_request(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, grocery_orders_make,
):
    """ items, personal_phone_id, position and yandex_uid should be
    in /grocery-orders/internal/v1/orders/v1/make request """

    tristero_parcels_db.flush_distlocks()

    personal_phone_id = 'some-id'
    customer_address = 'ymapsbm1://geo?some_text&ll=35.1%2C55.2'
    customer_meta = {
        'floor': 'floor_field',
        'room': 'room_field',
        'porch': 'porch_field',
        'courier_comment': 'courier_comment_field',
        'left_at_door': True,
        'intercom': '51К7307',
    }
    timeslot_start = '2021-07-15T17:09:00+00:00'
    timeslot_end = '2021-07-15T18:09:00+00:00'
    request_kind = 'hour_slot'

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id=personal_phone_id,
            customer_address=customer_address,
            customer_location='(35.1,55.2)',
            customer_meta=json.dumps(customer_meta),
            timeslot_start=timeslot_start,
            timeslot_end=timeslot_end,
            request_kind=request_kind,
        )
        parcel = order.add_parcel(11, status='in_depot')
        order.insert_dispatch_schedule(
            '2021-07-15T15:00:00+03:00', '2021-07-15T16:00:00+03:00',
        )

    position = _convert_customer_meta_to_pos(customer_meta)
    position['location'] = [35.1, 55.2]
    position['place_id'] = customer_address

    grocery_orders_make.check_request(
        {
            'items': [{'id': parcel.product_key, 'quantity': '1'}],
            'locale': '',
            'personal_phone_id': personal_phone_id,
            'position': position,
            'yandex_uid': order.uid,
            'timeslot': {'start': timeslot_start, 'end': timeslot_end},
            'request_kind': request_kind,
        },
    )

    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-dispatcher-periodic')

    assert grocery_orders_make.times_called == 1

    parcel.update_from_db()
    assert parcel.status == 'auto_ordered'


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_DISPATCHER_SETTINGS=ORDERS_DISPATCHER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-dispatcher-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@pytest.mark.parametrize('status', [400, 500])
@pytest.mark.parametrize('grouped_orders', [True, False])
@parametrize_dispatch_exp()
async def test_order_make_error(
        taxi_tristero_parcels,
        tristero_parcels_db,
        pgsql,
        grocery_orders_make,
        status,
        grouped_orders,
):
    """ dispatch field should remain false if dispatch
    was unsuccessful """

    tristero_parcels_db.flush_distlocks()
    dispatch_id = (
        '123e4567-e89b-12d3-a456-426614174000' if grouped_orders else None
    )
    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id='some-id',
            customer_address='ymapsbm1://geo?some_text&ll=35.1%2C55.2',
            customer_location='(35.1,55.2)',
        )
        parcel = order.add_parcel(11, status='in_depot')
        order.insert_dispatch_schedule(
            '2021-07-15T15:00:00+03:00',
            '2021-07-15T16:00:00+03:00',
            dispatch_id=dispatch_id,
        )

    grocery_orders_make.set_response_status(status)
    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-dispatcher-periodic')

    assert grocery_orders_make.has_calls
    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        'SELECT order_id, dispatched FROM parcels.orders_dispatch_schedule',
    )
    for row in cursor:
        assert row[1] is False

    parcel.update_from_db()
    assert parcel.status == 'in_depot'


@pytest.mark.config(
    TRISTERO_PARCELS_ORDERS_DISPATCHER_SETTINGS=ORDERS_DISPATCHER_CONIFG,
)
@pytest.mark.suspend_periodic_tasks('orders-dispatcher-periodic')
@pytest.mark.now('2021-07-15T15:30:00+03:00')
@parametrize_dispatch_exp()
async def test_combine_same_user_orders(
        taxi_tristero_parcels, tristero_parcels_db, pgsql, grocery_orders_make,
):
    """ orders with the same dispatch_id must be combined in a single order """
    tristero_parcels_db.flush_distlocks()

    ok_order_params = {
        'status': 'received',
        'personal_phone_id': 'some-id',
        'customer_address': 'ymapsbm1://geo?some_text&ll=35.1%2C55.2',
        'customer_location': '(35.1,55.2)',
        'timeslot_start': '2021-07-15T17:09:00+00:00',
        'timeslot_end': '2021-07-15T18:09:00+00:00',
        'request_kind': 'hour_slot',
    }
    dispatch_id = '123e4567-e89b-12d3-a456-426614174000'

    customer_meta = {
        'floor': 'floor_field',
        'room': 'room_field',
        'porch': 'porch_field',
        'courier_comment': 'courier_comment_field',
        'left_at_door': True,
        'intercom': '51К7307',
    }

    dispatch_start = '2021-07-15T15:00:00+03:00'
    dispatch_end = '2021-07-15T16:00:00+03:00'
    parcel_ids = []
    orders = []
    comment_list = []
    with tristero_parcels_db as db:
        order_with_meta = db.add_order(
            1,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
            customer_meta=json.dumps(customer_meta),
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            request_kind=ok_order_params['request_kind'],
        )
        comment_list.append(customer_meta['courier_comment'])
        parcel_ids.append(
            order_with_meta.add_parcel(11, status='in_depot').product_key,
        )
        parcel_ids.append(
            order_with_meta.add_parcel(12, status='in_depot').product_key,
        )
        order_with_meta.insert_dispatch_schedule(
            dispatch_start, dispatch_end, dispatch_id=dispatch_id,
        )
        partial_meta = customer_meta.copy()
        partial_meta['courier_comment'] = 'another comment'
        comment_list.append(partial_meta['courier_comment'])
        partial_meta.pop('left_at_door')
        order_with_partial_meta = db.add_order(
            2,
            status=ok_order_params['status'],
            personal_phone_id=ok_order_params['personal_phone_id'],
            customer_address=ok_order_params['customer_address'],
            customer_location=ok_order_params['customer_location'],
            customer_meta=json.dumps(partial_meta),
            timeslot_start=ok_order_params['timeslot_start'],
            timeslot_end=ok_order_params['timeslot_end'],
            request_kind=ok_order_params['request_kind'],
        )
        parcel_ids.append(
            order_with_partial_meta.add_parcel(
                21, status='in_depot',
            ).product_key,
        )
        parcel_ids.append(
            order_with_partial_meta.add_parcel(
                22, status='in_depot',
            ).product_key,
        )
        order_with_partial_meta.insert_dispatch_schedule(
            dispatch_start, dispatch_end, dispatch_id=dispatch_id,
        )
        orders = [order_with_meta, order_with_partial_meta]

    expected_request = {
        'items': [],
        'locale': '',
        'personal_phone_id': '',
        'position': {},
        'yandex_uid': '',
    }
    for item_id in parcel_ids:
        expected_request['items'].append({'id': item_id, 'quantity': '1'})
    expected_request['personal_phone_id'] = ok_order_params[
        'personal_phone_id'
    ]
    expected_request['position'] = {
        'location': [
            float(i)
            for i in ok_order_params['customer_location'][1:-1].split(',')
        ],
        'place_id': ok_order_params['customer_address'],
    }
    expected_request['yandex_uid'] = orders[0].uid
    expected_request['timeslot'] = {
        'start': orders[0].timeslot_start,
        'end': orders[0].timeslot_end,
    }
    expected_request['request_kind'] = orders[0].request_kind

    for key, value in _convert_customer_meta_to_pos(customer_meta).items():
        expected_request['position'][key] = value
    expected_request['position']['comment'] = ' '.join(comment_list)

    grocery_orders_make.check_request(expected_request)
    await taxi_tristero_parcels.invalidate_caches()
    await taxi_tristero_parcels.run_periodic_task('orders-dispatcher-periodic')

    assert grocery_orders_make.times_called == 1
    cursor = pgsql['tristero_parcels'].cursor()
    cursor.execute(
        'SELECT order_id, dispatched FROM parcels.orders_dispatch_schedule',
    )
    for row in cursor:
        assert row[1] is True
