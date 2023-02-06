# pylint: disable=too-many-lines
import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
# pylint: enable=import-error
import pytest
import pytz

from . import configs
from . import headers
from . import models
from . import order_log
from . import processing_noncrit

URI = (
    'ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.'
    '001&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2'
    'C%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%'
    'D0%92%D0%B0%D1%80%D1%88%D0%B0%D0%B2%D1%81%D0%BA'
    '%D0%BE%D0%B5%20%D1%88%D0%BE%D1%81%D1%81%D0%B5%2'
    'C%20141%D0%90%D0%BA1%2C%20%D0%BF%D0%BE%D0%B4%D1'
    '%8A%D0%B5%D0%B7%D0%B4%201%20%7B3457696635%7D'
)

NOW_DT = datetime.datetime(
    2020, 5, 25, 14, 43, 45, tzinfo=datetime.timezone.utc,
)
ERROR_AFTER_DT = NOW_DT + datetime.timedelta(
    minutes=processing_noncrit.ERROR_AFTER_MINUTES,
)
STOP_RETRY_AFTER_DT = NOW_DT + datetime.timedelta(
    minutes=processing_noncrit.STOP_RETRY_AFTER_MINUTES,
)


POLL_EATS_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_reserve_eats_order',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'should_try_hold': True},
        },
    ],
    is_config=True,
)

LAVKA_ROVER_FORCE_DELIVERY_ZONE_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_force_rover_zone',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'coordinates': [
                    [[[36.0, 54.0], [36.9, 54.0], [36.9, 56.1], [36.0, 56.1]]],
                ],
            },
        },
    ],
    is_config=True,
)

LAVKA_ROVER_MULTIORDER_FORBIDDEN = pytest.mark.experiments3(
    name='lavka_rover_remove_multiorder',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'multiple_dispatch_prohibited': False,
                'forcefully_ban_multiorder': True,
            },
        },
    ],
    is_config=True,
)

GROCERY_ORDERS_ETA_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_orders_eta',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'send_min_eta': True, 'send_max_eta': True},
        },
    ],
)

GROCERY_ORDERS_RECENT_GOODS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_orders_recent_goods',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'save_to_fav_goods': True},
        },
    ],
    is_config=True,
)


