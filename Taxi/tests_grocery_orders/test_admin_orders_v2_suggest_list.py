# pylint: disable=too-many-lines

import datetime
import json
import uuid

import pytest

from . import admin_orders_suggest_consts as consts
from . import models


def _check_order_history(order_history, expected):
    assert len(order_history) == len(expected)

    for idx, values in enumerate(expected):
        assert order_history[idx]['event_type'] == values[0]
        assert order_history[idx]['event_data'] == values[1]


def _check_closed_order_history(order_history):
    _check_order_history(
        order_history, consts.EXPECTED_ORDER_HISTORY_VALUES[0],
    )


def _check_canceled_order_history(order_history):
    _check_order_history(
        order_history, consts.EXPECTED_ORDER_HISTORY_VALUES[1],
    )


def _create_order_history(pgsql, order_id, db_values):
    cursor = pgsql['grocery_orders'].cursor()

    hours = len(db_values) * datetime.timedelta(hours=1)
    time = models.DEFAULT_CREATED + hours

    for event_type, event_data in reversed(db_values):
        cursor.execute(
            models.LOG_HISTORY_SQL,
            [order_id, time, event_type, json.dumps(event_data)],
        )
        time -= datetime.timedelta(hours=1)


def _create_closed_order_history(pgsql, order_id):
    _create_order_history(pgsql, order_id, consts.ORDER_HISTORY_DB_VALUES[0])


def _create_canceled_order_history(pgsql, order_id):
    _create_order_history(pgsql, order_id, consts.ORDER_HISTORY_DB_VALUES[1])


def _create_various_active_orders(pgsql, grocery_depots, region_id):
    some_cart_id_part = '00000000-0000-0000-0000-d9801310050'
    idempotency_token = 'sql-idempotency-token-'
    orders = [models.Order(pgsql=pgsql) for _ in range(11)]

    for idx, order in enumerate(orders):
        order_id = str(idx)
        cart_id = some_cart_id_part + str(order_id)

        hold_money_status = None
        close_money_status = None
        dispatch_status = None
        assembling_status = None
        wms_reserve_status = None
        dispatch_cargo_status = None
        desired_status = None

        if idx < 5:
            status = 'canceled'
            if idx % 5 == 0:
                hold_money_status = 'failed'
            if idx % 5 == 1:
                close_money_status = 'failed'
            if idx % 5 == 2:
                dispatch_status = 'failed'
            if idx % 5 == 3:
                assembling_status = 'failed'
            if idx % 5 == 4:
                wms_reserve_status = 'failed'
        elif idx < 10:
            if idx % 5 == 0:
                status = 'draft'
            if idx % 5 == 1:
                status = 'checked_out'
            if idx % 5 == 2:
                status = 'assembled'
            if idx % 5 == 3:
                status = 'assembled'
                dispatch_cargo_status = 'accepted'
            if idx % 5 == 4:
                status = 'delivering'
                desired_status = 'closed'
        elif idx == 10:
            status = 'closed'
            cart_id = '32d82a0f-7da0-459c-ba24-12ec11f30c99'

        order.upsert(
            order_id=order_id,
            cart_id=cart_id,
            idempotency_token=idempotency_token + str(order_id),
            short_order_id=str(6 + idx * 10),
            depot_id='1234' + str(idx),
            region_id=region_id,
            status=status,
            state=models.OrderState(
                assembling_status=assembling_status,
                hold_money_status=hold_money_status,
                close_money_status=close_money_status,
                wms_reserve_status=wms_reserve_status,
            ),
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_status=dispatch_status,
                dispatch_cargo_status=dispatch_cargo_status,
            ),
            desired_status=desired_status,
        )
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)


