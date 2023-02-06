import copy
import datetime
import uuid

import pytest

from . import headers
from . import models
from . import experiments

# pylint: disable=too-many-lines

DEPOT_ID = '2809'
DEPOT_LOCATION = [13.0, 37.0]
CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_ID_PREFIX = '00000000-0000-0000-0000-d980131005'

HEADERS = {
    'X-YaTaxi-Pass-Flags': 'ya-plus',
    'X-YaTaxi-User': 'eats_user_id=test_eats_user_id',
    'X-YaTaxi-Session': 'test_domain:test_session',
    'X-YaTaxi-Bound-Sessions': 'old_test_domain:old_test_session',
}

EMPTY_ORDERS_TRACKING = {
    'meta': {'count': 0},
    'payload': {'trackedOrders': []},
}

EATS_RESPONSE_JSON = {
    'id': '200817-087689',
    'eats_id': '200817-087689',
    'status': 'accepted',
    'performer': {'name': 'Philip J. Fry'},
    'check_after': 15,
    'contact': {'phone': '+79998887766', 'type': 'courier'},
    'contacts': [
        {
            'title': 'Do not ever call here!',
            'phone': '+74956970349',
            'type': 'courier',
        },
    ],
    'actions': [{'type': 'cancel_order', 'title': 'Get Rid Of Damn Order'}],
}

USE_DYNAMIC_DELIVERY_ETA = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'use_dynamic_delivery_eta': True},
        },
    ],
    is_config=True,
)

DEFAULT_ETA = 55

# we have to use actual now here,
# because we use PG's NOW() in cache and it's not mockable
NOW_FOR_CACHE = datetime.datetime.now()


@pytest.fixture(name='orders_state')
def _orders_state(mockserver, taxi_grocery_orders):
    async def _inner(order):
        return await taxi_grocery_orders.post(
            '/lavka/v1/orders/v1/state',
            headers=headers.DEFAULT_HEADERS,
            json={'known_orders': [{'id': order.order_id}]},
        )

    return _inner


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.parametrize('poll_eats', [True, False])
async def test_basic(taxi_grocery_orders, mockserver, load_json, poll_eats):
    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def mock_eda_orders_tracking(request):
        for key, value in HEADERS.items():
            assert request.headers[key] == value
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=HEADERS,
        json={'known_orders': [], 'should_poll_eats': poll_eats},
    )
    assert response.status_code == 200
    eats_orders_expected = []
    if poll_eats:
        eats_orders_expected = [eats_orders['payload']['trackedOrders'][0]]
        assert mock_eda_orders_tracking.times_called == 1

    assert response.json() == {
        'grocery_orders': [],
        'eats_orders': eats_orders_expected,
    }


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_eda_is_down(
        taxi_grocery_orders, mockserver, pgsql, grocery_depots, grocery_cart,
):
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def mock_eda_orders_tracking(request):
        return mockserver.make_response('fail', status=500)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1
    assert response.json()['grocery_orders'][0]['id'] == order.order_id

    assert mock_eda_orders_tracking.times_called > 0  # depends on retry count


TIME_START_ORDER = '2020-05-25T14:39:42+00:00'
TIME_NOW = '2020-05-25T17:43:45+03:00'
TIME_START_DELIVERY = '2020-05-25T17:40:45+03:00'
PASSED_FROM_START = 2

TIME_DELIVERED_ETA_FUTURE = '2020-05-25T17:46:42+03:00'
TIME_DELIVERED_ETA_PAST = '2020-05-25T17:43:42+03:00'
LEFT_FOR_DELIVERED = 3


PICKUPED_TIME_OK_CANCEL_1 = '2020-05-25T17:48:45+03:00'
PICKUPED_TIME_OK_CANCEL_2 = '2020-05-25T17:47:45+03:00'
PICKUPED_TIME_OK_CANCEL_3 = '2020-05-25T17:45:45+03:00'
PICKUPED_TIME_OK_CANCEL_4 = '2020-05-25T17:40:45+03:00'


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.now(TIME_NOW)
@pytest.mark.parametrize(
    'has_eta, time_passed', [(True, True), (True, False), (False, False)],
)
async def test_basic_delivery_eta(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        testpoint,
        has_eta,
        time_passed,
        cargo,
        grocery_depots,
        grocery_cart,
):
    if time_passed:
        delivery_eta = 2
    else:
        delivery_eta = 5

    if has_eta:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id='some_dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='new',
            dispatch_start_delivery_ts=TIME_START_DELIVERY,
            dispatch_delivery_eta=delivery_eta,
        )
    else:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id='some_dispatch_id',
            dispatch_driver_id='driver_id',
            dispatch_status='delivering',
            dispatch_cargo_status='new',
            dispatch_transport_type='car',
            dispatch_car_number='A000AA79',
        )

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=dispatch_status_info,
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id == order.order_id
        return TIME_START_ORDER

    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )
    assert response.status_code == 200

    if has_eta:
        if not time_passed:
            assert response.json()['grocery_orders'][0][
                'delivery_eta_min'
            ] == max(delivery_eta - PASSED_FROM_START, delivery_eta)
        else:
            assert (
                response.json()['grocery_orders'][0]['delivery_eta_min']
                == delivery_eta
            )
    else:
        assert (
            response.json()['grocery_orders'][0]['delivery_eta_min']
            == DEFAULT_ETA
            - (_stringtime(TIME_NOW) - _stringtime(TIME_START_ORDER)).seconds
            // 60
        )
        assert (
            response.json()['grocery_orders'][0]['courier_info']['car_number']
            == 'A000AA79'
        )
        assert (
            response.json()['grocery_orders'][0]['courier_info']['driver_id']
            == 'driver_id'
        )