@pytest.mark.now('2020-05-25T17:43:45+03:00')
@processing_noncrit.NOTIFICATION_CONFIG
@POLL_EATS_EXPERIMENT
@configs.NO_MULTIORDER_GOODS_EXPERIMENT
@LAVKA_ROVER_MULTIORDER_FORBIDDEN
@GROCERY_ORDERS_ETA_EXPERIMENT
@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=2)
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize('good', [configs.SPECIAL_ITEM_ID, 'good-id'])
async def test_basic_submit_v1(
        taxi_grocery_orders,
        eats_core_eater,
        mockserver,
        grocery_cart,
        now,
        yamaps_local,
        good,
        experiments3,
        testpoint,
        processing,
        grocery_depots,
        transactions_eda,
        check_yt_logging,
):
    eats_core_eater.set_personal_email_id('email')

    now = now.replace(tzinfo=pytz.UTC)
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    idempotency_token = 'my-idempotency-token'
    offer_id = 'yyy'
    user_id = 'uuu'
    eats_user_id = 'eee'
    phone_id = 'ppp'
    application = 'app_name=mobileweb_yango_android'
    min_eta = 5
    max_eta = 25
    place_id = 'yamaps://12345'
    flat = '666'
    city = 'Moscow'
    appmetrica_device_id = 'some-appmetrica'

    vat = 20.0
    item = models.GroceryCartItem(item_id=good, price='10', vat=str(vat))
    grocery_cart.set_items(items=[item])
    grocery_cart.set_order_conditions(
        delivery_cost=0, max_eta=max_eta, min_eta=min_eta,
    )
    grocery_cart.set_grocery_flow_version(None)

    grocery_cart.set_delivery_zone_type('pedestrian')

    delivery_type = 'courier' if good == configs.SPECIAL_ITEM_ID else 'rover'
    grocery_cart.set_delivery_type(delivery_type=delivery_type)

    depot = grocery_depots.add_depot(
        legacy_depot_id=models.DEFAULT_DEPOT_ID,
        depot_id=models.DEFAULT_DEPOT_ID,
    )
    eats_order_id = '111-orderid'

    experiments3.add_config(
        name='grocery_orders_tracking_info_log_settings',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': True},
    )

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        assert request.json['order']['id'] == eats_order_id
        return {
            'success': 1,
            'data': {
                'createdObjects': [],
                'updatedObjects': [],
                'orderInfo': {
                    'orderId': 'abcdef',
                    'customer': {'id': '123123abc'},
                    'organization': '',
                    'sum': 123,
                    'status': 'ok',
                    'items': [],
                },
            },
        }

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        assert request.headers['X-Request-Application'] == application
        assert request.headers['X-YaTaxi-UserId'] == user_id
        expected_request = {
            'delivery': {
                'date': (
                    now + datetime.timedelta(minutes=max_eta)
                ).isoformat(),
                'deliveryTime': max_eta,
                'fee': '0',
                'preparationTime': 0,
                'courierType': 'native',
            },
            'idempotencyKey': idempotency_token,
            'items': [
                {
                    'id': item.item_id,
                    'name': item.title,
                    'description': None,
                    'quantity': float(item.quantity),
                    'price': item.price,
                    'discount': None,
                    'weight': None,
                    'vatPercent': vat,
                    'options': [],
                },
            ],
            'metaInfo': {
                'min_eta': min_eta,
                'leave_under_door': True,
                'max_eta': max_eta,
            },
            'payment': {'currencyCode': item.currency, 'method': 'taxi'},
            'place': {'id': models.DEFAULT_DEPOT_ID},
            'user': {
                'address': {
                    'city': city,
                    'comment': 'please, fast!',
                    'doorcode': '42',
                    'entrance': '1',
                    'flat': '666',
                    'floor': '13',
                    'house': '141Ак1',
                    'location': {'latitude': 55.0, 'longitude': 37.0},
                    'street': 'Varshavskoye Highway',
                },
                'email': None,
                'id': eats_user_id,
                'idProvider': 'eats',
                'name': None,
            },
            'promocode': None,
            'extendedOptions': [
                {'type': 'gift_by_phone', 'phone_number': '88005553535'},
            ],
        }

        if good == configs.SPECIAL_ITEM_ID:
            expected_request['metaInfo']['multiple_dispatch_prohibited'] = True
        else:
            expected_request['metaInfo']['try_rover'] = True
            expected_request['metaInfo']['forcefully_ban_multiorder'] = True

        assert request.json == expected_request
        return {'payload': {'number': eats_order_id}}

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/set-order-id')
    def mock_set_order_id(request):
        assert request.json == {
            'order_id': eats_order_id,
            'cart_id': some_cart_id,
        }
        return {}

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert '88005553535' not in data['log']

    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': place_id,
            'floor': '13',
            'flat': flat,
            'entrance': '1',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
        'gift_by_phone': {'phone_number': '88005553535'},
        'use_rover': True,
    }

    user_info = f'eats_user_id={eats_user_id}, personal_phone_id={phone_id}'
    submit_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': application,
        'X-YaTaxi-User': user_info,
        'X-Idempotency-Token': idempotency_token,
        'X-YaTaxi-Session': 'taxi:' + user_id,
        'X-YaTaxi-Bound-Sessions': 'eats:12345,taxi:6789',
        'X-AppMetrica-DeviceId': appmetrica_device_id,
    }

    grocery_cart.check_request(
        fields_to_check={
            'additional_data': {
                'device_coordinates': {'location': [37, 55], 'uri': URI},
                'city': 'Moscow',
                'street': 'Varshavskoye Highway',
                'house': '141Ак1',
                'flat': flat,
                'comment': 'please, fast!',
                'doorcode': '42',
                'entrance': '1',
                'floor': '13',
            },
        },
        handler=mock_grocery_cart.Handler.checkout,
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit', json=submit_body, headers=submit_headers,
    )

    assert response.status_code == 200
    assert eats_order_id == response.json()['order_id']

    assert yamaps_local.times_called() == 1
    assert grocery_cart.checkout_times_called() == 1
    assert mock_eats_checkout.times_called == 1
    assert mock_set_order_id.times_called == 1
    assert testpoint_logs.times_called == 1
    assert mock_order_add.times_called == 1

    event_policy = {
        'stop_retry_after': STOP_RETRY_AFTER_DT.isoformat(),
        'error_after': ERROR_AFTER_DT.isoformat(),
        'retry_interval': processing_noncrit.RETRY_INTERVAL_MINUTES * 60,
        'retry_count': 1,
    }
    created_event = processing_noncrit.check_noncrit_event(
        processing,
        eats_order_id,
        'created',
        taxi_user_id='',
        app_name='mobileweb_yango_android',
        event_policy=event_policy,
    )
    assert created_event is not None
    status_change_event = processing_noncrit.check_noncrit_event(
        processing, eats_order_id, 'status_change',
    )
    assert status_change_event is not None
    order_log.check_eats_checkout(
        status_change_event,
        order_created_date='2020-05-25T17:43:45+03:00',
        user_id=eats_user_id,
        order_id=eats_order_id,
        depot_id=models.DEFAULT_DEPOT_ID,
        cart_items=[item],
        depot=depot,
        appmetrica_device_id=appmetrica_device_id,
    )
    add_address_event = processing_noncrit.check_noncrit_event(
        processing, eats_order_id, 'add_address',
    )
    assert add_address_event['flat'] == flat
    assert add_address_event['place_id'] == place_id
    assert add_address_event['city'] == city

    assert len(check_yt_logging.messages) == 1
    message = check_yt_logging.messages[0]
    assert message['key'] == eats_order_id
    assert message['value'] == {'max_eta': max_eta, 'min_eta': min_eta}


