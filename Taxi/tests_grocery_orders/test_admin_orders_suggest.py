# pylint: disable=too-many-lines

import datetime
import json
import uuid

import pytest

from . import admin_orders_suggest_consts as consts
from . import headers
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


@pytest.fixture(name='_create_various_active_orders')
def _create_various_active_orders(pgsql, grocery_depots):
    def inner(region_id):
        some_cart_id_part = '00000000-0000-0000-0000-d9801310050'
        idempotency_token = 'sql-idempotency-token-'
        orders = [
            models.Order(pgsql=pgsql, vip_type=consts.VIP_TYPE)
            for _ in range(11)
        ]

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
                personal_email_id=consts.SPECIFIC_ORDER['personal_email_id'],
            )
            grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    return inner


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
            vip_type=consts.VIP_TYPE,
            personal_email_id=consts.SPECIFIC_ORDER['personal_email_id'],
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
            taxi_user_id=taxi_user_id,
            personal_phone_id=personal_phone_id,
        )
        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            depot_id=order.depot_id,
            address='depot address',
        )

    return orders


def _create_atcive_orders_with_emailid(pgsql, grocery_depots):
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


async def _get_order(taxi_grocery_orders, order_id, header=None):
    if header is None:
        header = consts.HEADER
    header['X-Remote-IP'] = '172.99.23.44'
    request_json = {'order_id': order_id}
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=header,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    return orders[0]


def _create_specific_order(pgsql):
    return models.Order(
        pgsql,
        order_id=consts.SPECIFIC_ORDER['order_id'],
        cart_id=consts.SPECIFIC_ORDER['cart_id'],
        short_order_id=consts.SPECIFIC_ORDER['short_order_id'],
        order_version=consts.SPECIFIC_ORDER['order_version'],
        taxi_user_id=consts.SPECIFIC_ORDER['taxi_user_id'],
        tips=consts.SPECIFIC_ORDER['tips'],
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_status=consts.SPECIFIC_ORDER['dispatch_status'],
            dispatch_courier_name=consts.SPECIFIC_ORDER[
                'dispatch_courier_name'
            ],
            dispatch_id=consts.SPECIFIC_ORDER['dispatch_id'],
            dispatch_cargo_status=consts.SPECIFIC_ORDER[
                'dispatch_cargo_status'
            ],
            dispatch_delivery_eta=consts.SPECIFIC_ORDER[
                'dispatch_delivery_eta'
            ],
            dispatch_status_meta=consts.SPECIFIC_ORDER['dispatch_status_meta'],
        ),
        comment='specific_comment',
        client_price=consts.SPECIFIC_ORDER['client_price'],
        depot_id=consts.SPECIFIC_ORDER['depot_id'],
        personal_phone_id=consts.SPECIFIC_ORDER['personal_phone_id'],
        yandex_uid=consts.SPECIFIC_ORDER['yandex_uid'],
        phone_id=consts.SPECIFIC_ORDER['phone_id'],
        eats_user_id=consts.SPECIFIC_ORDER['eats_user_id'],
        eats_order_id=consts.SPECIFIC_ORDER['eats_order_id'],
        created=datetime.datetime.fromisoformat(
            consts.SPECIFIC_ORDER['created'],
        ),
        status=consts.SPECIFIC_ORDER['status'],
        cancel_reason_type=consts.SPECIFIC_ORDER['cancel_reason_type'],
        cancel_reason_message=consts.SPECIFIC_ORDER['cancel_reason_message'],
        city=consts.SPECIFIC_ORDER['city'],
        street=consts.SPECIFIC_ORDER['street'],
        flat=consts.SPECIFIC_ORDER['flat'],
        floor=consts.SPECIFIC_ORDER['floor'],
        place_id=consts.SPECIFIC_ORDER['place_id'],
        doorcode=consts.SPECIFIC_ORDER['doorcode'],
        doorcode_extra=consts.SPECIFIC_ORDER['doorcode_extra'],
        building_name=consts.SPECIFIC_ORDER['building_name'],
        doorbell_name=consts.SPECIFIC_ORDER['doorbell_name'],
        left_at_door=consts.SPECIFIC_ORDER['left_at_door'],
        meet_outside=consts.SPECIFIC_ORDER['meet_outside'],
        no_door_call=consts.SPECIFIC_ORDER['no_door_call'],
        postal_code=consts.SPECIFIC_ORDER['postal_code'],
        delivery_common_comment=consts.SPECIFIC_ORDER[
            'delivery_common_comment'
        ],
        state=models.OrderState(
            wms_reserve_status=consts.SPECIFIC_ORDER['wms_reserve_status'],
            hold_money_status=consts.SPECIFIC_ORDER['hold_money_status'],
            close_money_status=consts.SPECIFIC_ORDER['close_money_status'],
            assembling_status=consts.SPECIFIC_ORDER['assembling_status'],
        ),
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
        currency=consts.SPECIFIC_ORDER['currency'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        order_revision=consts.SPECIFIC_ORDER['order_revision'],
        billing_flow=consts.SPECIFIC_ORDER['billing_flow'],
        locale=consts.SPECIFIC_ORDER['locale'],
        vip_type=consts.VIP_TYPE,
        personal_email_id=consts.SPECIFIC_ORDER['personal_email_id'],
    )


