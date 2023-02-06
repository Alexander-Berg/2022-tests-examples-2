import datetime

import pytest

from . import models

GROCERY_ORDER_ID = 'd11c2b4180724389ab4d9a4ddca73fac-grocery'
OTHER_GROCERY_ORDER_ID = 'd99c2b4180724389ab4d9a4ddca73fac-grocery'
SHORT_ORDER_ID = '220222-457-2578'
DEPOT_ID = '123456'
APP_NAME = 'mobileweb_yango_android'
APP_INFO = f'app_name={APP_NAME}'

MAX_ETA = 50
CREATED = datetime.datetime(
    year=2020, month=3, day=10, tzinfo=datetime.timezone.utc,
)
PROMISED_AT = CREATED + datetime.timedelta(minutes=MAX_ETA)
FINISH_STARTED_IN_TIME = PROMISED_AT - datetime.timedelta(minutes=10)
FINISH_STARTED_LATE = PROMISED_AT + datetime.timedelta(minutes=10)

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'  # example: 2020-03-10T00:50:00+00:00

USER_COMMENT = 'user comment'


@pytest.mark.parametrize(
    'status, finish_started',
    [
        ('delivering', None),
        ('closed', FINISH_STARTED_IN_TIME),
        ('closed', FINISH_STARTED_LATE),
    ],
)
@pytest.mark.parametrize('order_id', [GROCERY_ORDER_ID, SHORT_ORDER_ID])
@pytest.mark.now(models.NOW)
async def test_basic(
        taxi_grocery_support,
        grocery_orders,
        grocery_cart,
        grocery_depots,
        grocery_order_log,
        grocery_marketing,
        antifraud,
        pgsql,
        now,
        status,
        finish_started,
        order_id,
):
    country_iso3 = 'RUS'
    finish_time = None
    if finish_started:
        finish_time = finish_started.isoformat()

    personal_phone_id = 'personal_phone_id'
    order = grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        status=status,
        created=CREATED.isoformat(),
        finish_started=finish_time,
        short_order_id=SHORT_ORDER_ID,
        country='Russia',
        city_label='Москва',
        user_info={
            'personal_phone_id': 'customer.personal_phone_id',
            'yandex_uid': 'customer.yandex_uid',
            'phone_id': 'customer.phone_id',
        },
        dispatch_status_info={
            'dispatch_id': 'dispatch_id',
            'status': 'revoked',
            'cargo_status': 'delivered',
            'performer_info': {'driver_id': 'test-driver-id'},
        },
        app_info=APP_INFO,
        cancel_reason_type='user_request',
        cancel_reason_message='message',
        leave_at_door=True,
        city='Москва',
        street='Большие Каменщики',
        house='37',
        entrance='7',
        flat='24',
        vip_type='ultima',
        timeslot_request_kind='wide_slot',
        comment='comment',
        personal_phone_id=personal_phone_id,
    )
    order['depot_id'] = DEPOT_ID

    grocery_cart.set_cart_data(
        cart_id=order['cart_id'], cart_version=order['cart_version'],
    )
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_promocode(
        code='PROMO',
        valid=True,
        discount='33',
        source='eats',
        discount_type='fixed',
    )
    max_eta = MAX_ETA
    grocery_cart.set_order_conditions(
        delivery_cost='100', max_eta=max_eta, min_eta=max_eta,
    )

    tin = 'tin-for-depot'
    region_id = 213
    city = 'Москва'  # derived from region_id
    grocery_depots.add_depot(
        depot_test_id=123,
        legacy_depot_id=order['depot']['id'],
        tin=tin,
        country_iso3=country_iso3,
        region_id=region_id,
    )

    grocery_order_log.set_order_ids_response([GROCERY_ORDER_ID])

    total_completed_orders_count = 7
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=total_completed_orders_count,
        user_id=order['yandex_uid'],
    )

    short_address = '{}, {} {} {}'.format(
        order['city'], order['street'], order['house'], order['flat'],
    )
    antifraud.check_order_antifraud_request(
        order_nr=order['order_id'], short_address=short_address,
    )
    antifraud.set_is_fraud(False)
    antifraud.set_is_suspicious(True)
    antifraud.set_lavka_users(lavka_users=True)

    now = now.replace(tzinfo=models.UTC_TZ)
    first_comment = {
        'comment': 'comment',
        'support_login': 'login',
        'timestamp': now.isoformat(),
    }
    comment = {
        'comment': USER_COMMENT,
        'support_login': 'support_login',
        'timestamp': now.isoformat(),
    }
    user = models.Customer(
        pgsql,
        personal_phone_id=personal_phone_id,
        comments=[first_comment, comment],
    )

    user.update_db()

    response = await taxi_grocery_support.post(
        '/internal/v1/get-chatterbox-order-meta',
        json={'metadata': {'order_id': order_id}},
    )

    assert response.status_code == 200
    order_meta = response.json()

    assert order_meta['metadata']['order_id'] == order['order_id']
    assert order_meta['metadata']['short_order_id'] == order['short_order_id']
    assert order_meta['metadata']['app_info'] == order['app_info']
    assert order_meta['metadata']['yandex_uid'] == order['yandex_uid']
    assert order_meta['metadata']['order_status'] == order['status']
    assert order_meta['metadata']['depot_id'] == order['depot']['id']
    assert order_meta['metadata']['created'] == order['created']
    assert order_meta['metadata']['payment_type'] == 'card'
    assert order_meta['metadata']['was_used_promocode'] is True
    assert order_meta['metadata']['promocode_info']['promocode'] == 'PROMO'
    assert order_meta['metadata']['promocode_info']['value'] == '33'
    assert order_meta['metadata']['promocode_info']['type'] == 'fixed'
    assert order_meta['metadata']['surge_additional_delivery_amount'] == '100'
    assert order_meta['metadata']['country_label'] == order['country']
    assert order_meta['metadata']['country_iso3'] == country_iso3
    assert order_meta['metadata']['city_label'] == city
    assert (
        order_meta['metadata']['courier_id']
        == order['dispatch_status_info']['performer_info']['driver_id']
    )
    assert order_meta['metadata']['cancel_reason_type'] == 'user_request'
    assert order_meta['metadata']['cancel_reason_message'] == 'message'
    assert order_meta['metadata']['user_fraud'] == 'Unsure'
    assert order_meta['metadata']['order_fraud'] == 'Unsure'
    assert order_meta['metadata']['good_client_story']
    assert order_meta['metadata']['leave_at_door'] == order['leave_at_door']
    assert order_meta['metadata']['street'] == order['street']
    assert order_meta['metadata']['house'] == order['house']
    assert order_meta['metadata']['entrance'] == order['entrance']
    assert order_meta['metadata']['flat'] == order['flat']
    assert order_meta['metadata']['vip_type'] == order['vip_type']
    assert (
        order_meta['metadata']['timeslot_request_kind']
        == order['timeslot_request_kind']
    )
    assert order_meta['metadata']['comment'] == order['comment']
    assert order_meta['metadata']['user_comment'] == USER_COMMENT
    assert (
        order_meta['metadata']['total_completed_orders_count']
        == total_completed_orders_count
    )

    order_created = datetime.datetime.fromisoformat(order['created'])
    order_promised_at = order_created + datetime.timedelta(minutes=max_eta)
    if status == 'delivering':
        time_interval = models.NOW_DT - order_promised_at
    elif status == 'closed':
        order_finish_started = datetime.datetime.fromisoformat(
            order['finish_started'],
        )
        time_interval = order_finish_started - order_promised_at
    order_delay_minutes = time_interval / datetime.timedelta(minutes=1)

    order_promised_at_str = order_promised_at.strftime(TIME_FORMAT)
    order_promised_at_str = (
        order_promised_at_str[:-2] + ':' + order_promised_at_str[-2:]
    )
    assert order_meta['metadata']['order_promised_at'] == order_promised_at_str

    if order_delay_minutes >= 0:
        assert (
            order_meta['metadata']['order_delay_minutes']
            == order_delay_minutes
        )
    else:
        assert order_meta['metadata']['order_delay_minutes'] == 0