@pytest.mark.now('2020-05-25T17:43:45+00:00')
@pytest.mark.parametrize(
    'cart_code,orders_code', [(401, 500), (404, 400), (409, 400), (500, 500)],
)
async def test_grocery_cart_4xx_for_eats_checkout(
        taxi_grocery_orders,
        mockserver,
        load_json,
        cart_code,
        orders_code,
        taxi_grocery_orders_monitor,
        yamaps_local,
):
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    idempotency_token = 'my-idempotency-token'

    @mockserver.json_handler('/grocery-cart/internal/v2/cart/checkout')
    def _mock_grocery_cart(request):
        return mockserver.make_response(
            '{"code": "NO_CODE", "message": ""}', cart_code,
        )

    offer_id = 'yyy'
    user_id = 'uuu'
    eats_user_id = 'eee'
    phone_id = 'ppp'
    application = 'app_name=mobileweb_yango_android'
    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
    }
    user_info = f'eats_user_id={eats_user_id}, personal_phone_id={phone_id}'
    submit_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': application,
        'X-YaTaxi-User': user_info,
        'X-Yandex-UID': '777',
        'X-YaTaxi-PhoneId': phone_id,
        'X-YaTaxi-UserId': user_id,
        'X-Idempotency-Token': idempotency_token,
        'X-YaTaxi-Session': 'taxi:' + user_id,
    }

    metrics_before = await taxi_grocery_orders_monitor.get_metric('metrics')

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit?checkout_type=eats',
        json=submit_body,
        headers=submit_headers,
    )

    metrics_after = await taxi_grocery_orders_monitor.get_metric('metrics')
    assert metrics_after['created_orders'] == metrics_before['created_orders']

    assert response.status_code == orders_code

    if cart_code == 500:
        assert _mock_grocery_cart.times_called == 3  # retry
    else:
        assert _mock_grocery_cart.times_called == 1


@POLL_EATS_EXPERIMENT
async def test_404_set_order_id(
        taxi_grocery_orders,
        mockserver,
        eats_core_eater,
        grocery_cart,
        grocery_depots,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)
    eats_core_eater.set_personal_email_id('email')

    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    idempotency_token = 'my-idempotency-token'
    offer_id = 'yyy'
    user_id = 'uuu'
    eats_user_id = 'eee'
    phone_id = 'ppp'
    application = 'app_name=mobileweb_yango_android'

    order_id = '111-orderid'

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        return {'payload': {'number': order_id}}

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        assert request.json['order']['id'] == order_id
        return {
            'success': 1,
            'data': {
                'createdObjects': [],
                'updatedObjects': [],
                'orderInfo': {
                    'orderId': 'abcdef',
                    'customer': {'id': '123123abc'},
                    'organization': '',
                    'sum': 123,
                    'status': 'ok',
                    'items': [],
                },
            },
        }

    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
    }
    user_info = f'eats_user_id={eats_user_id}, personal_phone_id={phone_id}'
    submit_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': application,
        'X-YaTaxi-User': user_info,
        'X-Idempotency-Token': idempotency_token,
        'X-YaTaxi-Session': 'taxi:' + user_id,
    }

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit?checkout_type=eats',
        json=submit_body,
        headers=submit_headers,
    )
    assert response.status_code == 200
    assert response.json()['order_id'] == order_id

    assert mock_eats_checkout.times_called == 1
    assert grocery_cart.checkout_times_called() == 1
    assert grocery_cart.set_order_id_times_called() == 1
    assert mock_order_add.times_called == 1