def _compare_orders(lhs_order, rhs_order):
    assert lhs_order['comment'] == rhs_order['comment']
    assert lhs_order['order_id'] == rhs_order['order_id']
    assert lhs_order['cart_id'] == rhs_order['cart_id']
    assert lhs_order['short_order_id'] == rhs_order['short_order_id']
    assert lhs_order['order_version'] == rhs_order['order_version']
    assert lhs_order['taxi_user_id'] == rhs_order['taxi_user_id']
    assert lhs_order['tips'] == rhs_order['tips']
    assert int(lhs_order['client_price']) == int(rhs_order['client_price'])
    assert lhs_order['depot_id'] == rhs_order['depot_id']
    assert lhs_order['personal_phone_id'] == rhs_order['personal_phone_id']
    assert lhs_order['yandex_uid'] == rhs_order['yandex_uid']
    assert lhs_order['phone_id'] == rhs_order['phone_id']
    assert lhs_order['eats_user_id'] == rhs_order['eats_user_id']
    assert lhs_order['eats_order_id'] == rhs_order['eats_order_id']
    assert lhs_order['created'] == rhs_order['created']

    assert lhs_order['status'] == rhs_order['status']
    assert lhs_order['cancel_reason_type'] == rhs_order['cancel_reason_type']
    assert (
        lhs_order['cancel_reason_message']
        == rhs_order['cancel_reason_message']
    )
    assert lhs_order['city'] == rhs_order['city']
    assert lhs_order['street'] == rhs_order['street']
    assert lhs_order['flat'] == rhs_order['flat']
    assert lhs_order['floor'] == rhs_order['floor']
    assert lhs_order['place_id'] == rhs_order['place_id']
    assert lhs_order['doorcode'] == rhs_order['doorcode']
    assert lhs_order['doorcode_extra'] == rhs_order['doorcode_extra']
    assert lhs_order['building_name'] == rhs_order['building_name']
    assert lhs_order['doorbell_name'] == rhs_order['doorbell_name']
    assert lhs_order['left_at_door'] == rhs_order['left_at_door']
    assert lhs_order['meet_outside'] == rhs_order['meet_outside']
    assert lhs_order['no_door_call'] == rhs_order['no_door_call']
    assert lhs_order['postal_code'] == rhs_order['postal_code']
    assert (
        lhs_order['delivery_common_comment']
        == rhs_order['delivery_common_comment']
    )
    assert lhs_order['wms_reserve_status'] == rhs_order['wms_reserve_status']
    assert lhs_order['hold_money_status'] == rhs_order['hold_money_status']
    assert lhs_order['close_money_status'] == rhs_order['close_money_status']
    assert lhs_order['assembling_status'] == rhs_order['assembling_status']
    assert lhs_order['edit_status'] == rhs_order['edit_status']
    assert lhs_order['currency'] == rhs_order['currency']
    assert lhs_order['app_info'] == rhs_order['app_info']
    assert lhs_order['dispatch_id'] == rhs_order['dispatch_id']
    assert lhs_order['dispatch_status'] == rhs_order['dispatch_status']
    assert (
        lhs_order['dispatch_cargo_status']
        == rhs_order['dispatch_cargo_status']
    )
    assert (
        lhs_order['dispatch_delivery_eta']
        == rhs_order['dispatch_delivery_eta']
    )
    assert lhs_order['order_revision'] == rhs_order['order_revision']
    assert lhs_order['billing_flow'] == rhs_order['billing_flow']
    assert lhs_order['timezone'] == rhs_order['timezone']
    assert lhs_order['vip_type'] == rhs_order['vip_type']
    assert lhs_order['personal_email_id'] == rhs_order['personal_email_id']


