import copy
import datetime

import pytest
import pytz

from . import headers
from . import models

SOME_CART_ID = '00000000-0000-0000-0000-d98013100500'
SOME_ORDER_ID = '111-23456'
SOME_ITEM_ID = 'item-id'

PERSONAL_PHONE_ID_USER = 'personal_phone_id=222'
PERSONAL_EATS_ID_USER = 'eats_user_id=111'

COMMON_HEADERS = {
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=yango_android',
    'X-YaTaxi-User': f'{PERSONAL_PHONE_ID_USER},{PERSONAL_EATS_ID_USER}',
    'X-Idempotency-Token': 'idempotency-token',
    'X-YaTaxi-Session': 'taxi:uuu',
}

POLL_EATS_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_reserve_eats_order',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'should_try_hold': True, 'timeout_seconds': 2000},
        },
    ],
    is_config=True,
)

NO_MULTIORDER_GOODS_EXPERIMENT = pytest.mark.experiments3(
    name='no_multiorder_goods',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'multiple_dispatch_prohibited': True,
                'forcefully_ban_multiorder': False,
                'goods-to-exclude': [SOME_ITEM_ID],
            },
        },
    ],
    default_value={},
    is_config=True,
)


DEFAULT_POSITION = {
    'location': [37, 55],
    'place_id': 'yamaps://12345',
    'floor': '13',
    'flat': '666',
    'doorcode': '42',
    'doorcode_extra': 'doorcode_extra',
    'building_name': 'building_name',
    'doorbell_name': 'doorbell_name',
    'left_at_door': False,
    'comment': 'please, fast!',
}


@POLL_EATS_EXPERIMENT
@NO_MULTIORDER_GOODS_EXPERIMENT
@pytest.mark.experiments3(
    name='grocery_override_payment_method',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'eats',
                    'arg_name': 'application.name',
                    'arg_type': 'string',
                },
            },
            'value': {'override_payment_method': True},
        },
    ],
    default_value={'override_payment_method': False},
    is_config=True,
)
@pytest.mark.parametrize(
    'user_provider,user_id,app_name',
    [('eats', '111', 'android'), ('yandex', 'uuu', 'eats')],
)
@pytest.mark.now(datetime.datetime(2020, 3, 25, 10, 0, 0).isoformat())
@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_basic(
        taxi_grocery_orders,
        mockserver,
        now,
        grocery_cart,
        user_provider,
        user_id,
        app_name,
        taxi_config,
        yamaps_local,
        grocery_depots,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)
    now = now.replace(tzinfo=pytz.UTC)

    taxi_config.set_values({'GROCERY_ORDERS_CHECKOUT_PROVIDER': user_provider})

    vat = 20.0
    item = models.GroceryCartItem(
        item_id=SOME_ITEM_ID, price='10', full_price='20', vat=str(vat),
    )
    grocery_cart.set_items(items=[item])

    payment_method = {'type': 'cart', 'id': 'id'}
    grocery_cart.set_payment_method(payment_method, discount=True)
    max_eta = 15
    grocery_cart.set_order_conditions(delivery_cost=0, max_eta=max_eta)

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        assert request.json['order']['id'] == SOME_ORDER_ID
        assert request.json['order']['reserve_timeout'] == 2000
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
        payment_method_type = 'taxi'
        if request.headers['X-Request-Application'] == 'app_name=eats':
            assert request.json['payment']['method'] == 'free'
            payment_method_type = 'free'

        assert request.headers['X-YaTaxi-UserId'] == 'uuu'
        assert (
            request.headers['X-YaTaxi-User'] == COMMON_HEADERS['X-YaTaxi-User']
        )

        assert request.json == {
            'delivery': {
                'date': (now + datetime.timedelta(minutes=15)).isoformat(),
                'deliveryTime': 15,
                'fee': '0',
                'preparationTime': 0,
            },
            'idempotencyKey': 'idempotency-token',
            'items': [
                {
                    'id': item.item_id,
                    'name': item.title,
                    'description': None,
                    'quantity': float(item.quantity),
                    'price': item.price,
                    'discount': {'amount': float(item.discount())},
                    'weight': None,
                    'vatPercent': vat,
                    'options': [],
                },
            ],
            'metaInfo': {
                'multiple_dispatch_prohibited': True,
                'payment_method': payment_method,
                'max_eta': max_eta,
                'leave_under_door': True,
            },
            'payment': {
                'currencyCode': item.currency,
                'method': payment_method_type,
            },
            'place': {'id': models.DEFAULT_DEPOT_ID},
            'user': {
                'address': {
                    'city': 'Moscow',
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
                'id': user_id,
                'idProvider': user_provider,
                'name': None,
            },
            'promocode': None,
            'extendedOptions': [
                {
                    'phone_number': '88005553535',
                    'name': 'Иван',
                    'type': 'gift_by_phone',
                },
            ],
        }
        return {'payload': {'number': SOME_ORDER_ID}}

    updated_headers = copy.copy(COMMON_HEADERS)
    updated_headers['X-Request-Application'] = 'app_name=' + app_name

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'payment_method_type': 'free',
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
            'gift_by_phone': {'phone_number': '88005553535', 'name': 'Иван'},
        },
        headers=updated_headers,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': SOME_ORDER_ID}

    assert mock_eats_checkout.times_called == 1
    assert yamaps_local.times_called() == 1
    assert grocery_cart.checkout_times_called() == 1
    assert grocery_cart.set_order_id_times_called() == 1
    assert mock_order_add.times_called == 1