@USE_DYNAMIC_DELIVERY_ETA
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.now(TIME_NOW)
@pytest.mark.parametrize(
    'has_delivered_eta,time_passed',
    [(True, True), (True, False), (False, False)],
)
async def test_dynamic_delivery_eta(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        testpoint,
        has_delivered_eta,
        time_passed,
        cargo,
        grocery_depots,
        grocery_cart,
        experiments3,
):
    min_delivery_eta = 2
    if has_delivered_eta:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id='some_dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='new',
            dispatch_start_delivery_ts=TIME_START_DELIVERY,
            dispatch_delivery_eta=min_delivery_eta,
            dispatch_delivered_eta_ts=TIME_DELIVERED_ETA_PAST
            if time_passed
            else TIME_DELIVERED_ETA_FUTURE,
        )
    else:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id='some_dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='new',
        )

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=dispatch_status_info,
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id == order.order_id
        return TIME_START_ORDER

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )
    assert response.status_code == 200

    order_response = response.json()['grocery_orders'][0]
    if has_delivered_eta:
        if not time_passed:
            assert order_response['delivery_eta_min'] == LEFT_FOR_DELIVERED
        else:
            assert order_response['delivery_eta_min'] == min_delivery_eta
    else:
        assert (
            response.json()['grocery_orders'][0]['delivery_eta_min']
            == DEFAULT_ETA
            - (_stringtime(TIME_NOW) - _stringtime(TIME_START_ORDER)).seconds
            // 60
        )


@pytest.mark.now(TIME_NOW)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_no_dynamic_delivery_eta_without_config(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
):
    delivery_eta = 8
    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id='some_dispatch_id',
        dispatch_status='delivering',
        dispatch_cargo_status='new',
        dispatch_start_delivery_ts=TIME_START_DELIVERY,
        dispatch_delivery_eta=delivery_eta,
        dispatch_delivered_eta_ts=TIME_DELIVERED_ETA_FUTURE,
    )

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=dispatch_status_info,
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
    )
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )
    assert response.status_code == 200

    order_response = response.json()['grocery_orders'][0]
    assert order_response['delivery_eta_min'] == max(
        delivery_eta, delivery_eta - PASSED_FROM_START,
    )


@pytest.mark.parametrize(
    'order_status, desired_order_status',
    [
        ('assembling', 'canceled'),
        ('delivering', 'canceled'),
        ('assembling', 'closed'),
        ('assembling', None),
    ],
)
@experiments.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_desired_status(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
        order_status,
        desired_order_status,
):
    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        desired_status=desired_order_status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
        ),
        created=NOW_FOR_CACHE,
    )

    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )

    expected_status = (
        'closed' if desired_order_status is not None else order_status
    )
    expected_resolution = (
        'succeeded' if desired_order_status == 'closed' else 'canceled'
    )

    expected_actions = []
    if expected_status != 'closed':
        expected_actions = [{'type': 'cancel'}, {'type': 'edit_address'}]

    assert response.status_code == 200
    response_order = response.json()['grocery_orders'][0]
    assert response_order['id'] == order.order_id
    assert response_order['status'] == expected_status
    assert response_order['actions'] == expected_actions

    if expected_status == 'closed':
        assert response_order['resolution'] == expected_resolution
    else:
        assert 'resolution' not in response_order


@pytest.mark.now(TIME_NOW)
@pytest.mark.parametrize(
    'pickuped_ts,has_cancel',
    [
        (None, True),
        (PICKUPED_TIME_OK_CANCEL_1, True),
        (PICKUPED_TIME_OK_CANCEL_2, True),
        (PICKUPED_TIME_OK_CANCEL_3, True),
        (PICKUPED_TIME_OK_CANCEL_4, True),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_cancel_action(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
        pickuped_ts,
        has_cancel,
):
    order = models.Order(
        pgsql=pgsql,
        status='assembling',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='',
            dispatch_status='accepted',
            dispatch_cargo_status='performer_found',
            dispatch_courier_name='SomeCourierName',
            dispatch_pickuped_eta_ts=pickuped_ts,
        ),
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
    )

    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    eats_orders = load_json('eda_orders_tracking_response.json')

    cargo.set_data(cargo_courier_position_error=404)

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    order_response = response.json()['grocery_orders'][0]

    if has_cancel:
        assert {'type': 'cancel'} in order_response['actions']
    else:
        assert {'type': 'cancel'} not in order_response['actions']


def compare_state_response(resp, ethalon):
    resp['grocery_orders'].sort(key=lambda kv: kv['id'])
    ethalon['grocery_orders'].sort(key=lambda kv: kv['id'])
    assert resp == ethalon


@pytest.mark.parametrize(
    'first_status,second_status,result_is_second',
    [
        ('delivering', 'closed', False),
        ('delivering', 'canceled', False),
        ('closed', 'delivering', True),
        ('canceled', 'delivering', True),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_select_not_closed(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        first_status,
        second_status,
        result_is_second,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
):
    order_1 = models.Order(
        pgsql=pgsql,
        status=first_status,
        cart_id=f'{CART_ID_PREFIX}01',
        created=NOW_FOR_CACHE,
    )
    order_2 = models.Order(
        pgsql=pgsql,
        status=second_status,
        cart_id=f'{CART_ID_PREFIX}02',
        created=NOW_FOR_CACHE,
    )

    grocery_cart.add_cart(cart_id=order_1.cart_id)
    grocery_cart.add_cart(cart_id=order_2.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order_1.depot_id, location=DEPOT_LOCATION,
    )

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json('eda_orders_tracking_response.json'),
        )
        return response

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': []},
    )

    assert response.status_code == 200
    order_id = order_2.order_id if result_is_second else order_1.order_id

    assert len(response.json()['grocery_orders']) == 1
    assert len(response.json()['eats_orders']) == 1
    order = response.json()['grocery_orders'][0]
    assert order['id'] == order_id


@pytest.mark.parametrize(
    'first_status,second_status',
    [('closed', 'canceled'), ('canceled', 'closed')],
)
@pytest.mark.config(GROCERY_ORDERS_ENABLE_CLOSED_ORDERS_STATE_BY_USER=True)
@pytest.mark.config(GROCERY_ORDERS_SHOW_CLOSED_ORDERS_IN_STATE_DURATION=5)
async def test_select_closed_by_timeout(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        first_status,
        second_status,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
):
    # Should be returned
    order_1 = models.Order(
        pgsql=pgsql,
        status=first_status,
        cart_id=f'{CART_ID_PREFIX}01',
        created=NOW_FOR_CACHE - datetime.timedelta(minutes=3),
        finished=NOW_FOR_CACHE,
    )

    # Not returned, too much time passed
    order_2 = models.Order(
        pgsql=pgsql,
        status=second_status,
        cart_id=f'{CART_ID_PREFIX}02',
        created=NOW_FOR_CACHE - datetime.timedelta(minutes=15),
        finished=NOW_FOR_CACHE - datetime.timedelta(minutes=10),
    )

    grocery_cart.add_cart(cart_id=order_1.cart_id)
    grocery_cart.add_cart(cart_id=order_2.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order_1.depot_id, location=DEPOT_LOCATION,
    )

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json('eda_orders_tracking_response.json'),
        )
        return response

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': []},
    )

    assert response.status_code == 200

    assert len(response.json()['grocery_orders']) == 1
    order = response.json()['grocery_orders'][0]
    assert order['id'] == order_1.order_id