@pytest.mark.now('2020-05-25T17:43:45+03:00')
@POLL_EATS_EXPERIMENT
@configs.NO_MULTIORDER_GOODS_EXPERIMENT
@GROCERY_ORDERS_ETA_EXPERIMENT
@GROCERY_ORDERS_RECENT_GOODS_EXPERIMENT
@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=2)
async def test_save_recent_goods(
        taxi_grocery_orders,
        grocery_cart,
        grocery_fav_goods,
        testpoint,
        eats_core_eater,
):
    eats_core_eater.set_personal_email_id('email')

    product_ids = ['test_product_id_1', 'test_product_id_2']
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    idempotency_token = 'my-idempotency-token'
    offer_id = 'yyy'
    user_id = 'uuu'
    eats_user_id = 'eee'
    phone_id = 'ppp'
    application = 'app_name=mobileweb_yango_android'
    min_eta = 5
    max_eta = 25

    items = [
        models.GroceryCartItem(item_id=product_id, price='10')
        for product_id in product_ids
    ]
    grocery_cart.set_items(items=items)
    grocery_cart.set_order_conditions(
        delivery_cost=0, max_eta=max_eta, min_eta=min_eta,
    )
    grocery_cart.set_grocery_flow_version(None)
    grocery_cart.set_delivery_type(delivery_type='courier')

    yandex_uid = 'test_yandex_uid'

    grocery_fav_goods.setup_request_checking(
        yandex_uid=yandex_uid, product_ids=product_ids,
    )

    @testpoint('save_recent_goods')
    def save_recent_goods(data):
        pass

    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
        'gift_by_phone': {'phone_number': '88005553535'},
        'use_rover': True,
    }
    user_info = f'eats_user_id={eats_user_id}, personal_phone_id={phone_id}'
    submit_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': application,
        'X-YaTaxi-User': user_info,
        'X-Idempotency-Token': idempotency_token,
        'X-YaTaxi-Session': 'taxi:' + user_id,
        'X-YaTaxi-Bound-Sessions': 'eats:12345,taxi:6789',
        'X-Yandex-UID': yandex_uid,
    }

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit', json=submit_body, headers=submit_headers,
    )
    assert response.status_code == 200

    await save_recent_goods.wait_call()

    assert grocery_fav_goods.times_called == 1


@pytest.mark.now('2020-05-25T17:43:45+03:00')
@POLL_EATS_EXPERIMENT
@configs.NO_MULTIORDER_GOODS_EXPERIMENT
@LAVKA_ROVER_MULTIORDER_FORBIDDEN
@GROCERY_ORDERS_ETA_EXPERIMENT
@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=2)
@pytest.mark.parametrize(
    'delivery_zone_type, courier_type',
    [
        ('pedestrian', 'native'),
        ('yandex_taxi', 'taxi'),
        ('yandex_taxi_remote', 'taxi'),
        ('yandex_taxi_night', 'taxi'),
    ],
)
async def test_courier_type(
        taxi_grocery_orders,
        eats_core_eater,
        mockserver,
        grocery_cart,
        now,
        yamaps_local,
        delivery_zone_type,
        courier_type,
):
    eats_core_eater.set_personal_email_id('email')

    now = now.replace(tzinfo=pytz.UTC)
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    idempotency_token = 'my-idempotency-token'
    offer_id = 'yyy'
    user_id = 'uuu'
    eats_user_id = 'eee'
    phone_id = 'ppp'
    application = 'app_name=mobileweb_yango_android'
    min_eta = 5
    max_eta = 25

    item = models.GroceryCartItem(item_id='item_id', price='10')
    grocery_cart.set_items(items=[item])
    grocery_cart.set_order_conditions(
        delivery_cost=0, max_eta=max_eta, min_eta=min_eta,
    )
    grocery_cart.set_grocery_flow_version(None)

    grocery_cart.set_delivery_zone_type(delivery_zone_type)
    grocery_cart.set_delivery_type(delivery_type='courier')

    eats_order_id = '111-orderid'

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def _mock_order_add(request):
        assert request.json['order']['id'] == eats_order_id
        return {
            'success': 1,
            'data': {
                'createdObjects': [],
                'updatedObjects': [],
                'orderInfo': {
                    'orderId': 'abcdef',
                    'customer': {'id': '123123abc'},
                    'organization': '',
                    'sum': 123,
                    'status': 'ok',
                    'items': [],
                },
            },
        }

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def _mock_eats_checkout(request):
        assert request.json['delivery']['courierType'] == courier_type
        return {'payload': {'number': eats_order_id}}

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/set-order-id')
    def _mock_set_order_id(_request):
        return {}

    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
        'gift_by_phone': {'phone_number': '88005553535'},
        'use_rover': True,
    }

    user_info = f'eats_user_id={eats_user_id}, personal_phone_id={phone_id}'
    submit_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': application,
        'X-YaTaxi-User': user_info,
        'X-Idempotency-Token': idempotency_token,
        'X-YaTaxi-Session': 'taxi:' + user_id,
        'X-YaTaxi-Bound-Sessions': 'eats:12345,taxi:6789',
    }

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit', json=submit_body, headers=submit_headers,
    )

    assert response.status_code == 200