@pytest.mark.translations(
    grocery_orders={
        'failure_specific_cancel_reason_message': {
            'ru': 'russian translation',
            'he': 'hebrew translation',
        },
    },
)
@pytest.mark.parametrize(
    'header, expected_translation',
    [
        ({'Accept-Language': 'ru'}, 'russian translation'),
        ({'Accept-Language': 'he'}, 'hebrew translation'),
    ],
)
async def test_specific_order(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        passport,
        header,
        expected_translation,
        antifraud,
):
    order = _create_specific_order(pgsql)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        timezone=consts.SPECIFIC_ORDER_TIMEZONE,
    )
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    specific_order = await _get_order(
        taxi_grocery_orders, order.order_id, header=header,
    )
    _compare_orders(specific_order, consts.SPECIFIC_ORDER)
    assert 'user_name' in specific_order
    assert 'has_ya_plus' in specific_order

    assert specific_order['batch'] is not None

    assert specific_order['cancel_reason_description'] == expected_translation


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
        assert 'personal_email_id' in order

        assert 'app_info' in order
        assert 'cart_id' in order
        assert order['currency'] == 'RUB'
        assert order['depot_id'] == '1234' + order['order_id']
        assert order['courier_name'] == 'super_courier'
        assert order['vip_type'] == consts.VIP_TYPE


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
    orders = _create_atcive_orders_with_emailid(pgsql, grocery_depots)

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
        assert 'taxi_user_id' in order
        assert 'eats_user_id' in order
        assert 'phone_id' in order
        assert 'status' in order
        assert 'place_id' in order
        assert 'created' in order
        assert 'order_version' in order
        assert 'order_revision' in order
        assert 'personal_email_id' in order

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


SHORT_ORDER_ID = 'short_order_id'
GROCERY_ORDER_ID = '7881317eb10d4ecda902fe21587f0df3-grocery'