@experiments.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_all_orders_by_session(
        taxi_grocery_orders,
        pgsql,
        load_json,
        testpoint,
        mockserver,
        cargo,
        grocery_depots,
        grocery_cart,
):
    order_statuses = [
        {'init': 'assembled', 'response': 'assembled'},
        {'init': 'checked_out', 'response': 'created'},
    ]

    order_country = 'country'
    order_city = 'city'
    order_house = 'house'
    order_street = 'street'
    order_entrance = 'entrance'
    order_floor = 'floor'
    order_first_flat = 'flat'
    order_second_flat = 'talf'
    order_doorcode = 'doorcode'
    order_left_at_door = True
    order_meet_outside = True
    order_no_door_call = True
    place_id = 'place_id'
    postal_code = 'postal_code'
    country_iso2 = 'country_iso2'

    order_1 = models.Order(
        pgsql=pgsql,
        status=order_statuses[0]['init'],
        cart_id=f'{CART_ID_PREFIX}01',
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_first_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        postal_code=postal_code,
    )
    order_2 = models.Order(
        pgsql=pgsql,
        status=order_statuses[1]['init'],
        cart_id=f'{CART_ID_PREFIX}02',
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_second_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        postal_code=postal_code,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id in [order_1.order_id, order_2.order_id]
        return TIME_START_ORDER

    grocery_cart.add_cart(cart_id=order_1.cart_id)
    grocery_cart.add_cart(cart_id=order_2.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order_1.depot_id,
        location=DEPOT_LOCATION,
        country_iso2=country_iso2,
    )

    eta_info = {
        'localized_promise': 'Заказ приедет к ~18:35',
        'promise_max': '2020-05-25T15:35:00+00:00',
        'delivery_eta_min': DEFAULT_ETA,
    }
    # We check proper translation in separate test
    tracking_info = {'title': 'order_remaining_time'}
    eta_info['tracking_info'] = tracking_info

    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': []},
    )

    compare_state_response(
        response.json(),
        {
            'grocery_orders': [
                {
                    'id': order_1.order_id,
                    'short_order_id': order_1.short_order_id,
                    'delivery_type': 'courier',
                    'status': order_statuses[0]['response'],
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order_1.cart_id,
                    'location': order_1.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'house': order_house,
                        'street': order_street,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_first_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'postal_code': postal_code,
                        'country_iso2': country_iso2,
                    },
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                },
                {
                    'id': order_2.order_id,
                    'short_order_id': order_2.short_order_id,
                    'delivery_type': 'courier',
                    'status': order_statuses[1]['response'],
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order_2.cart_id,
                    'location': order_2.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'house': order_house,
                        'street': order_street,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_second_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'postal_code': postal_code,
                        'country_iso2': country_iso2,
                    },
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                },
            ],
            'eats_orders': [eats_orders['payload']['trackedOrders'][0]],
        },
    )


@pytest.mark.parametrize(
    'session_in_pg, yandex_uid_in_pg',
    [
        ('session_1', 'yandex_uid1'),
        ('session_1', 'yandex_uid2'),
        ('session_2', 'yandex_uid1'),
        ('session_1', None),
    ],
)
@pytest.mark.parametrize(
    'request_bound_sessions, request_yandex_uid',
    [
        (['session_3', 'session_2'], None),
        (['session_3'], 'yandex_uid1'),
        (['session_3'], 'yandex_uid3'),
    ],
)
@experiments.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_orders_by_bound_sessions(
        taxi_grocery_orders,
        pgsql,
        mockserver,
        testpoint,
        session_in_pg,
        yandex_uid_in_pg,
        request_bound_sessions,
        request_yandex_uid,
        cargo,
        grocery_depots,
        grocery_cart,
):
    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def mock_eda_orders_tracking(request):
        return EMPTY_ORDERS_TRACKING

    order_country = 'country'
    order_city = 'city'
    order_house = 'house'
    order_street = 'street'
    order_entrance = 'entrance'
    order_floor = 'floor'
    order_flat = 'flat'
    order_doorcode = 'doorcode'
    order_left_at_door = True
    order_meet_outside = True
    order_no_door_call = True
    place_id = 'place_id'
    postal_code = 'postal_code'
    country_iso2 = 'country_iso2'

    order = models.Order(
        pgsql=pgsql,
        session=session_in_pg,
        yandex_uid=yandex_uid_in_pg,
        status='reserving',
        cart_id=CART_ID,
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        postal_code=postal_code,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id == order.order_id
        return TIME_START_ORDER

    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        location=DEPOT_LOCATION,
        country_iso2=country_iso2,
    )

    headers_bounds = copy.deepcopy(headers.DEFAULT_HEADERS)
    headers_bounds['X-YaTaxi-Bound-Sessions'] = ','.join(
        request_bound_sessions,
    )
    if request_yandex_uid:
        headers_bounds['X-Yandex-Uid'] = request_yandex_uid

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers_bounds,
        json={'known_orders': []},
    )

    eta_info = {
        'localized_promise': 'Заказ приедет к ~18:35',
        'promise_max': '2020-05-25T15:35:00+00:00',
        'delivery_eta_min': DEFAULT_ETA,
    }
    # We check proper translation in separate test
    tracking_info = {'title': 'order_remaining_time'}
    eta_info['tracking_info'] = tracking_info

    should_find = False
    if yandex_uid_in_pg is not None and yandex_uid_in_pg == request_yandex_uid:
        should_find = True
    if session_in_pg in request_bound_sessions:
        should_find = True

    if not should_find:
        assert response.json() == {'grocery_orders': [], 'eats_orders': []}
    else:
        assert response.json() == {
            'grocery_orders': [
                {
                    'id': order.order_id,
                    'short_order_id': order.short_order_id,
                    'delivery_type': 'courier',
                    'status': 'created',
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order.cart_id,
                    'location': order.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'house': order_house,
                        'street': order_street,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'postal_code': postal_code,
                        'country_iso2': country_iso2,
                    },
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                },
            ],
            'eats_orders': [],
        }

    assert mock_eda_orders_tracking.times_called == 1