def _create_active_orders(pgsql, grocery_depots):
    some_cart_id_part = '00000000-0000-0000-0000-d9801310050'
    idempotency_token = 'sql-idempotency-token-'

    def _created(days_shift):
        return models.DEFAULT_CREATED + datetime.timedelta(days=days_shift)

    orders = [
        models.Order(
            pgsql=pgsql,
            created=_created(i),
            order_revision=0,
            comment=consts.SPECIFIC_ORDER['comment'],
        )
        for i in range(10)
    ]

    for idx, order in enumerate(orders):
        order_id = str(idx)
        if idx < len(orders) / 2:
            taxi_user_id = 'taxi_user_id'
            personal_phone_id = None
            _create_closed_order_history(pgsql, order_id)
        else:
            taxi_user_id = None
            personal_phone_id = 'personal_phone_id'
            _create_canceled_order_history(pgsql, order_id)
        if idx in (0, len(orders) / 2):
            status = 'delivering'
        else:
            status = 'canceled'

        dispatch_info = models.DispatchStatusInfo(
            dispatch_courier_name='super_courier', dispatch_id='12345',
        )
        order.upsert(
            order_id=order_id,
            status=status,
            cart_id=some_cart_id_part + str(order_id),
            idempotency_token=idempotency_token + str(order_id),
            short_order_id=str(6 + idx * 10),
            depot_id='1234' + str(idx),
            dispatch_status_info=dispatch_info,
            taxi_user_id=taxi_user_id,
            personal_phone_id=personal_phone_id,
        )
        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            depot_id=order.depot_id,
            address='depot address',
            timezone='Europe/Moscow',
        )

    return orders


def _create_active_orders_with_emailid(pgsql, grocery_depots):
    some_cart_id_part = '00000000-0000-0000-0000-d9801310050'
    idempotency_token = 'sql-idempotency-token-'

    def _created(days_shift):
        return models.DEFAULT_CREATED + datetime.timedelta(days=days_shift)

    orders = [
        models.Order(
            pgsql=pgsql,
            created=_created(i),
            order_revision=0,
            vip_type=consts.VIP_TYPE,
        )
        for i in range(9)
    ]

    for idx, order in enumerate(orders):
        order_id = str(idx)
        if idx < 3:
            email_id = 'personal_email_id'
            _create_closed_order_history(pgsql, order_id)
            status = 'delivering'
        elif idx < 6:
            email_id = 'personal_email_id'
            _create_canceled_order_history(pgsql, order_id)
            status = 'canceled'
        else:
            email_id = None
            _create_closed_order_history(pgsql, order_id)
            status = 'canceled'

        dispatch_info = models.DispatchStatusInfo(
            dispatch_courier_name='super_courier',
        )
        order.upsert(
            order_id=order_id,
            status=status,
            cart_id=some_cart_id_part + str(order_id),
            idempotency_token=idempotency_token + str(order_id),
            short_order_id=str(6 + idx * 10),
            depot_id='1234' + str(idx),
            dispatch_status_info=dispatch_info,
            personal_email_id=email_id,
        )
        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            depot_id=order.depot_id,
            address='depot address',
        )

    return orders


ACTIVE_USER_ORDERS_SUGGEST = pytest.mark.parametrize(
    ('user_id', 'personal_phone_id', 'orders_filter', 'orders_count'),
    [
        ('taxi_user_id', None, None, 5),
        ('taxi_user_id', None, 'not_closed', 1),
        ('taxi_user_id', None, 'failed', 4),
        (None, 'personal_phone_id', None, 5),
        (None, 'personal_phone_id', 'not_closed', 1),
        (None, 'personal_phone_id', 'failed', 4),
    ],
)