@pytest.mark.parametrize('order_id', [SHORT_ORDER_ID, GROCERY_ORDER_ID])
@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cold_storage,
        grocery_depots,
        grocery_order_log,
        mockserver,
        order_id,
        antifraud,
):
    if order_id == SHORT_ORDER_ID:
        grocery_order_log.set_order_id_response(GROCERY_ORDER_ID)
    request_json = {'order_id': order_id}

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
    meet_outside = True
    no_door_call = True
    postal_code = 'SE16 3LR'
    delivery_common_comment = 'comment'
    place_id = 'some_place_id'
    floor = '1'
    flat = '5'
    house = '95B'
    street = 'Усачева'
    city = 'Москва'
    country = 'Россия'
    app_info = 'app_ver1=2,app_brand=yataxi,app_name=web'
    status = 'closed'
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
    location = [10.0, 20.0]
    promocode = 'late delivery'
    promocode_valid = True
    promocode_sum = '120'
    personal_email_id = 'personal_email_id'
    vip_type = consts.VIP_TYPE
    due = '2020-05-25T17:55:45+0000'
    idempotency_token = 'idem0'
    locale = 'ru'
    offer_id = 'offer-id-1'
    user_info = 'user_info-1'

    grocery_depots.add_depot(legacy_depot_id=depot_id)

    grocery_cold_storage.set_orders_response(
        items=[
            {
                'item_id': GROCERY_ORDER_ID,
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
                'meet_outside': meet_outside,
                'no_door_call': no_door_call,
                'postal_code': postal_code,
                'delivery_common_comment': delivery_common_comment,
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
                'location': location,
                'promocode': promocode,
                'promocode_valid': promocode_valid,
                'promocode_sum': promocode_sum,
                'vip_type': vip_type,
                'personal_email_id': personal_email_id,
                'due': due,
                'idempotency_token': idempotency_token,
                'locale': locale,
                'offer_id': offer_id,
                'user_info': user_info,
            },
        ],
    )

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/admin/info',
    )
    def _admin_info(request):
        return {
            'dispatches': [
                {
                    'dispatch_id': dispatch_id,
                    'cargo_details': [
                        {
                            'claim_id': 'claim_id_2',
                            'claim_status': 'new',
                            'is_current_claim': True,
                        },
                        {
                            'claim_id': 'claim_id_1',
                            'claim_status': 'cancelled',
                        },
                    ],
                },
            ],
        }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
    )

    assert response.status_code == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    order = orders[0]

    def _datetime_equal(response, request):
        return response == request[:-2] + ':' + request[-2:]

    assert order['order_id'] == order_id
    assert order['cart_id'] == cart_id
    assert order['short_order_id'] == short_order_id
    assert order['order_version'] == order_version
    assert order['taxi_user_id'] == taxi_user_id
    assert str(order['tips']) == tips
    assert order['courier_name'] == dispatch_courier_name
    assert order['client_price'] == client_price
    assert order['depot_id'] == depot_id
    assert order['personal_phone_id'] == personal_phone_id
    assert order['yandex_uid'] == yandex_uid
    assert order['phone_id'] == phone_id
    assert order['eats_user_id'] == eats_user_id
    assert order['eats_order_id'] == eats_order_id
    assert _datetime_equal(order['created'], created)

    assert order['status'] == status
    assert order['cancel_reason_type'] == cancel_reason_type
    assert order['cancel_reason_message'] == cancel_reason_message
    assert order['city'] == city
    assert order['street'] == street
    assert order['flat'] == flat
    assert order['place_id'] == place_id
    assert order['wms_reserve_status'] == wms_reserve_status
    assert order['hold_money_status'] == hold_money_status
    assert order['close_money_status'] == close_money_status
    assert order['assembling_status'] == assembling_status
    assert order['currency'] == currency
    assert order['app_info'] == app_info
    assert order['dispatch_id'] == dispatch_id
    assert order['dispatch_status'] == dispatch_status
    assert order['dispatch_cargo_status'] == dispatch_cargo_status
    assert order['dispatch_delivery_eta'] == dispatch_delivery_eta
    assert _datetime_equal(
        order['dispatch_start_delivery_ts'], dispatch_start_delivery_ts,
    )
    assert order['order_revision'] == order_revision
    assert order['billing_flow'] == billing_flow

    assert order['doorbell_name'] == doorbell_name[0]
    assert order['doorcode_extra'] == doorcode_extra[0]
    assert order['building_name'] == building_name[0]
    assert order['left_at_door'] == left_at_door[0]
    assert order['meet_outside'] == meet_outside
    assert order['no_door_call'] == no_door_call
    assert order['postal_code'] == postal_code
    assert order['delivery_common_comment'] == delivery_common_comment
    assert order['location'] == location

    assert set(order['allowed_actions']) == {
        'promocode',
        'refund',
        'partial_refund',
    }
    assert order['order_admin_info'] == 'order_finished'

    assert order['grocery_order_status'] == 'closed'
    assert order['user_fraud'] == 'Fraud'
    assert order['order_fraud'] == 'Fraud'
    assert order['promocode'] == promocode
    assert order['promocode_valid'] == promocode_valid
    assert order['promocode_sum'] == float(promocode_sum)
    assert order['vip_type'] == vip_type
    assert order['personal_email_id'] == personal_email_id


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage_specific_order(
        taxi_grocery_orders,
        pgsql,
        mockserver,
        grocery_depots,
        load_json,
        antifraud,
):
    order_id = '9dc2300a4d004a9e9d854a9f5e45816a-grocery'
    depot_id = '60287'

    class Context:
        request_type = 'order'  # 'order' -> 'history' -> None

    context = Context()

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/orders',
    )
    def cold_storage(request):
        body = request.json

        if context.request_type == 'order':
            context.request_type = 'history'

            assert body == load_json('suggest/cold_storage_order_request.json')
            return mockserver.make_response(
                json=load_json('suggest/cold_storage_order_response.json'),
            )
        if context.request_type == 'history':
            context.request_type = None
            assert body == load_json(
                'suggest/cold_storage_history_request.json',
            )
            return mockserver.make_response(
                json=load_json('suggest/cold_storage_history_response.json'),
            )

        raise RuntimeError('unexpected request')

    grocery_depots.add_depot(
        legacy_depot_id=depot_id, timezone=consts.SPECIFIC_ORDER_TIMEZONE,
    )

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json={'order_id': order_id},
    )

    assert response.status_code == 200
    assert cold_storage.times_called == 2
    assert context.request_type is None


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
                'due': '2020-05-25T17:20:45+0000',
                'idempotency_token': 'idem-0',
                'locale': 'en',
                'offer_id': 'offer-id-1',
                'user_info': 'some-user-info-1',
            }
            for order_id in order_ids[5:]
        ],
    )
    grocery_order_log.set_order_ids_response(order_ids)

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
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
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
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