@configs.GROCERY_PAYMENT_METHOD_VALIDATION
@pytest.mark.parametrize(
    'pm_id, flow_version',
    [
        ('good_id', 'eats_payments'),
        ('good_id', 'eats_core'),
        ('bad_id', 'eats_payments'),
        ('bad_id', 'eats_core'),
    ],
)
async def test_payment_method_validation(
        taxi_grocery_orders,
        eats_core_eater,
        grocery_cart,
        grocery_payments,
        pm_id,
        flow_version,
):
    eats_core_eater.set_personal_email_id('email')

    pm_type = 'card'
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    offer_id = 'yyy'
    grocery_cart.set_payment_method({'type': pm_type, 'id': pm_id})
    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
        'gift_by_phone': {'phone_number': '88005553535'},
        'use_rover': True,
        'flow_version': flow_version,
        'payment_method_id': pm_id,
        'payment_method_type': pm_type,
    }

    if pm_id == 'bad_id' and flow_version == 'eats_payments':
        grocery_payments.mock_validate(
            errors=[
                {
                    'method': {'id': pm_id, 'type': pm_type},
                    'error_code': 'not_exists',
                },
            ],
        )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json=submit_body,
        headers=headers.DEFAULT_HEADERS,
    )

    if pm_id == 'good_id' or flow_version == 'eats_core':
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json()['code'] == 'invalid_payment_method'


@LAVKA_ROVER_FORCE_DELIVERY_ZONE_EXPERIMENT
@pytest.mark.parametrize(
    'location,use_rover,sent_flag',
    [
        pytest.param([33.0, 51.0], True, False, id='no rover'),
        pytest.param(
            [36.5, 55.0], False, True, id='forced rover, ignore false',
        ),
        pytest.param([37.0, 55.0], True, True, id='rover'),
    ],
)
async def test_force_rover(
        taxi_grocery_orders,
        eats_core_eater,
        mockserver,
        grocery_cart,
        grocery_payments,
        location,
        use_rover,
        sent_flag,
):
    eats_core_eater.set_personal_email_id('email')
    grocery_cart.set_grocery_flow_version(None)
    grocery_cart.set_delivery_type(delivery_type='courier')

    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    offer_id = 'yyy'
    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': location,
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
        'gift_by_phone': {'phone_number': '88005553535'},
        'use_rover': use_rover,
    }

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        request.json['metaInfo']['try_rover'] = sent_flag
        return {'payload': {'number': '000000-000000'}}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json=submit_body,
        headers=headers.DEFAULT_HEADERS,
    )

    assert mock_eats_checkout.times_called == 1
    assert response.status_code == 200