@pytest.mark.parametrize(
    'init_status,times_tracking_called,response_status,'
    'cancel_reason_type,resolution',
    [
        ('delivering', 1, 'assembled', None, None),
        ('closed', 1, 'closed', None, 'succeeded'),
        ('canceled', 1, 'closed', 'failure', 'failed'),
        ('canceled', 1, 'closed', 'timeout', 'failed'),
        ('canceled', 1, 'closed', 'user_request', 'canceled'),
    ],
)
@experiments.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_orders_not_closed_by_bound_sessions(
        taxi_grocery_orders,
        pgsql,
        mockserver,
        testpoint,
        init_status,
        times_tracking_called,
        response_status,
        cargo,
        cancel_reason_type,
        resolution,
        grocery_depots,
        grocery_cart,
):
    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def mock_eda_orders_tracking(request):
        return EMPTY_ORDERS_TRACKING

    order_country = 'country'
    order_city = 'city'
    order_house = 'house'
    order_street = 'street'
    order_entrance = 'entrance'
    order_floor = 'floor'
    order_flat = 'flat'
    order_doorcode = 'doorcode'
    order_left_at_door = True
    order_meet_outside = True
    order_no_door_call = True
    place_id = 'place_id'
    postal_code = 'postal_code'
    country_iso2 = 'country_iso2'

    order = models.Order(
        pgsql=pgsql,
        session='111',
        status=init_status,
        cancel_reason_type=cancel_reason_type,
        cart_id=CART_ID,
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        postal_code=postal_code,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id == order.order_id
        return TIME_START_ORDER

    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        location=DEPOT_LOCATION,
        country_iso2=country_iso2,
    )

    headers_bounds = headers.DEFAULT_HEADERS
    headers_bounds['X-YaTaxi-Bound-Sessions'] = '111, 222'
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers_bounds,
        json={'known_orders': []},
    )

    eta_info = {}
    tracking_info_enabled_statuses = set(
        [
            'checked_out',
            'reserved',
            'reserving',
            'assembled',
            'assembling',
            'delivering',
        ],
    )
    if init_status in tracking_info_enabled_statuses:
        eta_info = {
            'localized_promise': 'Заказ приедет к ~18:35',
            'promise_max': '2020-05-25T15:35:00+00:00',
            'delivery_eta_min': DEFAULT_ETA,
        }
        # We check proper translation in separate test
        tracking_info = {'title': 'order_remaining_time'}
        eta_info['tracking_info'] = tracking_info

    if init_status == 'delivering':
        if resolution:
            resolution_response = {'resolution': resolution}
        else:
            resolution_response = {}

        assert response.json() == {
            'grocery_orders': [
                {
                    'id': order.order_id,
                    'short_order_id': order.short_order_id,
                    'delivery_type': 'courier',
                    'status': response_status,
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    # init_status - delivering, but no dispatch_status_info
                    # -> map it to GroceryOrderStatus::kAssembled
                    # -> its possible to cancel order
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order.cart_id,
                    'location': order.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'house': order_house,
                        'street': order_street,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'postal_code': postal_code,
                        'country_iso2': country_iso2,
                    },
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **resolution_response,
                    **eta_info,
                },
            ],
            'eats_orders': [],
        }
    else:
        assert response.json() == {'grocery_orders': [], 'eats_orders': []}

    assert mock_eda_orders_tracking.times_called == times_tracking_called


@pytest.mark.parametrize(
    'init_status,response_status,cargo_error_code,has_dispatch_info,'
    'cargo_times_called,has_position',
    [
        ('closed', 200, None, True, 0, False),
        ('canceled', 200, None, True, 0, False),
        ('pending_cancel', 200, None, True, 0, False),
        ('delivering', 200, None, True, 2, True),
        ('delivering', 200, None, False, 0, False),
        ('delivering', 200, 409, True, 2, False),
        ('delivering', 200, 404, True, 2, False),
        ('assembling', 200, None, True, 0, False),
        ('assembling', 200, None, False, 0, False),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_courier_position(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        init_status,
        response_status,
        cargo_error_code,
        has_dispatch_info,
        cargo_times_called,
        has_position,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
):
    if has_dispatch_info:
        dispatch_info = models.DispatchStatusInfo(
            dispatch_id='some_dispatch_id',
            dispatch_status='accepted',
            dispatch_cargo_status='new',
        )
    else:
        dispatch_info = models.DispatchStatusInfo()

    order_1 = models.Order(
        pgsql=pgsql,
        status=init_status,
        dispatch_status_info=dispatch_info,
        cart_id=f'{CART_ID_PREFIX}01',
        created=NOW_FOR_CACHE,
    )
    order_2 = models.Order(
        pgsql=pgsql,
        status=init_status,
        dispatch_status_info=dispatch_info,
        cart_id=f'{CART_ID_PREFIX}02',
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order_1.cart_id)
    grocery_cart.add_cart(cart_id=order_2.cart_id)

    grocery_depots.add_depot(legacy_depot_id=order_1.depot_id)

    cargo.set_data(cargo_courier_position_error=cargo_error_code)

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json('eda_orders_tracking_response.json'),
        )
        return response

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': [
                {'id': order_1.order_id},
                {'id': order_2.order_id},
            ],
        },
    )

    assert response.status_code == response_status

    assert len(response.json()['grocery_orders']) == 2
    assert len(response.json()['eats_orders']) == 1

    assert cargo.times_courier_position_called() == cargo_times_called

    for order in response.json()['grocery_orders']:
        if has_position:
            assert 'position' in order['courier_info']
        else:
            assert 'position' not in order['courier_info']


