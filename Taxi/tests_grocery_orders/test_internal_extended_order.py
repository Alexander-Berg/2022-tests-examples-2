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


def _create_specific_order(pgsql, is_success=True):
    if is_success:
        _create_closed_order_history(pgsql, consts.SPECIFIC_ORDER['order_id'])
    else:
        _create_canceled_order_history(
            pgsql, consts.SPECIFIC_ORDER['order_id'],
        )
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
        desired_status=consts.SPECIFIC_ORDER['desired_status'],
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
        currency=consts.SPECIFIC_ORDER['currency'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        order_revision=consts.SPECIFIC_ORDER['order_revision'],
        billing_flow=consts.SPECIFIC_ORDER['billing_flow'],
        locale=consts.SPECIFIC_ORDER['locale'],
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
        vip_type=consts.VIP_TYPE,
        push_notification_enabled=consts.SPECIFIC_ORDER[
            'push_notification_enabled'
        ],
        personal_email_id=consts.SPECIFIC_ORDER['personal_email_id'],
    )


async def _get_orders(taxi_grocery_orders, order_id):
    request_json = {'order_id': order_id}
    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info-extended', json=request_json,
    )
    assert response.status_code == 200
    orders = response.json()
    assert orders
    return orders


@pytest.mark.parametrize('is_success', [True, False])
async def test_basic(taxi_grocery_orders, pgsql, grocery_depots, is_success):
    order = _create_specific_order(pgsql, is_success)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        timezone=consts.SPECIFIC_ORDER_TIMEZONE,
    )
    models.OrderAuthContext(pgsql=pgsql, order_id=order.order_id)

    specific_orders = await _get_orders(taxi_grocery_orders, order.order_id)

    assert specific_orders['order_id'] == consts.SPECIFIC_ORDER['order_id']
    assert specific_orders['cart_id'] == consts.SPECIFIC_ORDER['cart_id']
    assert (
        specific_orders['short_order_id']
        == consts.SPECIFIC_ORDER['short_order_id']
    )
    assert (
        specific_orders['order_version']
        == consts.SPECIFIC_ORDER['order_version']
    )
    assert (
        specific_orders['taxi_user_id']
        == consts.SPECIFIC_ORDER['taxi_user_id']
    )
    assert specific_orders['tips'] == consts.SPECIFIC_ORDER['tips']
    assert int(specific_orders['client_price']) == int(
        consts.SPECIFIC_ORDER['client_price'],
    )
    assert specific_orders['depot_id'] == consts.SPECIFIC_ORDER['depot_id']
    assert (
        specific_orders['personal_phone_id']
        == consts.SPECIFIC_ORDER['personal_phone_id']
    )
    assert specific_orders['yandex_uid'] == consts.SPECIFIC_ORDER['yandex_uid']
    assert specific_orders['phone_id'] == consts.SPECIFIC_ORDER['phone_id']
    assert (
        specific_orders['eats_user_id']
        == consts.SPECIFIC_ORDER['eats_user_id']
    )
    assert (
        specific_orders['eats_order_id']
        == consts.SPECIFIC_ORDER['eats_order_id']
    )
    assert specific_orders['created'] == consts.SPECIFIC_ORDER['created']

    assert specific_orders['status'] == consts.SPECIFIC_ORDER['status']
    assert (
        specific_orders['desired_status']
        == consts.SPECIFIC_ORDER['desired_status']
    )
    assert (
        specific_orders['cancel_reason_type']
        == consts.SPECIFIC_ORDER['cancel_reason_type']
    )
    assert (
        specific_orders['cancel_reason_message']
        == consts.SPECIFIC_ORDER['cancel_reason_message']
    )
    assert specific_orders['city'] == consts.SPECIFIC_ORDER['city']
    assert specific_orders['street'] == consts.SPECIFIC_ORDER['street']
    assert specific_orders['flat'] == consts.SPECIFIC_ORDER['flat']
    assert specific_orders['floor'] == consts.SPECIFIC_ORDER['floor']
    assert specific_orders['place_id'] == consts.SPECIFIC_ORDER['place_id']
    assert specific_orders['doorcode'] == consts.SPECIFIC_ORDER['doorcode']
    assert (
        specific_orders['doorcode_extra']
        == consts.SPECIFIC_ORDER['doorcode_extra']
    )
    assert (
        specific_orders['building_name']
        == consts.SPECIFIC_ORDER['building_name']
    )
    assert (
        specific_orders['doorbell_name']
        == consts.SPECIFIC_ORDER['doorbell_name']
    )
    assert (
        specific_orders['left_at_door']
        == consts.SPECIFIC_ORDER['left_at_door']
    )
    assert (
        specific_orders['meet_outside']
        == consts.SPECIFIC_ORDER['meet_outside']
    )
    assert (
        specific_orders['no_door_call']
        == consts.SPECIFIC_ORDER['no_door_call']
    )
    assert (
        specific_orders['postal_code'] == consts.SPECIFIC_ORDER['postal_code']
    )
    assert (
        specific_orders['delivery_common_comment']
        == consts.SPECIFIC_ORDER['delivery_common_comment']
    )
    assert (
        specific_orders['wms_reserve_status']
        == consts.SPECIFIC_ORDER['wms_reserve_status']
    )
    assert (
        specific_orders['hold_money_status']
        == consts.SPECIFIC_ORDER['hold_money_status']
    )
    assert (
        specific_orders['close_money_status']
        == consts.SPECIFIC_ORDER['close_money_status']
    )
    assert (
        specific_orders['assembling_status']
        == consts.SPECIFIC_ORDER['assembling_status']
    )
    assert specific_orders['currency'] == consts.SPECIFIC_ORDER['currency']
    assert specific_orders['app_info'] == consts.SPECIFIC_ORDER['app_info']
    assert (
        specific_orders['dispatch_id'] == consts.SPECIFIC_ORDER['dispatch_id']
    )
    assert (
        specific_orders['dispatch_status']
        == consts.SPECIFIC_ORDER['dispatch_status']
    )
    assert (
        specific_orders['dispatch_cargo_status']
        == consts.SPECIFIC_ORDER['dispatch_cargo_status']
    )
    assert (
        specific_orders['dispatch_delivery_eta']
        == consts.SPECIFIC_ORDER['dispatch_delivery_eta']
    )
    assert (
        specific_orders['order_revision']
        == consts.SPECIFIC_ORDER['order_revision']
    )
    assert (
        specific_orders['billing_flow']
        == consts.SPECIFIC_ORDER['billing_flow']
    )
    assert (
        specific_orders['edit_status'] == consts.SPECIFIC_ORDER['edit_status']
    )
    if is_success:
        _check_closed_order_history(specific_orders['order_history'])
    else:
        _check_canceled_order_history(specific_orders['order_history'])
    assert specific_orders['vip_type'] == consts.SPECIFIC_ORDER['vip_type']
    assert (
        specific_orders['push_notification_enabled']
        == consts.SPECIFIC_ORDER['push_notification_enabled']
    )
    assert (
        specific_orders['personal_email_id']
        == consts.SPECIFIC_ORDER['personal_email_id']
    )

    cargo_dispatch = consts.SPECIFIC_ORDER['dispatch_status_meta'][
        'cargo_dispatch'
    ]
    assert specific_orders['batch'] == cargo_dispatch['dispatch_in_batch']
    assert (
        specific_orders['batch_order_num'] == cargo_dispatch['batch_order_num']
    )
    assert (
        specific_orders['dispatch_delivery_type']
        == cargo_dispatch['dispatch_delivery_type']
    )