@pytest.mark.parametrize('order_id', [GROCERY_ORDER_ID, SHORT_ORDER_ID])
@pytest.mark.now(models.NOW)
async def test_pickup(
        grocery_orders,
        taxi_grocery_support,
        grocery_cart,
        grocery_depots,
        grocery_order_log,
        antifraud,
        order_id,
):
    order = grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        short_order_id=SHORT_ORDER_ID,
        app_info=APP_INFO,
        city_label='Москва',
        user_info={
            'personal_phone_id': 'customer.personal_phone_id',
            'yandex_uid': 'customer.yandex_uid',
            'phone_id': 'customer.phone_id',
        },
        cancel_reason_type='user_request',
        cancel_reason_message='message',
    )
    order['depot_id'] = DEPOT_ID

    grocery_cart.set_cart_data(
        cart_id=order['cart_id'], cart_version=order['cart_version'],
    )

    grocery_cart.set_delivery_type('pickup')

    tin = 'tin-for-depot'
    grocery_depots.add_depot(
        depot_test_id=123, legacy_depot_id=order['depot']['id'], tin=tin,
    )

    grocery_order_log.set_order_ids_response([GROCERY_ORDER_ID])

    antifraud.set_is_fraud(False)
    antifraud.set_is_suspicious(True)
    response = await taxi_grocery_support.post(
        '/internal/v1/get-chatterbox-order-meta',
        json={'metadata': {'order_id': order_id}},
    )

    assert response.status_code == 200
    order_meta = response.json()

    assert 'order_delay_minutes' not in order_meta['metadata']

    assert not order_meta['metadata']['good_client_story']