@pytest.mark.parametrize(
    'init_status, dispatch_status, dispatch_cargo_status, transport_type,'
    ' result_status, has_open_action',
    [
        (
            'delivering',
            'accepted',
            'performer_found',
            None,
            'assembled',
            False,
        ),
        (
            'delivering',
            'accepted',
            'performer_found',
            'rover',
            'assembled',
            False,
        ),
        ('delivering', 'delivering', 'pickuped', 'rover', 'delivering', False),
        (
            'delivering',
            'delivering',
            'ready_for_delivery_confirmation',
            'rover',
            'delivery_arrived',
            True,
        ),
        (
            'delivering',
            'delivering',
            'delivery_arrived',
            'rover',
            'delivering',
            False,
        ),
        (
            'delivering',
            'delivering',
            'ready_for_delivery_confirmation',
            'car',
            'delivery_arrived',
            False,
        ),
        (
            'delivering',
            'delivering',
            'delivery_arrived',
            None,
            'delivery_arrived',
            False,
        ),
    ],
)
@pytest.mark.translations(
    grocery_orders={
        'courier_arrived_to_client_title': {'RU': 'Курьер уже у дома'},
        'courier_arrived_to_client_subtitle': {
            'RU': 'Нужно ещё несколько минут, чтобы вас найти',
        },
    },
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_rover_open_hatch(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        grocery_depots,
        grocery_cart,
        cargo,
        init_status,
        dispatch_status,
        dispatch_cargo_status,
        transport_type,
        result_status,
        has_open_action,
):
    dispatch_info = models.DispatchStatusInfo(
        dispatch_id='some_dispatch_id',
        dispatch_status=dispatch_status,
        dispatch_cargo_status=dispatch_cargo_status,
        dispatch_transport_type=transport_type,
    )

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        dispatch_status_info=dispatch_info,
        cart_id=f'{CART_ID_PREFIX}01',
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json('eda_orders_tracking_response.json'),
        )
        return response

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    assert response.status_code == 200

    assert len(response.json()['grocery_orders']) == 1
    assert len(response.json()['eats_orders']) == 1

    response_order = response.json()['grocery_orders'][0]
    assert response_order['status'] == result_status
    if has_open_action:
        assert {'type': 'rover_open_hatch'} in response_order['actions']
    else:
        assert {'type': 'rover_open_hatch'} not in response_order['actions']
    if result_status == 'delivery_arrived' and transport_type != 'rover':
        assert response_order['tracking_info'] == {
            'title': 'Курьер уже у дома',
            'subtitle': 'Нужно ещё несколько минут, чтобы вас найти',
        }


@pytest.mark.parametrize(
    'delivery_type,address,directions,short_address',
    [
        (
            'pickup',
            'Москва, Льва Толстого 16',
            'Подняться по лестнице',
            'Льва Толстого, 16',
        ),
        ('pickup', None, 'Подняться по лестнице', None),
        ('pickup', 'Москва, Льва Толстого 16', None, 'Льва Толстого, 16'),
        ('pickup', None, None, None),
        (
            'eats_dispatch',
            'Москва, Льва Толстого 16',
            'Подняться по лестнице',
            'Льва Толстого, 16',
        ),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_depot_info(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        load_json,
        cargo,
        grocery_depots,
        grocery_cart,
        delivery_type,
        address,
        directions,
        short_address,
):
    order = models.Order(pgsql=pgsql, cart_id=CART_ID, created=NOW_FOR_CACHE)
    grocery_cart.set_delivery_type(delivery_type)
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        address=address,
        directions=directions,
        short_address=short_address,
    )

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json('eda_orders_tracking_response.json'),
        )
        return response

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    assert response.status_code == 200

    response_order = response.json()['grocery_orders'][0]

    if delivery_type == 'pickup':
        depot_info = response_order['depot_info']

        for field, value in [
                ('address', address),
                ('directions', directions),
                ('short_address', short_address),
        ]:
            if value is not None:
                assert depot_info[field] == value
            else:
                assert field not in depot_info
    else:
        assert 'depot_info' not in response_order


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_just_created_order(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        mockserver,
        load_json,
):
    # Fill in depot caches etc
    # await taxi_grocery_orders.tests_control(invalidate_caches=True)
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        yandex_uid=headers.YANDEX_UID,
        session=HEADERS['X-YaTaxi-Session'],
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1
    assert response.json()['grocery_orders'][0]['id'] == order.order_id

    # Now with old cache
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        yandex_uid=headers.YANDEX_UID,
        session=HEADERS['X-YaTaxi-Session'],
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 2
    assert (
        response.json()['grocery_orders'][0]['id'] == order.order_id
        or response.json()['grocery_orders'][1]['id'] == order.order_id
    )


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.parametrize(
    'old_order_days_ago, is_found_in_cache',
    # 30 is a magic number hardcoded in c++ code,
    # so cache only contains orders for last 30 days
    [(29, True), (31, False)],
)
async def test_orders_cache_ttl(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        testpoint,
        old_order_days_ago,
        is_found_in_cache,
):
    def _setup_order(created):
        order = models.Order(
            pgsql=pgsql,
            created=created,
            status='reserving',
            yandex_uid=headers.YANDEX_UID,
            session=HEADERS['X-YaTaxi-Session'],
        )
        grocery_cart.add_cart(cart_id=order.cart_id)

        return order

    recent_order = _setup_order(NOW_FOR_CACHE)

    old_order = _setup_order(
        NOW_FOR_CACHE - datetime.timedelta(days=old_order_days_ago),
    )

    grocery_depots.add_depot(legacy_depot_id=recent_order.depot_id)

    @testpoint('orders_not_found_in_cache')
    def orders_not_found_in_cache_tp(data):
        assert data == {'count': 1}

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [
                {'id': recent_order.order_id},
                {'id': old_order.order_id},
            ],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 2

    if not is_found_in_cache:
        assert orders_not_found_in_cache_tp.times_called == 1