@configs.PASS_PAYMENT_METHOD_CHECKOUT_ENABLED_EATS_CYCLE
async def test_pass_payment_method_to_cart(
        taxi_grocery_orders, eats_core_eater, grocery_cart,
):
    eats_core_eater.set_personal_email_id('email')

    pm_type = 'card'
    pm_id = 'card-x2809'
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    offer_id = 'yyy'
    grocery_cart.set_payment_method({'type': pm_type, 'id': pm_id})
    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {
            'location': [37, 55],
            'place_id': 'yamaps://12345',
            'floor': '13',
            'flat': '666',
            'doorcode': '42',
            'doorcode_extra': 'doorcode_extra',
            'building_name': 'building_name',
            'doorbell_name': 'doorbell_name',
            'left_at_door': True,
            'comment': 'please, fast!',
        },
        'flow_version': 'eats_payments',
        'payment_method_id': pm_id,
        'payment_method_type': pm_type,
    }

    grocery_cart.check_request(
        {'payment_method': {'type': pm_type, 'id': pm_id}},
        handler=mock_grocery_cart.Handler.checkout,
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json=submit_body,
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.now('2020-05-25T17:43:45+03:00')
@POLL_EATS_EXPERIMENT
@configs.NO_MULTIORDER_GOODS_EXPERIMENT
@LAVKA_ROVER_MULTIORDER_FORBIDDEN
@GROCERY_ORDERS_ETA_EXPERIMENT
@pytest.mark.config(GROCERY_ORDERS_ORDER_TIMEOUT=2)
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize('uid', ['12345', None])
@pytest.mark.parametrize('phone_id', ['ppp', None])
async def test_use_limited_discounts(
        taxi_grocery_orders,
        eats_core_eater,
        mockserver,
        grocery_cart,
        stq,
        grocery_depots,
        uid,
        phone_id,
):
    eats_core_eater.set_personal_email_id('email')
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    idempotency_token = 'my-idempotency-token'
    offer_id = 'yyy'
    user_id = 'uuu'
    eats_user_id = 'eee'
    application = 'app_name=mobileweb_yango_android'
    min_eta = 5
    max_eta = 25
    place_id = 'yamaps://12345'
    appmetrica_device_id = 'some-appmetrica'
    limited_discount_ids = ['first_id, second_id']

    vat = 20.0
    item = models.GroceryCartItem(item_id='good-id', price='10', vat=str(vat))
    grocery_cart.set_items(items=[item])
    grocery_cart.set_order_conditions(
        delivery_cost=0, max_eta=max_eta, min_eta=min_eta,
    )
    grocery_cart.set_grocery_flow_version(None)

    grocery_cart.set_delivery_zone_type('pedestrian')
    grocery_cart.set_limited_discount_ids(
        limited_discount_ids=limited_discount_ids,
    )
    grocery_cart.set_delivery_type(delivery_type='courier')

    grocery_depots.add_depot(
        legacy_depot_id=models.DEFAULT_DEPOT_ID,
        depot_id=models.DEFAULT_DEPOT_ID,
    )
    eats_order_id = '111-orderid'

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        return {
            'success': 1,
            'data': {
                'createdObjects': [],
                'updatedObjects': [],
                'orderInfo': {
                    'orderId': 'abcdef',
                    'customer': {'id': '123123abc'},
                    'organization': '',
                    'sum': 123,
                    'status': 'ok',
                    'items': [],
                },
            },
        }

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        return {'payload': {'number': eats_order_id}}

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/set-order-id')
    def mock_set_order_id(request):
        return {}

    submit_body = {
        'cart_id': some_cart_id,
        'cart_version': 4,
        'offer_id': offer_id,
        'position': {'location': [37, 55], 'place_id': place_id},
    }
    if phone_id:
        user_info = (
            f'eats_user_id={eats_user_id}, personal_phone_id={phone_id}'
        )
    else:
        user_info = f'eats_user_id={eats_user_id}'

    submit_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': application,
        'X-YaTaxi-User': user_info,
        'X-Idempotency-Token': idempotency_token,
        'X-YaTaxi-Session': 'taxi:' + user_id,
        'X-YaTaxi-Bound-Sessions': 'eats:12345,taxi:6789',
        'X-AppMetrica-DeviceId': appmetrica_device_id,
    }
    if uid:
        submit_headers['X-Yandex-UID'] = uid

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit', json=submit_body, headers=submit_headers,
    )
    assert response.status_code == 200
    assert mock_eats_checkout.times_called == 1
    assert mock_set_order_id.times_called == 1
    assert mock_order_add.times_called == 1

    if uid:
        assert stq.grocery_discounts_discount_usage_add.times_called == 1
        args = stq.grocery_discounts_discount_usage_add.next_call()
        assert args['id'] == eats_order_id
        args['kwargs'].pop('log_extra')
        args['kwargs']['discount_ids'] = args['kwargs']['discount_ids'].sort()
        args_dict = {
            'order_id': eats_order_id,
            'yandex_uid': int(uid),
            'discount_ids': limited_discount_ids.sort(),
            'add_time': '2020-05-25T14:43:45+00:00',
        }
        if phone_id:
            args_dict['personal_phone_id'] = phone_id
        assert args['kwargs'] == args_dict
    else:
        assert stq.grocery_discounts_discount_usage_add.times_called == 0