@pytest.mark.parametrize('order_id', [GROCERY_ORDER_ID, SHORT_ORDER_ID])
@pytest.mark.parametrize(
    'source', ['grocery_order_log', 'grocery_orders', 'grocery_cart'],
)
async def test_not_found(
        grocery_order_log,
        grocery_orders,
        grocery_cart,
        taxi_grocery_support,
        order_id,
        source,
):
    if source != 'grocery_order_log':
        grocery_order_log.set_order_ids_response([GROCERY_ORDER_ID])
    elif order_id == GROCERY_ORDER_ID:
        return

    if source == 'grocery_cart':
        grocery_orders.add_order(
            order_id=GROCERY_ORDER_ID, short_order_id=SHORT_ORDER_ID,
        )

    response = await taxi_grocery_support.post(
        '/internal/v1/get-chatterbox-order-meta',
        json={'metadata': {'order_id': order_id}},
    )

    assert response.status_code == 404

    assert 'metadata' not in response.json()

    order_id_is_short = order_id == SHORT_ORDER_ID
    assert grocery_order_log.times_get_order_ids_called() == int(
        order_id_is_short,
    )
    assert grocery_orders.info_times_called() == int(
        source != 'grocery_order_log',
    )
    assert grocery_cart.retrieve_times_called() == int(
        source == 'grocery_cart',
    )


async def test_order_log_conflict(
        grocery_order_log, grocery_orders, grocery_cart, taxi_grocery_support,
):
    grocery_order_log.set_order_ids_response(
        [GROCERY_ORDER_ID, OTHER_GROCERY_ORDER_ID],
    )

    response = await taxi_grocery_support.post(
        '/internal/v1/get-chatterbox-order-meta',
        json={'metadata': {'order_id': SHORT_ORDER_ID}},
    )

    assert response.status_code == 409

    assert 'metadata' not in response.json()

    assert grocery_order_log.times_get_order_ids_called() == 1
    assert grocery_orders.info_times_called() == 0
    assert grocery_cart.retrieve_times_called() == 0