@pytest.mark.parametrize(
    'cargo_dispatch',
    [
        {'dispatch_in_batch': True, 'batch_order_num': 1},
        {'dispatch_in_batch': True},
        None,
    ],
)
async def test_dispatch_batch(
        taxi_grocery_orders,
        pgsql,
        cargo_dispatch,
        grocery_depots,
        grocery_cart,
):
    dispatch_id = 'grocery_dispatch_id123'

    dispatch_status_meta = (
        {'cargo_dispatch': cargo_dispatch}
        if cargo_dispatch is not None
        else None
    )

    order = models.Order(
        pgsql=pgsql,
        status='closed',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='closed',
            dispatch_cargo_status='delivered',
            dispatch_status_meta=dispatch_status_meta,
        ),
        dispatch_flow='grocery_dispatch',
    )

    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1
    assert response.json()['grocery_orders'][0]['id'] == order.order_id

    if (
            'cargo_dispatch_info'
            in response.json()['grocery_orders'][0]['courier_info'].keys()
    ):
        assert (
            response.json()['grocery_orders'][0]['courier_info'][
                'cargo_dispatch_info'
            ]
            == cargo_dispatch
        )
    else:
        assert cargo_dispatch is None


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
async def test_status_update_order(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        mockserver,
        load_json,
):
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        yandex_uid=headers.YANDEX_UID,
        session=HEADERS['X-YaTaxi-Session'],
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
    )

    order.upsert(status='delivering')
    order.update()

    assert order.status == 'delivering'

    new_status_updated = str(order.status_updated)
    assert new_status_updated != TIME_START_ORDER

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)

    eats_orders = load_json('eda_orders_tracking_response.json')

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return eats_orders

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    assert response.status_code == 200

    response = response.json()['grocery_orders'][0]
    assert response['status_updated'] != new_status_updated


@pytest.mark.config(GROCERY_ORDERS_ADD_PROMISE_TO_RESPONSE=True)
@pytest.mark.parametrize(
    'order_create_time,promise_max,text,locale,timezone',
    [
        pytest.param(
            '2019-01-01T12:00:00+00:00',
            '2019-01-01T12:15:00+00:00',
            'Order will arrive until ~12:15',
            'en',
            'UTC',
            id='en',
        ),
        pytest.param(
            '2019-01-01T12:00:00+03:00',
            '2019-01-01T09:15:00+00:00',
            'Заказ приедет к ~12:15',
            'ru',
            'Europe/Moscow',
            id='ru',
        ),
    ],
)
async def test_promise_localization(
        pgsql,
        testpoint,
        mocked_time,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        order_create_time,
        promise_max,
        text,
        locale,
        timezone,
):
    mocked_time.set(_stringtime(order_create_time))
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        yandex_uid=headers.YANDEX_UID,
        session=HEADERS['X-YaTaxi-Session'],
        created=order_create_time,
        locale=locale,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id == order.order_id
        return order_create_time

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_order_conditions(delivery_cost=10, max_eta=15)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id, timezone=timezone)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1
    assert response.json()['grocery_orders'][0]['id'] == order.order_id
    assert response.json()['grocery_orders'][0]['localized_promise'] == text
    assert response.json()['grocery_orders'][0]['promise_max'] == promise_max


@pytest.mark.config(GROCERY_ORDERS_ADD_PROMISE_TO_RESPONSE=True)
@pytest.mark.parametrize(
    'tips_in_cart, cart_tips_paid_template',
    [
        ({'amount': '10', 'amount_type': 'absolute'}, '10 $SIGN$$CURRENCY$'),
        ({'amount': '100', 'amount_type': 'percent'}, '301 $SIGN$$CURRENCY$'),
    ],
)
async def test_tips_in_cart(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        tips_in_cart,
        cart_tips_paid_template,
):
    order = models.Order(pgsql=pgsql, status='reserving')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_tips(tips_in_cart)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    tips = body['grocery_orders'][0]['tips']

    assert len(body['grocery_orders']) == 1
    assert tips['cart_tips_paid_template'] == cart_tips_paid_template
    assert tips['cart_tips_amount'] == tips_in_cart['amount']
    assert tips['cart_tips_amount_type'] == tips_in_cart['amount_type']
    assert 'ask_for_tips' not in tips


@pytest.mark.config(GROCERY_ORDERS_ADD_PROMISE_TO_RESPONSE=True)
@pytest.mark.parametrize(
    'payment_type, payment_id',
    [
        ('card', 'card-x8c4f98acb5a3666cdcebe158'),
        ('googlepay', 'google_pay-629_5d0b824e_07bf_4369_bd24_6143727a2572'),
    ],
)
async def test_payment_data(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        payment_type,
        payment_id,
):
    order = models.Order(pgsql=pgsql, status='reserving')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method({'type': payment_type, 'id': payment_id})
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )

    assert response.status_code == 200
    order = response.json()['grocery_orders'][0]

    assert order['payment_method_type'] == payment_type
    assert order['payment_method_id'] == payment_id