@pytest.mark.now('2020-05-25T17:43:45+03:00')
@pytest.mark.parametrize('bad_orders_type', ['all', 'failed', 'not_closed'])
async def test_active_orders_filters(
        taxi_grocery_orders,
        bad_orders_type,
        mocked_time,
        _create_various_active_orders,
        antifraud,
):
    region_id = 100
    _create_various_active_orders(region_id)

    request_json = {'bad_orders_type': bad_orders_type, 'region_id': region_id}

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
    )

    assert response.status_code == 200

    response_orders = response.json()['orders']

    number_of_orders = len(response_orders)

    if bad_orders_type == 'failed':
        assert number_of_orders == 5
    if bad_orders_type == 'not_closed':
        assert number_of_orders == 5
    if bad_orders_type == 'all':
        assert number_of_orders == 11

    if response_orders:
        created = response_orders[0]['created']

    for order in response_orders:
        assert datetime.datetime.fromisoformat(
            created,
        ) >= datetime.datetime.fromisoformat(order['created'])
        created = order['created']
        if bad_orders_type == 'failed':
            assert (
                order['status'] == 'canceled'
                or order['status'] == 'pending_cancel'
            )
        if bad_orders_type == 'not_closed':
            assert (
                order['status'] != 'closed' and order['status'] != 'canceled'
            )
        assert order['vip_type'] == consts.VIP_TYPE
        assert (
            order['personal_email_id']
            == consts.SPECIFIC_ORDER['personal_email_id']
        )


