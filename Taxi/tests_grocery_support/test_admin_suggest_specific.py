import pytest

from . import admin_orders_suggest_consts as consts
from . import experiments
from . import models

SHORT_ORDER_ID = '234902-234-9430'
GROCERY_ORDER_ID = '7881317eb10d4ecda902fe21587f0df3-grocery'
GROCERY_SECOND_ORDER_ID = '7771317eb10d4ecda902fe21587f0df3-grocery'

DEFAULT_EXPIRATION_TIME = 2400  # config default
DEFAULT_MAX_ORDER_IDS = 50  # config default


async def _get_orders(taxi_grocery_orders, order_id, header=None):
    if header is None:
        header = consts.HEADER
    header['X-Remote-IP'] = '172.99.23.44'
    request_json = {'order_id': order_id}
    response = await taxi_grocery_orders.post(
        '/admin/v1/suggest/specific', json=request_json, headers=header,
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert orders
    return orders


@pytest.fixture(name='add_depot', autouse=True)
def add_depot(grocery_depots):
    grocery_depots.add_depot(
        depot_test_id=int(consts.SPECIFIC_ORDER['depot_id']),
        legacy_depot_id=consts.SPECIFIC_ORDER['depot_id'],
        timezone=consts.SPECIFIC_ORDER_TIMEZONE,
    )


def _compare_orders(lhs_order, rhs_order):
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
    assert lhs_order['wms_reserve_status'] == rhs_order['wms_reserve_status']
    assert lhs_order['hold_money_status'] == rhs_order['hold_money_status']
    assert lhs_order['close_money_status'] == rhs_order['close_money_status']
    assert lhs_order['assembling_status'] == rhs_order['assembling_status']
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
    assert lhs_order['edit_status'] == rhs_order['edit_status']
    assert lhs_order['order_history'] == rhs_order['order_history']
    assert lhs_order['vip_type'] == rhs_order['vip_type']
    assert (
        lhs_order['push_notification_enabled']
        == rhs_order['push_notification_enabled']
    )
    assert set(lhs_order['allowed_actions']) == set(
        rhs_order['allowed_actions'],
    )


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
@pytest.mark.parametrize(
    'is_banned, is_suspicious, good_client_story',
    [(True, False, True), (False, False, False), (False, True, None)],
)
async def test_specific_order(
        taxi_grocery_support,
        header,
        expected_translation,
        grocery_orders,
        antifraud,
        is_banned,
        is_suspicious,
        good_client_story,
):
    order = grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        eats_order_id=consts.SPECIFIC_ORDER['eats_order_id'],
        taxi_user_id=consts.SPECIFIC_ORDER['taxi_user_id'],
        eats_user_id=consts.SPECIFIC_ORDER['eats_user_id'],
        yandex_uid=consts.SPECIFIC_ORDER['yandex_uid'],
        session=consts.SPECIFIC_ORDER['session'],
        phone_id=consts.SPECIFIC_ORDER['phone_id'],
        personal_phone_id=consts.SPECIFIC_ORDER['personal_phone_id'],
        status=consts.SPECIFIC_ORDER['status'],
        desired_status=consts.SPECIFIC_ORDER['desired_status'],
        status_updated=consts.SPECIFIC_ORDER['status_updated'],
        country=consts.SPECIFIC_ORDER['country'],
        city=consts.SPECIFIC_ORDER['city'],
        street=consts.SPECIFIC_ORDER['street'],
        house=consts.SPECIFIC_ORDER['house'],
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
        entrance=consts.SPECIFIC_ORDER['entrance'],
        postal_code=consts.SPECIFIC_ORDER['postal_code'],
        created=consts.SPECIFIC_ORDER['created'],
        updated=consts.SPECIFIC_ORDER['updated'],
        order_version=consts.SPECIFIC_ORDER['order_version'],
        wms_reserve_status=consts.SPECIFIC_ORDER['wms_reserve_status'],
        hold_money_status=consts.SPECIFIC_ORDER['hold_money_status'],
        close_money_status=consts.SPECIFIC_ORDER['close_money_status'],
        assembling_status=consts.SPECIFIC_ORDER['assembling_status'],
        cancel_reason_type=consts.SPECIFIC_ORDER['cancel_reason_type'],
        cancel_reason_message=consts.SPECIFIC_ORDER['cancel_reason_message'],
        region_id=consts.SPECIFIC_ORDER['region_id'],
        client_price=consts.SPECIFIC_ORDER['client_price'],
        currency=consts.SPECIFIC_ORDER['currency'],
        promocode=consts.SPECIFIC_ORDER['promocode'],
        promocode_valid=consts.SPECIFIC_ORDER['promocode_valid'],
        promocode_sum=consts.SPECIFIC_ORDER['promocode_sum'],
        short_order_id=consts.SPECIFIC_ORDER['short_order_id'],
        grocery_flow_version=consts.SPECIFIC_ORDER['grocery_flow_version'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        cart_id=consts.SPECIFIC_ORDER['cart_id'],
        dispatch_id=consts.SPECIFIC_ORDER['dispatch_id'],
        dispatch_status=consts.SPECIFIC_ORDER['dispatch_status'],
        dispatch_cargo_status=consts.SPECIFIC_ORDER['dispatch_cargo_status'],
        dispatch_delivery_eta=consts.SPECIFIC_ORDER['dispatch_delivery_eta'],
        dispatch_start_delivery_ts=consts.SPECIFIC_ORDER[
            'dispatch_start_delivery_ts'
        ],
        comment=consts.SPECIFIC_ORDER['comment'],
        tips=consts.SPECIFIC_ORDER['tips'],
        location=consts.SPECIFIC_ORDER['location'],
        tips_status=consts.SPECIFIC_ORDER['tips_status'],
        grocery_order_status=consts.SPECIFIC_ORDER['grocery_order_status'],
        courier_name=consts.SPECIFIC_ORDER['courier_name'],
        order_revision=consts.SPECIFIC_ORDER['order_revision'],
        billing_flow=consts.SPECIFIC_ORDER['billing_flow'],
        depot_address=consts.SPECIFIC_ORDER['depot_address'],
        order_history=[],
        items=consts.SPECIFIC_ORDER['items'],
        dispatch_flow=consts.SPECIFIC_ORDER['dispatch_flow'],
        timezone=consts.SPECIFIC_ORDER['timezone'],
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
        batch=consts.SPECIFIC_ORDER_CARGO_DISPATCH['dispatch_in_batch'],
        batch_order_num=consts.SPECIFIC_ORDER_CARGO_DISPATCH[
            'batch_order_num'
        ],
        vip_type=consts.SPECIFIC_ORDER['vip_type'],
        user_ip=consts.SPECIFIC_ORDER['user_ip'],
        push_notification_enabled=True,
        feedback_status=consts.SPECIFIC_FEEDBACK['feedback_status'],
        evaluation=consts.SPECIFIC_FEEDBACK['evaluation'],
        feedback_options=consts.SPECIFIC_FEEDBACK['feedback_options'],
        feedback_comment=consts.SPECIFIC_FEEDBACK['feedback_comment'],
        dispatch_delivery_type=consts.SPECIFIC_ORDER_CARGO_DISPATCH[
            'dispatch_delivery_type'
        ],
    )
    order['depot_id'] = consts.SPECIFIC_ORDER['depot_id']

    short_address = '{}, {} {} {}'.format(
        order['city'], order['street'], order['house'], order['flat'],
    )
    antifraud.check_order_antifraud_request(
        order_nr=order['order_id'], short_address=short_address,
    )
    antifraud.set_is_fraud(is_banned)
    antifraud.set_is_suspicious(is_suspicious)
    antifraud.set_lavka_users(lavka_users=good_client_story)

    specific_orders = await taxi_grocery_support.post(
        '/admin/v1/suggest/specific',
        json={'order_id': GROCERY_ORDER_ID},
        headers=header,
    )
    specific_orders = specific_orders.json()['orders']
    assert specific_orders[0]['order_history'] == []

    expected_order = consts.SPECIFIC_ORDER
    expected_order['order_id'] = GROCERY_ORDER_ID
    _compare_orders(specific_orders[0], expected_order)
    assert 'user_name' in specific_orders[0]
    assert 'has_ya_plus' in specific_orders[0]
    assert (
        specific_orders[0]['cancel_reason_description'] == expected_translation
    )

    assert (
        specific_orders[0]['batch']
        == consts.SPECIFIC_ORDER_CARGO_DISPATCH['dispatch_in_batch']
    )
    assert (
        specific_orders[0]['batch_order_num']
        == consts.SPECIFIC_ORDER_CARGO_DISPATCH['batch_order_num']
    )
    assert (
        specific_orders[0]['dispatch_delivery_type']
        == consts.SPECIFIC_ORDER_CARGO_DISPATCH['dispatch_delivery_type']
    )

    assert (
        specific_orders[0]['feedback_status']
        == consts.SPECIFIC_FEEDBACK['feedback_status']
    )
    assert (
        specific_orders[0]['evaluation']
        == consts.SPECIFIC_FEEDBACK['evaluation']
    )
    assert (
        specific_orders[0]['feedback_options']
        == consts.SPECIFIC_FEEDBACK['feedback_options']
    )
    assert (
        specific_orders[0]['feedback_comment']
        == consts.SPECIFIC_FEEDBACK['feedback_comment']
    )

    for order in specific_orders:
        if is_banned:
            assert order['order_fraud'] == 'Fraud'
            assert order['user_fraud'] == 'Fraud'
        elif is_suspicious:
            assert order['order_fraud'] == 'Unsure'
            assert order['user_fraud'] == 'Unsure'
        else:
            assert order['order_fraud'] == 'Clear'
            assert order['user_fraud'] == 'Clear'
        if good_client_story:
            assert order['good_client_story']
        else:
            assert not order['good_client_story']


@pytest.mark.parametrize('order_id, ', [SHORT_ORDER_ID, SHORT_ORDER_ID[-4:]])
async def test_specific_orders(
        taxi_grocery_support,
        grocery_orders,
        antifraud,
        grocery_order_log,
        order_id,
):
    if order_id == SHORT_ORDER_ID:
        order_ids_request_check_data = {
            'short_order_id': order_id,
            'expiration_time': None,
            'max_order_ids': None,
        }
    else:
        order_ids_request_check_data = {
            'short_order_id': '%-{}'.format(order_id),
            'expiration_time': DEFAULT_EXPIRATION_TIME,
            'max_order_ids': DEFAULT_MAX_ORDER_IDS,
        }
    grocery_order_log.set_order_ids_check_data(
        check_data=order_ids_request_check_data,
    )
    grocery_order_log.set_order_ids_response(
        [GROCERY_ORDER_ID, GROCERY_SECOND_ORDER_ID],
    )

    order_first = grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        taxi_user_id=consts.SPECIFIC_ORDER['taxi_user_id'],
        eats_user_id=consts.SPECIFIC_ORDER['eats_user_id'],
        status=consts.SPECIFIC_ORDER['status'],
        place_id=consts.SPECIFIC_ORDER['place_id'],
        order_version=consts.SPECIFIC_ORDER['order_version'],
        grocery_flow_version=consts.SPECIFIC_ORDER['grocery_flow_version'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        cart_id=consts.SPECIFIC_ORDER['cart_id'],
        grocery_order_status=consts.SPECIFIC_ORDER['grocery_order_status'],
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
    )
    order_first['depot_id'] = consts.SPECIFIC_ORDER['depot_id']

    order_second = grocery_orders.add_order(
        order_id=GROCERY_SECOND_ORDER_ID,
        taxi_user_id=consts.SPECIFIC_ORDER['taxi_user_id'],
        eats_user_id=consts.SPECIFIC_ORDER['eats_user_id'],
        status=consts.SPECIFIC_ORDER['status'],
        place_id=consts.SPECIFIC_ORDER['place_id'],
        order_version=consts.SPECIFIC_ORDER['order_version'],
        grocery_flow_version=consts.SPECIFIC_ORDER['grocery_flow_version'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        cart_id=consts.SPECIFIC_ORDER['cart_id'],
        grocery_order_status=consts.SPECIFIC_ORDER['grocery_order_status'],
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
    )
    order_second['depot_id'] = consts.SPECIFIC_ORDER['depot_id']

    antifraud.set_is_fraud(True)
    antifraud.set_is_suspicious(True)

    header = {'Accept-Language': 'ru', 'X-Remote-IP': '127.0.0.1'}
    specific_orders = await taxi_grocery_support.post(
        '/admin/v1/suggest/specific',
        json={'order_id': order_id},
        headers=header,
    )
    specific_orders = specific_orders.json()['orders']

    assert len(specific_orders) == 2
    assert grocery_order_log.times_get_order_ids_called() == 1
    assert specific_orders[0]['order_id'] != specific_orders[1]['order_id']
    for order in specific_orders:
        assert (
            order['order_id'] == GROCERY_ORDER_ID
            or order['order_id'] == GROCERY_SECOND_ORDER_ID
        )


async def test_order_history(taxi_grocery_support, grocery_orders, antifraud):
    order_first = grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        taxi_user_id=consts.SPECIFIC_ORDER['taxi_user_id'],
        eats_user_id=consts.SPECIFIC_ORDER['eats_user_id'],
        status=consts.SPECIFIC_ORDER['status'],
        place_id=consts.SPECIFIC_ORDER['place_id'],
        order_version=consts.SPECIFIC_ORDER['order_version'],
        grocery_flow_version=consts.SPECIFIC_ORDER['grocery_flow_version'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        cart_id=consts.SPECIFIC_ORDER['cart_id'],
        grocery_order_status=consts.SPECIFIC_ORDER['grocery_order_status'],
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
        order_history=consts.EXPECTED_ORDER_HISTORY_VALUES[0],
    )
    order_first['depot_id'] = consts.SPECIFIC_ORDER['depot_id']

    antifraud.set_is_fraud(True)
    antifraud.set_is_suspicious(True)

    header = {'Accept-Language': 'ru', 'X-Remote-IP': '127.0.0.1'}
    specific_orders = await taxi_grocery_support.post(
        '/admin/v1/suggest/specific',
        json={'order_id': GROCERY_ORDER_ID},
        headers=header,
    )
    specific_orders = specific_orders.json()['orders'][0]

    assert (
        specific_orders['order_history']
        == consts.EXPECTED_ORDER_HISTORY_VALUES[0]
    )


@pytest.mark.now(models.NOW)
@experiments.GROCERY_SUPPORT_ALLOWED_ACTIONS_EXPIRATION_TIMES
@pytest.mark.parametrize(
    'status, desired_status, dispatch_status, created, dispatch_delivery_type,'
    ' allowed_actions',
    [
        (
            'draft',
            None,
            None,
            models.ONE_AND_A_HALF_DAYS_BEFORE_NOW,
            None,
            ['promocode', 'correct_remove'],
        ),
        (
            'draft',
            None,
            None,
            models.NOW,
            None,
            [
                'promocode',
                'correct_remove',
                'correct_add',
                'cancel',
                'compensation',
            ],
        ),
        (
            'delivering',
            None,
            None,
            models.HALF_A_DAY_BEFORE_NOW,
            None,
            [
                'promocode',
                'refund',
                'partial_refund',
                'correct_remove',
                'cancel',
                'compensation',
            ],
        ),
        (
            'closed',
            None,
            None,
            models.THREE_DAYS_BEFORE_NOW,
            None,
            ['promocode', 'correct_remove'],
        ),
        (
            'canceled',
            None,
            None,
            models.NOW,
            None,
            ['promocode', 'correct_remove', 'compensation'],
        ),
        (
            'canceled',
            'canceled',
            None,
            models.NOW,
            None,
            ['promocode', 'compensation'],
        ),
        (
            'canceled',
            'canceled',
            'created',
            models.NOW,
            None,
            ['promocode', 'compensation', 'edit_address'],
        ),
        (
            'canceled',
            'canceled',
            'created',
            models.NOW,
            'courier',
            ['promocode', 'compensation', 'edit_address'],
        ),
        (
            'canceled',
            'canceled',
            'created',
            models.NOW,
            'yandex_taxi',
            ['promocode', 'compensation'],
        ),
    ],
)
async def test_allowed_actions(
        taxi_grocery_support,
        grocery_orders,
        antifraud,
        status,
        desired_status,
        dispatch_status,
        created,
        dispatch_delivery_type,
        allowed_actions,
):
    order = grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        taxi_user_id=consts.SPECIFIC_ORDER['taxi_user_id'],
        eats_user_id=consts.SPECIFIC_ORDER['eats_user_id'],
        status=status,
        desired_status=desired_status,
        dispatch_status=dispatch_status,
        dispatch_cargo_status=consts.SPECIFIC_ORDER['dispatch_cargo_status'],
        place_id=consts.SPECIFIC_ORDER['place_id'],
        order_version=consts.SPECIFIC_ORDER['order_version'],
        grocery_flow_version=consts.SPECIFIC_ORDER['grocery_flow_version'],
        app_info=consts.SPECIFIC_ORDER['app_info'],
        cart_id=consts.SPECIFIC_ORDER['cart_id'],
        grocery_order_status=consts.SPECIFIC_ORDER['grocery_order_status'],
        edit_status=consts.SPECIFIC_ORDER['edit_status'],
        created=created,
        dispatch_delivery_type=dispatch_delivery_type,
    )
    order['depot_id'] = consts.SPECIFIC_ORDER['depot_id']

    antifraud.set_is_fraud(True)
    antifraud.set_is_suspicious(True)

    header = {'Accept-Language': 'ru', 'X-Remote-IP': '127.0.0.1'}
    specific_orders = await taxi_grocery_support.post(
        '/admin/v1/suggest/specific',
        json={'order_id': GROCERY_ORDER_ID},
        headers=header,
    )
    specific_orders = specific_orders.json()['orders'][0]

    assert set(specific_orders['allowed_actions']) == set(allowed_actions)