@pytest.mark.translations(
    grocery_orders={
        'order_remaining_time': {
            'ru': 'Ещё примерно %(minutes)s минут',
            'en': '%(minutes)s more minutes',
        },
    },
)
@pytest.mark.parametrize(
    'created_time,current_time,promise_max,courier_promise,text,'
    'locale,timezone',
    [
        (
            '2019-01-01T12:00:00+0000',
            '2019-01-01T12:00:00+0000',
            '2019-01-01T12:15:00+0000',
            None,
            '15 more minutes',
            'en',
            'UTC',
        ),
        (
            '2019-01-01T12:00:00+0000',
            '2019-01-01T12:00:00+0000',
            '2019-01-01T12:15:00+0000',
            12,
            '12 more minutes',
            'en',
            'UTC',
        ),
        (
            '2019-01-01T09:00:00+0000',
            '2019-01-01T12:00:00+0300',
            '2019-01-01T09:15:00+0000',
            None,
            'Ещё примерно 15 минут',
            'ru',
            'Europe/Moscow',
        ),
        (
            '2019-01-01T12:00:00+0000',
            '2019-01-01T12:30:00+0000',
            '2019-01-01T12:15:00+0000',
            None,
            'Ещё примерно 1 минут',
            'RU',
            'UTC',
        ),
    ],
)
async def test_tracking_info(
        pgsql,
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        cargo,
        created_time,
        current_time,
        promise_max,
        courier_promise,
        text,
        locale,
        timezone,
        mocked_time,
):
    mocked_time.set(_stringtime(current_time))

    order_status = ('assembled',)
    dispatch_status_info = models.DispatchStatusInfo()

    if courier_promise is not None:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id='dispatch_id',
            dispatch_status='delivering',
            dispatch_cargo_status='pickup_arrived',
            dispatch_start_delivery_ts=current_time,
            dispatch_delivery_eta=courier_promise,
        )
        order_status = 'delivering'

    order = models.Order(
        pgsql=pgsql,
        yandex_uid=headers.YANDEX_UID,
        status=order_status,
        session=HEADERS['X-YaTaxi-Session'],
        created=created_time,
        locale=locale,
        dispatch_status_info=dispatch_status_info,
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_order_conditions(delivery_cost=10, max_eta=15)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id, timezone=timezone)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1
    response_order = response.json()['grocery_orders'][0]
    assert response_order['id'] == order.order_id
    assert response_order['tracking_info'] == {'title': text}


@pytest.mark.parametrize(
    'courier_name',
    [
        None,
        '',
        'Ivan',
        'Ivanov Ivan',
        'Ivanov Ivan Ivanovich',
        'Ivanov Ivan Hasin Ogli',
    ],
)
async def test_courier_name(
        pgsql, taxi_grocery_orders, grocery_cart, grocery_depots, courier_name,
):
    courier_first_name = 'Ivan'
    if courier_name == '':
        courier_first_name = ''
    order_status = ('assembled',)

    dispatch_id = 'dispatch_id_123'
    driver_id = 'driver_id_123'

    order = models.Order(
        pgsql=pgsql,
        yandex_uid=headers.YANDEX_UID,
        status=order_status,
        session=HEADERS['X-YaTaxi-Session'],
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='accepted',
            dispatch_cargo_status='accepted',
            dispatch_driver_id=driver_id,
            dispatch_courier_name=courier_name,
            dispatch_courier_first_name=courier_first_name,
        ),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_order_conditions(delivery_cost=10, max_eta=15)

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers={**headers.DEFAULT_HEADERS, **HEADERS},
        json={
            'known_orders': [{'id': order.order_id}],
            'should_poll_eats': False,
        },
    )

    assert response.status_code == 200

    response_order = response.json()['grocery_orders'][0]

    if courier_name is None:
        assert 'none' not in response_order['courier_info'].keys()
    else:
        assert response_order['courier_info']['name'] == courier_first_name


@pytest.mark.experiments3(
    is_config=True,
    name='grocery_orders_source_availability',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'available_sources': ['yango']},
)
@experiments.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=False)
@pytest.mark.now(TIME_START_ORDER)
async def test_filter_orders_by_source(
        taxi_grocery_orders,
        pgsql,
        load_json,
        testpoint,
        mockserver,
        cargo,
        grocery_depots,
        grocery_cart,
):
    order_statuses = [
        {'init': 'assembled', 'response': 'assembled'},
        {'init': 'checked_out', 'response': 'created'},
    ]

    order_country = 'country'
    order_city = 'city'
    order_house = 'house'
    order_street = 'street'
    order_entrance = 'entrance'
    order_floor = 'floor'
    order_first_flat = 'flat'
    order_second_flat = 'talf'
    order_third_flat = 'third flat'
    order_doorcode = 'doorcode'
    order_left_at_door = True
    order_meet_outside = True
    order_no_door_call = True
    place_id = 'place_id'
    postal_code = 'postal_code'
    country_iso2 = 'country_iso2'

    order_1 = models.Order(
        pgsql=pgsql,
        status=order_statuses[0]['init'],
        cart_id=f'{CART_ID_PREFIX}01',
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_first_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        postal_code=postal_code,
    )
    # should not be filtered because order explicitly in known_orders
    order_2 = models.Order(
        pgsql=pgsql,
        status=order_statuses[1]['init'],
        cart_id=f'{CART_ID_PREFIX}02',
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_second_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        app_info='app_name=mobilweb_market_lavka_android',
        app_name='mobilweb_market_lavka_android',
        postal_code=postal_code,
    )

    order_3 = models.Order(
        pgsql=pgsql,
        status=order_statuses[1]['init'],
        cart_id=f'{CART_ID_PREFIX}03',
        country=order_country,
        city=order_city,
        house=order_house,
        street=order_street,
        entrance=order_entrance,
        floor=order_floor,
        flat=order_third_flat,
        doorcode=order_doorcode,
        left_at_door=order_left_at_door,
        meet_outside=order_meet_outside,
        no_door_call=order_no_door_call,
        place_id=place_id,
        created=NOW_FOR_CACHE,
        status_updated=TIME_START_ORDER,
        app_info='app_name=mobilweb_market_lavka_android',
        app_name='mobilweb_market_lavka_android',
        postal_code=postal_code,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id in [
            order_1.order_id,
            order_2.order_id,
            order_3.order_id,
        ]
        return TIME_START_ORDER

    grocery_cart.add_cart(cart_id=order_1.cart_id)
    grocery_cart.add_cart(cart_id=order_2.cart_id)
    grocery_cart.add_cart(cart_id=order_3.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order_1.depot_id,
        location=DEPOT_LOCATION,
        country_iso2=country_iso2,
    )

    eta_info = {
        'localized_promise': 'Заказ приедет к ~18:35',
        'promise_max': '2020-05-25T15:35:00+00:00',
        'delivery_eta_min': DEFAULT_ETA,
    }
    # We check proper translation in separate test
    tracking_info = {'title': 'order_remaining_time'}
    eta_info['tracking_info'] = tracking_info

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        return []

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order_2.order_id}]},
    )

    compare_state_response(
        response.json(),
        {
            'grocery_orders': [
                {
                    'id': order_1.order_id,
                    'short_order_id': order_1.short_order_id,
                    'delivery_type': 'courier',
                    'status': order_statuses[0]['response'],
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order_1.cart_id,
                    'location': order_1.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'house': order_house,
                        'street': order_street,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_first_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'postal_code': postal_code,
                        'country_iso2': country_iso2,
                    },
                    **eta_info,
                },
                {
                    'id': order_2.order_id,
                    'short_order_id': order_2.short_order_id,
                    'delivery_type': 'courier',
                    'status': order_statuses[1]['response'],
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order_2.cart_id,
                    'location': order_2.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'house': order_house,
                        'street': order_street,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_second_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'postal_code': postal_code,
                        'country_iso2': country_iso2,
                    },
                    **eta_info,
                },
            ],
            'eats_orders': [],
        },
    )