@pytest.mark.parametrize(
    'not_closed_filter',
    ['orders_in_depot', 'dispatched_orders', 'finishing_orders'],
)
async def test_not_closed_active_orders_filters(
        taxi_grocery_orders,
        _create_various_active_orders,
        not_closed_filter,
        antifraud,
):
    region_id = 100
    _create_various_active_orders(region_id)

    request_json = {
        'orders_type': 'not_closed',
        'region_id': region_id,
        'not_closed_orders_filter': not_closed_filter,
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
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
        _create_various_active_orders,
        canceled_orders_filter,
        antifraud,
):
    region_id = 100
    _create_various_active_orders(region_id)

    request_json = {
        'orders_type': 'canceled',
        'region_id': region_id,
        'canceled_orders_filter': canceled_orders_filter,
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request_json, headers=consts.HEADER,
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
        '/admin/orders/v1/suggest', json=request, headers=consts.HEADER,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == orders_count
    for order in orders:
        if depot_id is not None:
            assert order['depot_id'] == depot_id
        if region_id is not None:
            assert order['region_id'] == region_id


@pytest.mark.parametrize('limit', [None, 1000])
async def test_default_pagination(
        taxi_grocery_orders, pgsql, limit, grocery_depots, antifraud,
):
    orders = [models.Order(pgsql=pgsql) for _ in range(101)]

    for idx, order in enumerate(orders):
        order_id = str(idx)
        order.depot_id = str(idx)
        grocery_depots.add_depot(legacy_depot_id=order.depot_id)
        some_cart_id_part = '00000000-0000-0000-0000-d98013100'
        idempotency_token = 'sql-idempotency-token-'

        cart_id = some_cart_id_part + '{:03d}'.format(idx)

        order.upsert(
            order_id=order_id,
            eats_order_id='eats_order_id' + str(idx),
            short_order_id=str(6 + idx * 10),
            cart_id=cart_id,
            region_id=100,
            depot_id=order.depot_id,
            idempotency_token=idempotency_token + str(idx),
        )
    request = {'region_id': 100}
    if limit:
        request['limit'] = limit
    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/suggest', json=request, headers=consts.HEADER,
    )
    orders = response.json()['orders']
    assert len(orders) == 50


async def test_dispatch_fields(
        taxi_grocery_orders, pgsql, grocery_depots, antifraud,
):
    order_with_dispatch = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
    )
    grocery_depots.add_depot(legacy_depot_id=order_with_dispatch.depot_id)
    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=str(uuid.uuid4()),
        dispatch_status='accepted',
        dispatch_cargo_status='performer_found',
        dispatch_delivery_eta=600,
        dispatch_start_delivery_ts='2020-03-03T10:04:37.646Z',
    )
    order_with_dispatch.upsert(dispatch_status_info=dispatch_status_info)

    order = await _get_order(taxi_grocery_orders, order_with_dispatch.order_id)

    assert order['dispatch_id'] == dispatch_status_info.dispatch_id
    assert order['dispatch_status'] == dispatch_status_info.dispatch_status
    assert (
        order['dispatch_cargo_status']
        == dispatch_status_info.dispatch_cargo_status
    )
    assert (
        order['dispatch_delivery_eta']
        == dispatch_status_info.dispatch_delivery_eta
    )
    assert (
        order['dispatch_start_delivery_ts'] == '2020-03-03T10:04:37.646+00:00'
    )

    order_without_dispatch = models.Order(
        pgsql,
        order_id='2',
        cart_id='00000000-0000-0000-0000-d98013100501',
        idempotency_token='my-idempotency-token1',
        dispatch_status_info=models.DispatchStatusInfo(
            None, None, None, None, None,
        ),
    )

    order = await _get_order(
        taxi_grocery_orders, order_without_dispatch.order_id,
    )

    assert 'dispatch_id' not in order
    assert 'dispatch_status' not in order
    assert 'dispatch_cargo_status' not in order
    assert 'dispatch_delivery_eta' not in order
    assert 'dispatch_start_delivery_ts' not in order