@POLL_EATS_EXPERIMENT
@pytest.mark.parametrize(
    'promocode_valid,expected_response_code',
    [(None, 200), (False, 400), (True, 200)],
)
@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_promocode(
        taxi_grocery_orders,
        mockserver,
        promocode_valid,
        expected_response_code,
        grocery_cart,
        yamaps_local,
        grocery_depots,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)

    promo = 'LAVKABACKEND-1000'
    if promocode_valid is not None:
        grocery_cart.set_promocode(code=promo, valid=promocode_valid)

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        assert request.json['order']['id'] == SOME_ORDER_ID
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
        if promocode_valid is not None:
            assert request.json['promocode'] == promo
        else:
            assert request.json['promocode'] is None

        return {'payload': {'number': SOME_ORDER_ID}}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
            },
        },
        headers=COMMON_HEADERS,
    )
    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        assert response.json() == {'order_id': SOME_ORDER_ID}
        assert mock_eats_checkout.times_called == 1
        assert grocery_cart.set_order_id_times_called() == 1
        assert mock_order_add.times_called == 1
    else:
        assert response.json() == {
            'code': 'grocery_invalid_promocode',
            'message': f'Promocode {promo} is not valid',
        }
        assert mock_eats_checkout.times_called == 0
        assert grocery_cart.set_order_id_times_called() == 0
    assert grocery_cart.checkout_times_called() == 1


@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_badrequest(
        taxi_grocery_orders,
        mockserver,
        now,
        grocery_cart,
        taxi_config,
        yamaps_local,
):

    user_provider = 'eats'

    taxi_config.set_values({'GROCERY_ORDERS_CHECKOUT_PROVIDER': user_provider})

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        return mockserver.make_response(
            '{"message": "bad request", "status": "error"}', status=400,
        )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
            },
        },
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'bad_request'
    assert mock_eats_checkout.times_called == 1
    assert grocery_cart.checkout_times_called() == 1
    assert yamaps_local.times_called() == 1


@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_entrance_from_request(
        taxi_grocery_orders,
        mockserver,
        now,
        grocery_cart,
        taxi_config,
        yamaps_local,
):

    user_provider = 'eats'

    taxi_config.set_values({'GROCERY_ORDERS_CHECKOUT_PROVIDER': user_provider})

    entrance = 'some-test-entrance'

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        assert request.json['user']['address']['entrance'] == entrance
        return mockserver.make_response(
            '{"message": "bad request", "status": "error"}', status=400,
        )

    await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
                'entrance': entrance,
            },
        },
        headers=COMMON_HEADERS,
    )

    assert mock_eats_checkout.times_called == 1
    assert yamaps_local.times_called() == 1
    assert grocery_cart.checkout_times_called() == 1