@pytest.mark.parametrize(
    'init_status, response_status, dispatch_error_code,'
    'dispatch_times_called, has_position',
    [
        ('closed', 200, None, 0, False),
        ('canceled', 200, None, 0, False),
        ('pending_cancel', 200, None, 0, False),
        ('delivering', 200, None, 1, True),
        ('delivering', 200, 404, 1, False),
        ('assembling', 200, None, 0, False),
        ('assembling', 200, None, 0, False),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_dispatch_performer_position(
        taxi_grocery_orders,
        mockserver,
        pgsql,
        init_status,
        response_status,
        dispatch_error_code,
        dispatch_times_called,
        has_position,
        load_json,
        grocery_dispatch,
        grocery_depots,
        grocery_cart,
        eats_orders_tracking,
):
    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=_get_new_uuid(),
            dispatch_status='created',
            dispatch_cargo_status='new',
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_dispatch.set_data(
        dispatch_id=order.dispatch_status_info.dispatch_id,
        performer_position_error=dispatch_error_code,
    )

    @mockserver.json_handler('/eats-orders-new/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json(
                '../test_orders_state/eda_orders_tracking_response.json',
            ),
        )
        return response

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': [{'id': order.order_id}, {'id': order.order_id}],
        },
    )

    assert response.status_code == response_status

    assert len(response.json()['grocery_orders']) == 1
    assert len(response.json()['eats_orders']) == 1

    assert (
        grocery_dispatch.times_performer_position_called()
        == dispatch_times_called
    )

    for order in response.json()['grocery_orders']:
        if has_position:
            assert 'position' in order['courier_info']
        else:
            assert 'position' not in order['courier_info']


def _stringtime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')


def _get_new_uuid():
    return str(uuid.uuid4())


@pytest.fixture(name='prepare_payment_tracking')
def _prepare_payment_tracking(
        mockserver,
        experiments3,
        load_json,
        grocery_depots,
        grocery_cart,
        pgsql,
):
    def _inner(
            flow,
            order_status,
            hold_status,
            exp_enabled,
            need_track_payment=None,
    ):
        experiments3.add_config(
            name='grocery_orders_payment_tracking_enabled',
            consumers=['grocery-orders/submit'],
            default_value={'enabled': exp_enabled},
        )

        order = models.Order(
            pgsql=pgsql,
            status=order_status,
            grocery_flow_version=flow,
            cart_id=CART_ID,
            order_settings={'need_track_payment': need_track_payment},
        )

        order_state = copy.deepcopy(order.state)
        order_state.hold_money_status = hold_status
        order.upsert(state=order_state)

        grocery_cart.add_cart(cart_id=order.cart_id)

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
        )

        @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
        def _mock_eda_orders_tracking(request):
            response = copy.deepcopy(
                load_json(
                    '../test_orders_state/eda_orders_tracking_response.json',
                ),
            )
            return response

        return order

    return _inner


@pytest.mark.parametrize(
    'flow, order_status, hold_status, exp_enabled, expected',
    [
        ('tristero_flow_v1', 'checked_out', None, None, False),
        ('grocery_flow_v3', 'assembling', None, None, False),
        ('grocery_flow_v3', 'checked_out', 'success', None, False),
        ('grocery_flow_v3', 'checked_out', None, False, False),
        ('grocery_flow_v3', 'checked_out', None, True, True),
    ],
)
async def test_payment_tracking(
        orders_state,
        prepare_payment_tracking,
        flow,
        order_status,
        hold_status,
        exp_enabled,
        expected,
):
    order = prepare_payment_tracking(
        flow=flow,
        order_status=order_status,
        hold_status=hold_status,
        exp_enabled=exp_enabled,
    )

    response = await orders_state(order)

    order_response = response.json()['grocery_orders'][0]

    assert order_response['need_track_payment'] == expected


@pytest.mark.parametrize('need_track_payment', [True, False])
async def test_payment_tracking_with_submit(
        orders_state, prepare_payment_tracking, need_track_payment,
):
    flow = 'grocery_flow_v3'
    order_status = 'checked_out'

    order = prepare_payment_tracking(
        flow=flow,
        order_status=order_status,
        hold_status=None,
        exp_enabled=False,
        need_track_payment=need_track_payment,
    )

    response = await orders_state(order)

    order_response = response.json()['grocery_orders'][0]

    assert order_response['need_track_payment'] == need_track_payment


@pytest.mark.parametrize('load_from_cache', [True, False])
@pytest.mark.parametrize('tips_payment_flow', ['separate', 'with_order'])
async def test_tips_payment_flow_from_order(
        pgsql,
        orders_state,
        mockserver,
        load_json,
        grocery_cart,
        grocery_depots,
        tips_payment_flow,
        load_from_cache,
):
    created = NOW_FOR_CACHE

    if not load_from_cache:
        created = created - datetime.timedelta(days=30)

    order = models.Order(pgsql=pgsql, created=created)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_tips(
        {
            'amount': '10',
            'amount_type': 'absolute',
            'payment_flow': tips_payment_flow,
        },
    )

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    @mockserver.json_handler('/eats-orders/api/v2/orders/tracking')
    def _mock_eda_orders_tracking(request):
        response = copy.deepcopy(
            load_json(
                '../test_orders_state/eda_orders_tracking_response.json',
            ),
        )
        return response

    response = await orders_state(order)

    order_response = response.json()['grocery_orders'][0]
    assert order_response['tips_flow'] == tips_payment_flow