QUERIES_ORDER_STATUS = pytest.mark.parametrize(
    ('status', 'dispatch_status', 'expected_grocery_order_status'),
    [
        ('reserving', None, 'created'),
        ('assembling', None, 'assembling'),
        ('assembled', None, 'assembled'),
        ('delivering', 'created', 'assembled'),
        ('delivering', 'delivering', 'delivering'),
        ('delivering', 'closed', 'closed'),
        ('canceled', None, 'closed'),
    ],
)


@QUERIES_ORDER_STATUS
async def test_order_grocery_status(
        taxi_grocery_orders,
        grocery_depots,
        pgsql,
        status,
        dispatch_status,
        expected_grocery_order_status,
        antifraud,
):
    order = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        status=status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_status=dispatch_status,
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    order = await _get_order(taxi_grocery_orders, order.order_id)
    assert order['grocery_order_status'] == expected_grocery_order_status


QUERIES_ORDERS_STATES = pytest.mark.parametrize(
    (
        'assembling_status',
        'wms_reserve_status',
        'hold_money_status',
        'close_money_status',
    ),
    [
        ('assembled', 'success', 'success', 'success'),
        ('failed', 'failed', 'failed', 'failed'),
    ],
)


@QUERIES_ORDERS_STATES
async def test_order_state(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        assembling_status,
        wms_reserve_status,
        hold_money_status,
        close_money_status,
        antifraud,
):
    assembled_order = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        state=models.OrderState(
            assembling_status=assembling_status,
            wms_reserve_status=wms_reserve_status,
            hold_money_status=hold_money_status,
            close_money_status=close_money_status,
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=assembled_order.depot_id)

    order = await _get_order(taxi_grocery_orders, assembled_order.order_id)
    assert order['assembling_status'] == assembling_status
    assert order['wms_reserve_status'] == wms_reserve_status
    assert order['hold_money_status'] == hold_money_status
    assert order['close_money_status'] == close_money_status


ORDER_ADMIN_INFO = pytest.mark.parametrize(
    (
        'status',
        'desired_status',
        'wms_reserve_status',
        'hold_money_status',
        'close_money_status',
        'assembling_status',
        'dispatch_status',
        'cargo_status',
        'expected_admin_info',
    ),
    consts.ADMIN_INFO_STATUSES,
)


@ORDER_ADMIN_INFO
async def test_order_admin_info(
        taxi_grocery_orders,
        pgsql,
        status,
        desired_status,
        wms_reserve_status,
        hold_money_status,
        close_money_status,
        assembling_status,
        dispatch_status,
        cargo_status,
        expected_admin_info,
        grocery_depots,
        antifraud,
):
    order = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        state=models.OrderState(
            wms_reserve_status=wms_reserve_status,
            hold_money_status=hold_money_status,
            close_money_status=close_money_status,
            assembling_status=assembling_status,
        ),
        status=status,
        desired_status=desired_status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_status=dispatch_status,
            dispatch_cargo_status=cargo_status,
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    order = await _get_order(taxi_grocery_orders, order.order_id)
    assert order['order_admin_info'] == expected_admin_info


@pytest.mark.parametrize(
    'status,desired_status,close_money_status,'
    'dispatch_cargo_status,actions',
    [
        ('draft', None, None, None, {'cancel', 'correct', 'promocode'}),
        ('assembling', 'canceled', None, None, {'promocode', 'cancel'}),
        (
            'delivering',
            None,
            'success',
            'delivery_arrived',
            {'promocode', 'close', 'refund', 'partial_refund', 'cancel'},
        ),
        (
            'assembled',
            None,
            'success',
            None,
            {'promocode', 'cancel', 'refund', 'partial_refund'},
        ),
        (
            'closed',
            None,
            None,
            None,
            {'promocode', 'refund', 'partial_refund', 'cancel'},
        ),
        (
            'closed',
            None,
            'success',
            None,
            {'promocode', 'refund', 'partial_refund', 'cancel'},
        ),
        ('canceled', None, None, None, {'promocode'}),
    ],
)
async def test_admin_actions(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        status,
        desired_status,
        close_money_status,
        dispatch_cargo_status,
        actions,
        antifraud,
):
    order = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        state=models.OrderState(close_money_status=close_money_status),
        status=status,
        desired_status=desired_status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_status='delivering',
            dispatch_cargo_status=dispatch_cargo_status,
        ),
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    order = await _get_order(taxi_grocery_orders, order.order_id)
    assert set(order['allowed_actions']) == actions