@ACTIVE_USER_ORDERS_SUGGEST
async def test_active_user_orders(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        grocery_order_log,
        user_id,
        personal_phone_id,
        orders_filter,
        orders_count,
        antifraud,
        passport,
):
    orders = _create_active_orders(pgsql, grocery_depots)

    request_json = {}
    order_ids = []

    if user_id is not None:
        for order in orders:
            if order.taxi_user_id == user_id:
                if orders_filter is None:
                    order_ids.append(order.order_id)
                if (
                        orders_filter == 'not_closed'
                        and order.status != 'closed'
                        and order.status != 'canceled'
                ):
                    order_ids.append(order.order_id)
                if orders_filter == 'failed' and order.status == 'canceled':
                    order_ids.append(order.order_id)

        request_json['user_id'] = user_id

    if personal_phone_id is not None:
        for order in orders:
            if order.personal_phone_id == personal_phone_id:
                if orders_filter is None:
                    order_ids.append(order.order_id)
                if (
                        orders_filter == 'not_closed'
                        and order.status != 'closed'
                        and order.status != 'canceled'
                ):
                    order_ids.append(order.order_id)
                if orders_filter == 'failed' and order.status == 'canceled':
                    order_ids.append(order.order_id)

        request_json['phone_id'] = personal_phone_id

    grocery_order_log.set_order_ids_response(order_ids)
    if orders_filter == 'not_closed':
        request_json['show_not_closed'] = True
    if orders_filter == 'failed':
        request_json['show_failed'] = True
    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200

    response_orders = response.json()['orders']

    assert len(response_orders) == orders_count
    assert passport.times_mock_blackbox_called() == orders_count

    if response_orders:
        created = response_orders[0]['created']

    for order in response_orders:
        assert datetime.datetime.fromisoformat(
            created,
        ) >= datetime.datetime.fromisoformat(order['created'])
        created = order['created']

        assert 'order_id' in order
        assert 'cart_id' in order
        assert 'order_admin_info' in order
        assert 'personal_phone_id' in order

        assert 'city' in order
        assert 'street' in order
        assert 'house' in order
        assert 'flat' in order
        assert 'floor' in order

        assert 'created' in order
        assert 'updated' in order
        assert 'short_order_id' in order
        assert 'comment' in order

        assert order['dispatch_id'] == '12345'
        assert order['depot_address'] == 'depot address'
        assert order['timezone'] == 'Europe/Moscow'
        assert order['courier_name'] == 'super_courier'
        assert order['user_name'] == 'Иван Иванович'


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cold_storage,
        grocery_depots,
        grocery_order_log,
        antifraud,
        passport,
):
    order_id = '7881317eb10d4ecda902fe21587f0df3-grocery'
    grocery_order_log.set_order_ids_response([order_id])

    tips_status = 'pending'
    tips = '1.23'
    comment = 'До двери'
    created = '2020-05-25T17:20:45+0000'
    updated = '2020-05-25T17:35:45+0000'
    finished = '2020-05-25T17:43:45+0000'
    dispatch_start_delivery_ts = '2020-05-25T17:33:45+0000'
    dispatch_delivery_eta = 17
    dispatch_courier_name = 'Александр'
    dispatch_cargo_status = 'new'
    dispatch_status = 'delivering'
    dispatch_id = str(uuid.uuid4())
    grocery_flow_version = 'grocery_flow_v1'
    currency = 'RUB'
    cancel_reason_message = 'Слишком долго'
    cancel_reason_type = 'user_request'
    assembling_status = 'assembled'
    close_money_status = 'success'
    hold_money_status = 'success'
    wms_reserve_status = 'success'
    doorcode = 'K123'
    doorcode_extra = ('doorcode_extra',)
    building_name = ('building_name',)
    doorbell_name = ('doorbell_name',)
    left_at_door = (False,)
    place_id = 'some_place_id'
    floor = '1'
    flat = '5'
    house = '95B'
    street = 'Усачева'
    city = 'Москва'
    country = 'Россия'
    app_info = 'app_ver1=2,app_brand=yataxi,app_name=web'
    status = 'canceled'
    client_price = 230.5
    depot_id = '123456'
    session = 'taxi:1526371256471'
    yandex_uid = '236i17836172'
    personal_phone_id = 'ye7872iu1rc3hir'
    phone_id = '12312ye7872iu1rc3hir'
    eats_user_id = 'some_12y48i2d'
    taxi_user_id = 'some_du38xo'
    eats_order_id = '12323-452123'
    cart_id = '32d82a0f-7da0-459c-ba24-12ec11f30c99'
    cart_version = 4
    short_order_id = '12312-123-1231'
    order_version = 13
    order_revision = 2
    billing_flow = 'grocery_payments'
    dispatch_flow = 'grocery_dispatch'
    due = '2020-05-25T17:55:45+0000'
    idempotency_token = 'idem0'
    locale = 'ru'
    offer_id = 'offer-id-1'
    user_info = 'user_info-1'

    timezone = 'Europe/Moscow'
    depot_address = 'Depot address'

    grocery_depots.add_depot(
        legacy_depot_id=depot_id, timezone=timezone, address=depot_address,
    )

    grocery_cold_storage.set_orders_response(
        items=[
            {
                'item_id': order_id,
                'status': status,
                'client_price': str(client_price),
                'depot_id': depot_id,
                'session': session,
                'yandex_uid': yandex_uid,
                'personal_phone_id': personal_phone_id,
                'phone_id': phone_id,
                'eats_user_id': eats_user_id,
                'taxi_user_id': taxi_user_id,
                'eats_order_id': eats_order_id,
                'cart_id': cart_id,
                'cart_version': cart_version,
                'short_order_id': short_order_id,
                'order_version': order_version,
                'assembling_status': assembling_status,
                'close_money_status': close_money_status,
                'hold_money_status': hold_money_status,
                'wms_reserve_status': wms_reserve_status,
                'doorcode': doorcode,
                'doorcode_extra': doorcode_extra[0],
                'building_name': building_name[0],
                'doorbell_name': doorbell_name[0],
                'left_at_door': left_at_door[0],
                'place_id': place_id,
                'floor': floor,
                'flat': flat,
                'house': house,
                'street': street,
                'city': city,
                'country': country,
                'app_info': app_info,
                'cancel_reason_type': cancel_reason_type,
                'cancel_reason_message': cancel_reason_message,
                'currency': currency,
                'order_id': order_id,
                'grocery_flow_version': grocery_flow_version,
                'dispatch_id': dispatch_id,
                'dispatch_status': dispatch_status,
                'dispatch_cargo_status': dispatch_cargo_status,
                'dispatch_courier_name': dispatch_courier_name,
                'dispatch_delivery_eta': dispatch_delivery_eta,
                'dispatch_start_delivery_ts': dispatch_start_delivery_ts,
                'created': created,
                'updated': updated,
                'finished': finished,
                'comment': comment,
                'tips': tips,
                'tips_status': tips_status,
                'order_revision': order_revision,
                'billing_flow': billing_flow,
                'dispatch_flow': dispatch_flow,
                'location': [10, 20],
                'due': due,
                'idempotency_token': idempotency_token,
                'locale': locale,
                'offer_id': offer_id,
                'user_info': user_info,
            },
        ],
    )

    request_json = {'phone_id': personal_phone_id}
    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    order = orders[0]

    def _datetime_equal(response, request):
        return response == request[:-2] + ':' + request[-2:]

    assert order['order_id'] == order_id
    assert order['cart_id'] == cart_id
    assert order['order_admin_info'] == 'order_canceled'
    assert order['personal_phone_id'] == personal_phone_id
    assert order['short_order_id'] == short_order_id

    assert order['city'] == city
    assert order['street'] == street
    assert order['house'] == house
    assert order['flat'] == flat
    assert order['floor'] == floor
    assert order['comment'] == comment

    assert _datetime_equal(order['created'], created)
    assert _datetime_equal(order['updated'], updated)

    assert order['dispatch_id'] == dispatch_id
    assert order['courier_name'] == dispatch_courier_name
    assert order['depot_address'] == depot_address
    assert order['timezone'] == timezone

    assert passport.times_mock_blackbox_called() == 1
    assert order['user_name'] == 'Иван Иванович'