SHORT_ORDER_ID = 'short_order_id'
GROCERY_ORDER_ID = '7881317eb10d4ecda902fe21587f0df3-grocery'
GROCERY_SECOND_ORDER_ID = '7771317eb10d4ecda902fe21587f0df3-grocery'


def _to_iso_format(date, time_zone='+00:00'):
    return date.isoformat() + time_zone


DELTA = datetime.timedelta(hours=3, minutes=2)
TIMEPOINT_A = datetime.datetime(2020, 10, 30, 11, 19)
TIMEPOINT_B = datetime.datetime(2020, 10, 31, 11, 19)


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
        dispatch_id='1337',
        dispatch_status='accepted',
        dispatch_cargo_status='performer_found',
        dispatch_delivery_eta=600,
        dispatch_start_delivery_ts='2020-03-03T10:04:37.646Z',
    )
    order_with_dispatch.upsert(dispatch_status_info=dispatch_status_info)

    order = await _get_orders(
        taxi_grocery_orders, order_with_dispatch.order_id,
    )

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

    order = await _get_orders(
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

    orders = await _get_orders(taxi_grocery_orders, order.order_id)
    assert orders['grocery_order_status'] == expected_grocery_order_status


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

    order = await _get_orders(taxi_grocery_orders, assembled_order.order_id)
    assert order['assembling_status'] == assembling_status
    assert order['wms_reserve_status'] == wms_reserve_status
    assert order['hold_money_status'] == hold_money_status
    assert order['close_money_status'] == close_money_status


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
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    order = await _get_orders(taxi_grocery_orders, order.order_id)


@pytest.mark.config(GROCERY_ORDERS_USE_COLD_STORAGE=True)
async def test_cold_storage_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cold_storage,
        grocery_depots,
        grocery_order_log,
        antifraud,
):
    order_id = GROCERY_ORDER_ID

    request_json = {'order_id': order_id}

    tips_status = 'pending'
    tips = '1.23'
    comment = 'До двери'
    created = '2020-05-25T17:20:45+0000'
    updated = '2020-05-25T17:35:45+0000'
    finished = '2020-05-25T17:43:45+0000'
    dispatch_start_delivery_ts = '2020-05-25T17:33:45+0000'
    dispatch_delivery_eta = 17
    dispatch_courier_name = 'Камешко Александр Александрович'
    dispatch_courier_first_name = 'Александр'
    dispatch_cargo_status = 'new'
    dispatch_status = 'delivering'
    dispatch_id = '12345'
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
    short_order_id = SHORT_ORDER_ID
    order_version = 13
    order_revision = 2
    billing_flow = 'grocery_payments'
    dispatch_flow = 'grocery_dispatch'
    location = [10.0, 20.0]
    promocode = 'late delivery'
    promocode_valid = True
    promocode_sum = '120'
    vip_type = consts.VIP_TYPE
    push_notification_enabled = True
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
                'dispatch_courier_first_name': dispatch_courier_first_name,
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
                'push_notification_enabled': push_notification_enabled,
                'due': due,
                'idempotency_token': idempotency_token,
                'locale': locale,
                'offer_id': offer_id,
                'user_info': user_info,
            },
        ],
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info-extended',
        json=request_json,
        headers=consts.HEADER,
    )

    assert response.status_code == 200

    order = response.json()

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
    assert order['floor'] == floor
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

    assert order['grocery_order_status'] == 'closed'
    assert order['promocode'] == promocode
    assert order['promocode_valid'] == promocode_valid
    assert order['promocode_sum'] == float(promocode_sum)
    assert order['vip_type'] == vip_type
    assert order['push_notification_enabled'] == push_notification_enabled


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
        '/internal/v1/get-info-extended', json={'order_id': order_id},
    )

    assert response.status_code == 200
    assert cold_storage.times_called == 2
    assert context.request_type is None