async def test_cargo_claims_info_in_grocery_dispatch_flow(
        mockserver, taxi_grocery_orders, pgsql, grocery_depots, antifraud,
):
    dispatch_id = str(uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}'))

    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/admin/info',
    )
    def _admin_info(request):
        return {
            'dispatches': [
                {
                    'dispatch_id': dispatch_id,
                    'cargo_details': [
                        {
                            'claim_id': 'claim_id_2',
                            'claim_status': 'new',
                            'is_current_claim': True,
                        },
                        {
                            'claim_id': 'claim_id_1',
                            'claim_status': 'cancelled',
                        },
                    ],
                },
            ],
        }

    order = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='created',
            dispatch_cargo_status='new',
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    order = await _get_order(taxi_grocery_orders, order.order_id)
    expected_cargo_claims_info = [
        {
            'claim_id': 'claim_id_2',
            'claim_status': 'new',
            'is_current_claim': True,
        },
        {'claim_id': 'claim_id_1', 'claim_status': 'cancelled'},
    ]
    assert order['dispatch_flow'] == 'grocery_dispatch'
    assert order['cargo_claims_info'] == expected_cargo_claims_info


@pytest.mark.config(GROCERY_ORDERS_ALLOW_TO_CANCEL_DELIVERING_ORDERS=True)
async def test_can_cancel_on_grocery_dispatch(
        taxi_grocery_orders, pgsql, grocery_depots, antifraud,
):
    order = models.Order(
        pgsql,
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_status='delivering', dispatch_cargo_status='pickuped',
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    order = await _get_order(taxi_grocery_orders, order.order_id)
    assert 'cancel' in order['allowed_actions']


@pytest.mark.parametrize(
    'is_banned, is_suspicious', [(True, False), (False, False), (False, True)],
)
async def test_antifraud(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        antifraud,
        is_banned,
        is_suspicious,
):
    order = models.Order(
        pgsql,
        personal_phone_id='1111',
        order_id='1',
        cart_id='00000000-0000-0000-0000-d98013100500',
        idempotency_token='my-idempotency-token',
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_status='delivering', dispatch_cargo_status='pickuped',
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    antifraud.set_is_fraud(is_banned)
    antifraud.set_is_suspicious(is_suspicious)
    antifraud.check_user_antifraud_request(
        personal_phone_id=order.personal_phone_id,
    )
    antifraud.check_order_antifraud_request(order_nr=order.order_id)

    order = await _get_order(taxi_grocery_orders, order.order_id)

    assert antifraud.times_user_antifraud_called() == 1
    assert antifraud.times_order_antifraud_called() == 1

    if is_banned:
        assert order['order_fraud'] == 'Fraud'
        assert order['user_fraud'] == 'Fraud'
    elif is_suspicious:
        assert order['order_fraud'] == 'Unsure'
        assert order['user_fraud'] == 'Unsure'
    else:
        assert order['order_fraud'] == 'Clear'
        assert order['user_fraud'] == 'Clear'


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
        '/admin/orders/v1/suggest',
        json=request_json,
        headers={'X-Yandex-Login': support_login},
    )

    assert response.status_code == 200
    assert response.json()['is_personal'] == is_personal