@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_no_house(
        taxi_grocery_orders,
        mockserver,
        now,
        grocery_cart,
        taxi_config,
        yamaps_local,
):
    user_provider = 'eats'

    taxi_config.set_values({'GROCERY_ORDERS_CHECKOUT_PROVIDER': user_provider})

    yamaps_local.set_data(house='')

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        return mockserver.make_response(
            '{"message": "bad request", "status": "error"}', status=400,
        )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
            },
        },
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_address',
        'message': 'Delivery address is invalid',
    }
    assert mock_eats_checkout.times_called == 0
    assert grocery_cart.checkout_times_called() == 1
    assert yamaps_local.times_called() == 1


@POLL_EATS_EXPERIMENT
@pytest.mark.now(datetime.datetime(2020, 3, 25, 10, 0, 0).isoformat())
@pytest.mark.config(GROCERY_ORDERS_CHECKOUT_TYPE='eats')
async def test_delivery_cost(
        taxi_grocery_orders,
        mockserver,
        now,
        grocery_cart,
        yamaps_local,
        grocery_depots,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)

    now = now.replace(tzinfo=pytz.UTC)

    item = models.GroceryCartItem(item_id='item-id', price='10')
    grocery_cart.set_items(items=[item])

    delivery_cost = '199.99'
    grocery_cart.set_order_conditions(delivery_cost=delivery_cost, max_eta=15)

    @mockserver.json_handler('/grocery-wms-gateway/v1/orders/add')
    def mock_order_add(request):
        assert request.json['order']['id'] == SOME_ORDER_ID
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

    @mockserver.json_handler('/grocery-cart/internal/v1/cart/set-order-id')
    def mock_set_order_id(request):
        assert request.json == {
            'order_id': SOME_ORDER_ID,
            'cart_id': SOME_CART_ID,
        }
        return {}

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        assert (
            request.headers['X-Request-Application']
            == 'app_name=yango_android'
        )
        assert request.headers['X-YaTaxi-UserId'] == 'uuu'
        assert request.json['delivery'] == {
            'date': (now + datetime.timedelta(minutes=15)).isoformat(),
            'deliveryTime': 15,
            'fee': delivery_cost,
            'preparationTime': 0,
        }

        assert len(request.json['items']) == 1
        response_item = request.json['items'][0]
        assert response_item['id'] == item.item_id
        assert response_item['name'] == item.title
        assert response_item['price'] == item.price

        return {'payload': {'number': SOME_ORDER_ID}}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'position': {
                'location': [37, 55],
                'place_id': 'yamaps://12345',
                'floor': '13',
                'flat': '666',
                'doorcode': '42',
                'doorcode_extra': 'doorcode_extra',
                'building_name': 'building_name',
                'doorbell_name': 'doorbell_name',
                'left_at_door': False,
                'comment': 'please, fast!',
            },
        },
        headers=COMMON_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': SOME_ORDER_ID}

    assert mock_eats_checkout.times_called == 1
    assert grocery_cart.checkout_times_called() == 1
    assert yamaps_local.times_called() == 1
    assert mock_set_order_id.times_called == 1
    assert mock_order_add.times_called == 1