EMAIL_FILTER_ORDERS = pytest.mark.parametrize(
    ('personal_email_id', 'orders_filter', 'orders_count'),
    [
        ('personal_email_id', None, 6),
        ('personal_email_id', 'not_closed', 3),
        ('personal_email_id', 'failed', 3),
    ],
)


@EMAIL_FILTER_ORDERS
async def test_email_id_filter(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        grocery_order_log,
        personal_email_id,
        orders_filter,
        orders_count,
        antifraud,
):
    orders = _create_active_orders_with_emailid(pgsql, grocery_depots)

    request_json = {}
    order_ids = []

    if personal_email_id is not None:
        for order in orders:
            if order.personal_email_id == personal_email_id:
                if orders_filter is None:
                    order_ids.append(order.order_id)
                if (
                        orders_filter == 'not_closed'
                        and order.status != 'closed'
                        and order.status != 'canceled'
                ):
                    order_ids.append(order.order_id)
                if orders_filter == 'failed' and order.status == 'canceled':
                    order_ids.append(order.order_id)

        request_json['email_id'] = personal_email_id

    grocery_order_log.set_order_ids_response(order_ids)
    if orders_filter == 'not_closed':
        request_json['show_not_closed'] = True
    if orders_filter == 'failed':
        request_json['show_failed'] = True

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
    )

    assert response.status_code == 200

    response_orders = response.json()['orders']

    assert len(response_orders) == orders_count

    if response_orders:
        created = response_orders[0]['created']

    for order in response_orders:
        assert datetime.datetime.fromisoformat(
            created,
        ) >= datetime.datetime.fromisoformat(order['created'])
        created = order['created']

        assert 'order_id' in order
        assert 'cart_id' in order
        assert 'taxi_user_id' in order
        assert 'eats_user_id' in order
        assert 'phone_id' in order
        assert 'status' in order
        assert 'place_id' in order
        assert 'created' in order
        assert 'order_version' in order
        assert 'order_revision' in order

        assert 'depot_id' in order
        assert 'depot_address' in order
        assert 'client_price' in order
        assert 'short_order_id' in order
        assert 'grocery_flow_version' in order

        assert 'app_info' in order
        assert 'cart_id' in order
        assert order['currency'] == 'RUB'
        assert order['depot_id'] == '1234' + order['order_id']
        assert order['courier_name'] == 'super_courier'
        assert order['vip_type'] == consts.VIP_TYPE


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_orders_bulk_suggest(
        taxi_grocery_orders,
        pgsql,
        grocery_cold_storage,
        grocery_depots,
        grocery_order_log,
        antifraud,
):
    order_ids = ['order_id_' + str(i) for i in range(0, 10)]
    request_json = {'user_id': 'super_user'}
    depot_id = '12345'
    grocery_depots.add_depot(legacy_depot_id=depot_id)

    for i in range(0, 5):
        models.Order(pgsql, order_id=order_ids[i], depot_id=depot_id)

    grocery_cold_storage.set_orders_response(
        items=[
            {
                'item_id': order_id,
                'order_id': order_id,
                'cart_id': '32d82a0f-7da0-459c-ba24-12ec11f30c99',
                'cart_version': 1,
                'short_order_id': 'short_id',
                'order_version': 1,
                'status': 'closed',
                'place_id': 'place_id',
                'app_info': 'info',
                'grocery_flow_version': 'grocery_flow_v1',
                'created': '2020-05-25T17:20:45+0000',
                'updated': '2020-05-25T17:20:45+0000',
                'depot_id': depot_id,
                'billing_flow': 'grocery_payments',
                'dispatch_flow': 'grocery_dispatch',
                'eats_user_id': 'eats-user-id',
                'session': 'taxi:1526371256471',
                'taxi_user_id': 'taxi_user_id',
                'location': [10, 20],
                'due': '2020-05-25T17:55:45+0000',
                'idempotency_token': 'idem0',
                'locale': 'ru',
                'offer_id': 'offer-id-1',
                'user_info': 'user_info-1',
            }
            for order_id in order_ids[5:]
        ],
    )
    grocery_order_log.set_order_ids_response(order_ids)

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200

    assert grocery_order_log.times_called_ids_by_range() == 1
    assert grocery_cold_storage.orders_times_called() == 1

    response_orders = response.json()['orders']
    assert len(response_orders) == len(order_ids)
    for order in response_orders:
        assert order['order_id'] in order_ids