@pytest.mark.parametrize('use_short_order_id', [True, False])
@pytest.mark.parametrize('feedback_status', ['refused', 'submitted'])
async def test_feedback(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        use_short_order_id,
        feedback_status,
):
    if feedback_status == 'submitted':
        evaluation = consts.SPECIFIC_FEEDBACK['evaluation']
        feedback_options = consts.SPECIFIC_FEEDBACK['feedback_options']
        feedback_comment = consts.SPECIFIC_FEEDBACK['feedback_comment']
    else:
        evaluation = None
        feedback_options = None
        feedback_comment = None

    order = models.Order(
        pgsql,
        order_id=consts.SPECIFIC_ORDER['order_id'],
        short_order_id=consts.SPECIFIC_ORDER['short_order_id'],
        status='closed',
        feedback_status=feedback_status,
        evaluation=evaluation,
        feedback_options=feedback_options,
        feedback_comment=feedback_comment,
    )

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        timezone=consts.SPECIFIC_ORDER_TIMEZONE,
    )
    order_id = (
        order.order_id if not use_short_order_id else order.short_order_id
    )

    specific_orders = await _get_orders(taxi_grocery_orders, order_id)

    assert specific_orders['order_id'] == consts.SPECIFIC_ORDER['order_id']
    assert (
        specific_orders['short_order_id']
        == consts.SPECIFIC_ORDER['short_order_id']
    )
    assert specific_orders['feedback_status'] == feedback_status
    if feedback_status == 'submitted':
        assert specific_orders['evaluation'] == evaluation
        assert specific_orders['feedback_options'] == feedback_options
        assert specific_orders['feedback_comment'] == feedback_comment
    else:
        assert 'evaluation' not in specific_orders
        assert 'feedback_options' not in specific_orders
        assert 'feedback_comment' not in specific_orders