@pytest.mark.parametrize(
    'cart_cashback_flow, eats_action, cashback_to_pay',
    [('charge', 'use', '100'), ('gain', 'save_up', None)],
)
async def test_submit_with_cashback(
        taxi_grocery_orders,
        eats_core_eater,
        mockserver,
        grocery_cart,
        cart_cashback_flow,
        eats_action,
        cashback_to_pay,
):
    personal_email_id = 'personal_email_id-x123'
    eats_core_eater.set_personal_email_id(personal_email_id)

    item = models.GroceryCartItem(
        item_id='item-id', price='10', full_price='20',
    )
    grocery_cart.set_items(items=[item])

    payment_id = 'card-x1233421'
    payment_type = 'card'

    wallet_id = 'w/12312312213'

    grocery_cart.set_payment_method({'type': payment_type, 'id': payment_id})
    grocery_cart.set_cashback_data(
        flow=cart_cashback_flow, cashback_to_pay=cashback_to_pay,
    )

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        json = request.json

        ya_taxi_user = f'personal_phone_id={headers.PERSONAL_PHONE_ID}'
        ya_taxi_user += f',personal_email_id={personal_email_id}'
        ya_taxi_user += f',eats_user_id={headers.EATS_USER_ID}'

        assert request.headers['X-YaTaxi-User'] == ya_taxi_user

        assert json['payment'] == {
            'method': 'eats-payments',
            'currencyCode': 'RUB',
        }

        payment_info = {
            'id': payment_id,
            'type': payment_type,
            'cashback': {'action': eats_action, 'id': wallet_id},
        }

        if cashback_to_pay is not None:
            payment_info['cashback']['amount'] = cashback_to_pay

        assert json['paymentInformation'] == payment_info

        return {'payload': {'number': SOME_ORDER_ID}}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'payment_method_type': payment_type,
            'payment_method_id': payment_id,
            'cashback': {
                'wallet_id': wallet_id,
                'cashback_to_pay': cashback_to_pay,
            },
            'flow_version': 'eats_payments',
            'position': DEFAULT_POSITION,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': SOME_ORDER_ID}

    assert mock_eats_checkout.times_called == 1


async def test_submit_with_charity(
        taxi_grocery_orders, eats_core_eater, mockserver, grocery_cart,
):
    personal_email_id = 'personal_email_id-x123'
    eats_core_eater.set_personal_email_id(personal_email_id)

    item = models.GroceryCartItem(
        item_id='item-id', price='10', full_price='20',
    )
    grocery_cart.set_items(items=[item])

    payment_id = 'card-x1233421'
    payment_type = 'card'

    grocery_cart.set_payment_method({'type': payment_type, 'id': payment_id})

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        json = request.json

        assert json['donationOrder'] == {'type': 'roundup'}

        return {'payload': {'number': SOME_ORDER_ID}}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'payment_method_type': payment_type,
            'payment_method_id': payment_id,
            'flow_version': 'eats_payments',
            'position': DEFAULT_POSITION,
            'charity': {'type': 'helping_hand'},
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': SOME_ORDER_ID}

    assert mock_eats_checkout.times_called == 1


async def test_no_personal_email_id(
        taxi_grocery_orders, eats_core_eater, mockserver, grocery_cart,
):
    item = models.GroceryCartItem(
        item_id='item-id', price='10', full_price='20',
    )
    grocery_cart.set_items(items=[item])

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def mock_eats_checkout(request):
        return {'payload': {'number': SOME_ORDER_ID}}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'payment_method_type': 'card',
            'payment_method_id': 'payment_id',
            'flow_version': 'eats_payments',
            'position': DEFAULT_POSITION,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'no_personal_email_id'

    assert mock_eats_checkout.times_called == 0


async def test_no_payment_id(
        taxi_grocery_orders, eats_core_eater, mockserver, grocery_cart,
):
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'payment_method_type': 'card',
            'flow_version': 'eats_payments',
            'position': DEFAULT_POSITION,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'bad_payment_method'


@pytest.mark.parametrize(
    'cart_cashback_flow, amount_to_pay',
    [
        pytest.param(
            'charge',
            None,
            id='Charge cashback without cashback amount to pay',
        ),
        pytest.param(
            'gain', '100', id='Gain cashback with cashback amount to pay',
        ),
    ],
)
async def test_submit_with_cashback_errors(
        taxi_grocery_orders,
        eats_core_eater,
        grocery_cart,
        cart_cashback_flow,
        amount_to_pay,
):
    item = models.GroceryCartItem(
        item_id='item-id', price='10', full_price='20',
    )
    grocery_cart.set_items(items=[item])

    payment_id = 'card-x1233421'
    payment_type = 'card'

    wallet_id = 'w/12312312213'

    grocery_cart.set_payment_method({'type': payment_type, 'id': payment_id})
    grocery_cart.set_cashback_data(flow=cart_cashback_flow)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': 4,
            'offer_id': 'yyy',
            'payment_method_type': payment_type,
            'payment_method_id': payment_id,
            'cashback': {
                'wallet_id': wallet_id,
                'cashback_to_pay': amount_to_pay,
            },
            'flow_version': 'eats_payments',
            'position': DEFAULT_POSITION,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'bad_request'