def _to_iso_format(date, time_zone='+00:00'):
    return date.isoformat() + time_zone


DELTA = datetime.timedelta(hours=3, minutes=2)
TIME_ZONE_DELTA = datetime.timedelta(hours=3)
TIMEPOINT_A = datetime.datetime(2020, 10, 30, 11, 19)
TIMEPOINT_B = datetime.datetime(2020, 10, 31, 11, 19)


@pytest.mark.parametrize(
    'start,end,expected',
    [
        (TIMEPOINT_A - DELTA, TIMEPOINT_B + DELTA, 'both'),
        (TIMEPOINT_A - DELTA, TIMEPOINT_A + DELTA, 'first'),
        (TIMEPOINT_B - DELTA, TIMEPOINT_B + DELTA, 'second'),
        (TIMEPOINT_A + DELTA, 'inf', 'second'),
        ('-inf', TIMEPOINT_B - DELTA, 'first'),
        ('-inf', 'inf', 'both'),
    ],
)
async def test_time_interval(
        taxi_grocery_orders,
        grocery_order_log,
        pgsql,
        start,
        end,
        expected,
        grocery_depots,
        antifraud,
):
    order = models.Order(
        pgsql=pgsql,
        order_id='first_order',
        region_id=100,
        updated=_to_iso_format(TIMEPOINT_A),
        idempotency_token='_idempotency_token_1',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    order = models.Order(
        pgsql=pgsql,
        order_id='second_order',
        region_id=100,
        updated=_to_iso_format(TIMEPOINT_B),
        idempotency_token='_idempotency_token_2',
    )

    time_interval = {}
    if start != '-inf':
        time_interval['start'] = _to_iso_format(start, '+03:00')
    if end != 'inf':
        time_interval['end'] = _to_iso_format(end, '+03:00')

    request_json = {'time_interval': time_interval, 'region_id': 100}

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200
    orders = response.json()['orders']
    if expected == 'first':
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'first_order'
    if expected == 'second':
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'second_order'
    if expected == 'both':
        assert len(orders) == 2
        if orders[0]['order_id'] == 'first_order':
            assert orders[1]['order_id'] == 'second_order'
        elif orders[0]['order_id'] == 'second_order':
            assert orders[1]['order_id'] == 'first_order'
        else:
            assert False


@pytest.mark.parametrize(
    'start,end,expected',
    [
        (TIMEPOINT_A - DELTA, TIMEPOINT_B + DELTA, 'both'),
        (TIMEPOINT_A - DELTA, TIMEPOINT_A + DELTA, 'first'),
        (TIMEPOINT_B - DELTA, TIMEPOINT_B + DELTA, 'second'),
        (TIMEPOINT_A + DELTA, 'inf', 'second'),
        ('-inf', TIMEPOINT_B - DELTA, 'first'),
        ('-inf', 'inf', 'both'),
    ],
)
async def test_courier_id_filter(
        taxi_grocery_orders,
        grocery_order_log,
        pgsql,
        grocery_depots,
        antifraud,
        start,
        end,
        expected,
):
    order = models.Order(
        pgsql=pgsql,
        order_id='first_order',
        region_id=100,
        created=_to_iso_format(TIMEPOINT_A),
        idempotency_token='_idempotency_token_1',
        dispatch_performer=models.DispatchPerformer(driver_id='some_id'),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    order = models.Order(
        pgsql=pgsql,
        order_id='second_order',
        region_id=100,
        created=_to_iso_format(TIMEPOINT_B),
        idempotency_token='_idempotency_token_2',
        dispatch_performer=models.DispatchPerformer(driver_id='some_id'),
    )

    order = models.Order(
        pgsql=pgsql,
        order_id='third_order',
        region_id=100,
        created=_to_iso_format(TIMEPOINT_A),
        idempotency_token='_idempotency_token_3',
        dispatch_performer=models.DispatchPerformer(driver_id='some_id_2'),
    )

    time_interval = {}
    if start != '-inf':
        time_interval['start'] = _to_iso_format(start, '+03:00')
    if end != 'inf':
        time_interval['end'] = _to_iso_format(end, '+03:00')

    request_json = {
        'order_created_time_interval': time_interval,
        'courier_id': 'some_id',
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200
    orders = response.json()['orders']
    if expected == 'first':
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'first_order'
    if expected == 'second':
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'second_order'
    if expected == 'both':
        assert len(orders) == 2
        if orders[0]['order_id'] == 'first_order':
            assert orders[1]['order_id'] == 'second_order'
        elif orders[0]['order_id'] == 'second_order':
            assert orders[1]['order_id'] == 'first_order'
        else:
            assert False


UPDATED_TIMEPOINT = datetime.datetime(2021, 8, 31, 12, 00)


@pytest.mark.parametrize(
    'start,end,expected',
    [
        (TIMEPOINT_A - DELTA, TIMEPOINT_B + DELTA, 'both'),
        (TIMEPOINT_A - DELTA, TIMEPOINT_A + DELTA, 'first'),
        (TIMEPOINT_B - DELTA, TIMEPOINT_B + DELTA, 'second'),
        (TIMEPOINT_A + DELTA, 'inf', 'second'),
        ('-inf', TIMEPOINT_B - DELTA, 'first'),
        ('-inf', 'inf', 'both'),
    ],
)
@pytest.mark.parametrize('email_id', ['some_id', None])
async def test_created_time_interval(
        taxi_grocery_orders,
        grocery_order_log,
        pgsql,
        start,
        end,
        expected,
        email_id,
        grocery_depots,
        antifraud,
):
    order = models.Order(
        pgsql=pgsql,
        order_id='first_order',
        region_id=100,
        updated=_to_iso_format(UPDATED_TIMEPOINT),
        created=_to_iso_format(TIMEPOINT_A),
        idempotency_token='_idempotency_token_1',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    order = models.Order(
        pgsql=pgsql,
        order_id='second_order',
        region_id=100,
        updated=_to_iso_format(UPDATED_TIMEPOINT),
        created=_to_iso_format(TIMEPOINT_B),
        idempotency_token='_idempotency_token_2',
        personal_email_id=email_id,
    )

    time_interval = {}
    order_log_time_interval = {}
    if start != '-inf':
        time_interval['start'] = _to_iso_format(start, '+03:00')
        order_log_time_interval['start'] = _to_iso_format(
            start - TIME_ZONE_DELTA, '+00:00',
        )
    if end != 'inf':
        time_interval['end'] = _to_iso_format(end, '+03:00')
        order_log_time_interval['end'] = _to_iso_format(
            end - TIME_ZONE_DELTA, '+00:00',
        )

    order_ids = []
    if expected == 'first':
        order_ids.append('first_order')
    elif expected == 'second':
        order_ids.append('second_order')
    else:
        order_ids.append('first_order')
        order_ids.append('second_order')

    grocery_order_log.set_order_ids_response(
        order_ids, personal_email_id=email_id, period=order_log_time_interval,
    )

    request_json = {'order_created_time_interval': time_interval}
    if email_id is not None:
        request_json['email_id'] = email_id
    else:
        request_json['region_id'] = order.region_id

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200
    orders = response.json()['orders']
    if expected == 'first':
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'first_order'
    if expected == 'second':
        assert len(orders) == 1
        assert orders[0]['order_id'] == 'second_order'
    if expected == 'both':
        assert len(orders) == 2
        if orders[0]['order_id'] == 'first_order':
            assert orders[1]['order_id'] == 'second_order'
        elif orders[0]['order_id'] == 'second_order':
            assert orders[1]['order_id'] == 'first_order'
        else:
            assert False


@pytest.mark.parametrize(
    'not_closed_filter',
    ['orders_in_depot', 'dispatched_orders', 'finishing_orders'],
)
async def test_not_closed_active_orders_filters(
        taxi_grocery_orders,
        grocery_depots,
        pgsql,
        not_closed_filter,
        antifraud,
):
    region_id = 100
    _create_various_active_orders(pgsql, grocery_depots, region_id)

    request_json = {
        'orders_type': 'not_closed',
        'region_id': region_id,
        'not_closed_orders_filter': not_closed_filter,
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200

    response_orders = response.json()['orders']

    number_of_orders = len(response_orders)
    if not_closed_filter == 'orders_in_depot':
        assert number_of_orders == 3
    if not_closed_filter == 'dispatched_orders':
        assert number_of_orders == 1
    if not_closed_filter == 'finishing_orders':
        assert number_of_orders == 1


@pytest.mark.parametrize(
    'canceled_orders_filter',
    ['payment_failed', 'dispatch_failed', 'wms_failed'],
)
async def test_canceled_active_orders_filters(
        taxi_grocery_orders,
        grocery_depots,
        pgsql,
        canceled_orders_filter,
        antifraud,
):
    region_id = 100
    _create_various_active_orders(pgsql, grocery_depots, region_id)

    request_json = {
        'orders_type': 'canceled',
        'region_id': region_id,
        'canceled_orders_filter': canceled_orders_filter,
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200

    response_orders = response.json()['orders']

    number_of_orders = len(response_orders)
    if canceled_orders_filter == 'payment_failed':
        assert number_of_orders == 2
    if canceled_orders_filter == 'dispatch_failed':
        assert number_of_orders == 1
    if canceled_orders_filter == 'wms_failed':
        assert number_of_orders == 2


def _create_active_orders_different_region(pgsql, grocery_depots):
    orders = [models.Order(pgsql=pgsql) for _ in range(10)]

    for idx, order in enumerate(orders):
        order_id = str(idx)

        some_cart_id_part = '00000000-0000-0000-0000-d9801310050'
        idempotency_token = 'sql-idempotency-token-'

        order.upsert(
            order_id=order_id,
            eats_order_id='eats_order_id' + str(idx),
            short_order_id=str(6 + idx * 10),
            depot_id='1234' + str(idx),
            region_id=100 + idx % 2,
            cart_id=some_cart_id_part + str(order_id),
            idempotency_token=idempotency_token + str(order_id),
        )
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)


@pytest.mark.parametrize(
    'limit,offset,depot_id,region_id,orders_count',
    [
        (None, None, None, 100, 5),
        (5, None, None, 100, 5),
        (5, 5, None, 100, 0),
        (None, None, '12340', None, 1),
        (10, 1, '12340', None, 0),
        (None, 10, None, 100, 0),
        (None, None, '12340', 100, 1),
    ],
)
async def test_different_regions(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        limit,
        offset,
        depot_id,
        region_id,
        orders_count,
        antifraud,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)
    _create_active_orders_different_region(pgsql, grocery_depots)
    request = {}
    if limit:
        request['limit'] = limit
    if offset:
        request['offset'] = offset
    if depot_id:
        request['depot_id'] = depot_id
    if region_id:
        request['region_id'] = region_id
    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list', json=request, headers=consts.HEADER,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == orders_count


@pytest.mark.parametrize('limit', [None, 1000])
async def test_default_pagination(
        taxi_grocery_orders, pgsql, limit, grocery_depots, antifraud,
):
    orders = [models.Order(pgsql=pgsql) for _ in range(101)]

    for idx, order in enumerate(orders):
        order_id = str(idx)
        depot_id = str(idx)
        grocery_depots.add_depot(legacy_depot_id=depot_id)
        some_cart_id_part = '00000000-0000-0000-0000-d98013100'
        idempotency_token = 'sql-idempotency-token-'

        cart_id = some_cart_id_part + '{:03d}'.format(idx)

        order.upsert(
            order_id=order_id,
            eats_order_id='eats_order_id' + str(idx),
            short_order_id=str(6 + idx * 10),
            cart_id=cart_id,
            depot_id=depot_id,
            region_id=100,
            idempotency_token=idempotency_token + str(idx),
        )
    request = {'region_id': 100}
    if limit:
        request['limit'] = limit
    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list', json=request, headers=consts.HEADER,
    )
    orders = response.json()['orders']
    assert len(orders) == 50


@pytest.mark.parametrize(
    'personal_phone_id, depot_id, is_personal',
    [('personal-phone-id', None, True), (None, 'depot-id', False)],
)
async def test_is_personal(
        taxi_grocery_orders, personal_phone_id, depot_id, is_personal,
):
    support_login = 'support-login'

    request_json = {'phone_id': personal_phone_id, 'depot_id': depot_id}

    response = await taxi_grocery_orders.post(
        '/admin/orders/v2/suggest/list',
        json=request_json,
        headers={'X-Yandex-Login': support_login},
    )

    assert response.status_code == 200
    assert response.json()['is_personal'] == is_personal
