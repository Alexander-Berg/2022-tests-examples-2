import copy
import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as cart
# pylint: enable=import-error
import pytest

from tests_grocery_orders_tracking import configs
from tests_grocery_orders_tracking import consts
from tests_grocery_orders_tracking import headers
from tests_grocery_orders_tracking import models

# pylint: disable=too-many-lines

DEPOT_LOCATION = [13.0, 37.0]
CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_ID_PREFIX = '00000000-0000-0000-0000-d980131005'

EATS_HEADERS = {
    'X-Yandex-UID': headers.DEFAULT_HEADERS['X-Yandex-UID'],
    'X-Request-Language': headers.DEFAULT_HEADERS['X-Request-Language'],
    'X-Request-Application': headers.DEFAULT_HEADERS['X-Request-Application'],
    'X-Device-Id': headers.DEFAULT_HEADERS['X-AppMetrica-DeviceId'],
}

EMPTY_ORDERS_TRACKING = {
    'meta': {'count': 0},
    'payload': {'trackedOrders': []},
}

DEFAULT_ETA = 55

# we have to use actual now here,
# because we use PG's NOW() in cache and it's not mockable
NOW_FOR_CACHE = datetime.datetime.now()

NO_MONEY_ERROR_TEXT_TITLE = 'No money on card Title'
NO_MONEY_ERROR_TEXT_SUB_TITLE = 'No money on card SubTitle'
COMMON_MONEY_ERROR_TEXT_TITLE = 'Common payment error Title'
COMMON_MONEY_ERROR_TEXT_SUB_TITLE = 'Common payment error SubTitle'

NOW = pytest.mark.now('2020-05-25T17:43:45+03:00')
DEFAULT_TIMESLOT = None
SUPER_TIMESLOT = {
    'start': '2020-05-25T14:00:00+03:00',
    'end': '2020-05-25T20:00:00+03:00',
}

LOCALIZATION_TPL_ARGS = [
    'minutes',
    'short_order_id',
    'courier_short_name',
    'batch_order_num',
    'price',
]
DEFAULT_DELIVERY_ETA = 55
SHORT_ORDER_ID = '280920-a-9501097'
BATCH_ORDER_NUM = 123
COURIER_SHORT_NAME = 'Courier'
DEFAULT_PRICE = '0 $SIGN$$CURRENCY$'
LOCALIZATION_TPL_PARAMS = [
    DEFAULT_DELIVERY_ETA,
    SHORT_ORDER_ID,
    COURIER_SHORT_NAME,
    BATCH_ORDER_NUM,
]

DEFAULT_ORDER_DURATION = 55
SHORT_ORDER_DURATION = 45


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.parametrize('poll_eats', [True, False])
async def test_basic(
        taxi_grocery_orders_tracking,
        load_json,
        poll_eats,
        eats_orders_tracking,
):
    eats_orders = load_json('eda_orders_tracking_response.json')
    eats_orders_tracking.check_tracking_headers(EATS_HEADERS)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [], 'should_poll_eats': poll_eats},
    )
    assert response.status_code == 200
    eats_orders_expected = []
    if poll_eats:
        eats_orders_expected = [eats_orders['payload']['trackedOrders'][0]]
        assert eats_orders_tracking.times_tracking_called() == 1

    assert response.json() == {
        'grocery_orders': [],
        'eats_orders': eats_orders_expected,
    }


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_eda_is_down(
        taxi_grocery_orders_tracking,
        eats_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_cart,
):
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    eats_orders_tracking.set_tracking_error_code(500)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1
    assert response.json()['grocery_orders'][0]['id'] == order.order_id

    assert (
        eats_orders_tracking.times_tracking_called() > 0
    )  # depends on retry count


TIME_START_ORDER = '2020-05-25T14:39:42+00:00'
TIME_NOW = '2020-05-25T17:43:45+03:00'
TIME_START_DELIVERY = '2020-05-25T17:40:45+03:00'
PASSED_FROM_START = 2

TIME_DELIVERED_ETA_FUTURE = '2020-05-25T17:46:42+03:00'
TIME_DELIVERED_ETA_PAST = '2020-05-25T17:43:42+03:00'
LEFT_FOR_DELIVERED = 3


PICKUPED_TIME_OK_CANCEL_1 = '2020-05-25T17:48:45+03:00'
PICKUPED_TIME_OK_CANCEL_2 = '2020-05-25T17:47:45+03:00'
PICKUPED_TIME_OK_CANCEL_3 = '2020-05-25T17:46:45+03:00'
PICKUPED_TIME_OK_CANCEL_4 = '2020-05-25T17:40:45+03:00'


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.now(TIME_NOW)
@pytest.mark.parametrize(
    'has_eta, time_passed', [(True, True), (True, False), (False, False)],
)
async def test_basic_delivery_eta(
        taxi_grocery_orders_tracking,
        pgsql,
        testpoint,
        has_eta,
        time_passed,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
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
            dispatch_courier_name='Vasya',
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

    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )
    assert response.status_code == 200

    if has_eta:
        assert 'delivery_eta_min' in response.json()['grocery_orders'][0]
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


@configs.USE_DYNAMIC_DELIVERY_ETA
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.now(TIME_NOW)
@pytest.mark.parametrize(
    'has_delivered_eta,time_passed',
    [(True, True), (True, False), (False, False)],
)
async def test_dynamic_delivery_eta(
        taxi_grocery_orders_tracking,
        pgsql,
        testpoint,
        has_delivered_eta,
        time_passed,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )
    assert response.status_code == 200

    order_response = response.json()['grocery_orders'][0]
    if has_delivered_eta:
        assert 'delivery_eta_min' in order_response
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
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_no_dynamic_delivery_eta_without_config(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': ([{'id': order.order_id}])},
    )
    assert response.status_code == 200

    order_response = response.json()['grocery_orders'][0]
    assert order_response['delivery_eta_min'] == max(
        delivery_eta, delivery_eta - PASSED_FROM_START,
    )


@pytest.mark.parametrize('send_known_orders', [True, False])
@pytest.mark.parametrize(
    'order_status,dispatch_status_info,response_order_status,payment_status',
    [
        ('checked_out', None, 'created', 'success'),
        ('checked_out', None, 'created', 'failed'),
        ('checked_out', None, 'created', 'unknown'),
        ('reserved', None, 'created', 'unknown'),
        ('reserving', None, 'created', 'unknown'),
        ('assembling', None, 'assembling', 'unknown'),
        ('assembled', None, 'assembled', 'unknown'),
        ('delivering', None, 'assembled', 'success'),
        (
            'delivering',
            models.DispatchStatusInfo(
                dispatch_id='',
                dispatch_status='created',
                dispatch_cargo_status='new',
            ),
            'assembled',
            'unknown',
        ),
        (
            'delivering',
            models.DispatchStatusInfo(
                dispatch_id='',
                dispatch_status='accepted',
                dispatch_cargo_status='new',
            ),
            'assembled',
            'unknown',
        ),
        (
            'delivering',
            models.DispatchStatusInfo(
                dispatch_id='',
                dispatch_status='delivering',
                dispatch_cargo_status='new',
            ),
            'delivering',
            'unknown',
        ),
        (
            'delivering',
            models.DispatchStatusInfo(
                dispatch_id='',
                dispatch_status='closed',
                dispatch_cargo_status='new',
                dispatch_courier_name='SomeCourierName',
            ),
            'closed',
            'unknown',
        ),
        (
            'delivering',
            models.DispatchStatusInfo(
                dispatch_id='',
                dispatch_status='revoked',
                dispatch_cargo_status='new',
                dispatch_courier_name='SomeCourierName',
            ),
            'closed',
            'unknown',
        ),
        (
            'delivering',
            models.DispatchStatusInfo(
                dispatch_id='',
                dispatch_status='failed',
                dispatch_cargo_status='new',
                dispatch_courier_name='SomeCourierName',
            ),
            'closed',
            'unknown',
        ),
        ('pending_cancel', None, 'closed', 'unknown'),
        ('canceled', None, 'closed', 'unknown'),
        ('closed', None, 'closed', 'unknown'),
    ],
)
@pytest.mark.experiments3(
    name='lavka_order_cancel_allowed_statuses',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'statuses': ['created', 'assembling', 'delivering'],
            },
        },
    ],
    default_value={},
    is_config=True,
)
@configs.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_by_order_id(
        taxi_grocery_orders_tracking,
        pgsql,
        load_json,
        testpoint,
        order_status,
        dispatch_status_info,
        response_order_status,
        send_known_orders,
        payment_status,
        cargo,
        grocery_depots,
        grocery_cart,
        eats_orders_tracking,
        now,
):
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
    country_iso2 = 'country_iso2'
    hold_money_status = payment_status if payment_status != 'unknown' else None

    if dispatch_status_info is not None:
        order = models.Order(
            pgsql=pgsql,
            status=order_status,
            dispatch_status_info=dispatch_status_info,
            state=models.OrderState(hold_money_status=hold_money_status),
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
        )
    else:
        order = models.Order(
            pgsql=pgsql,
            status=order_status,
            state=models.OrderState(hold_money_status=hold_money_status),
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

    eats_orders = load_json('eda_orders_tracking_response.json')

    cargo.set_data(cargo_courier_position_error=404)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': (
                [{'id': order.order_id}] if send_known_orders else []
            ),
        },
    )

    if response_order_status == 'delivering':
        expected_actions = [{'type': 'cancel'}, {'type': 'call_courier'}]
    elif response_order_status == 'assembled':
        expected_actions = [{'type': 'edit_address'}]
    elif response_order_status == 'closed':
        expected_actions = []
    else:
        expected_actions = [{'type': 'cancel'}, {'type': 'edit_address'}]

    courier_info = (
        {
            'courier_info': {
                'name': dispatch_status_info.dispatch_courier_first_name,
            },
        }
        if dispatch_status_info is not None
        and dispatch_status_info.dispatch_courier_first_name
        else {'courier_info': {}}
    )

    eta_info = {'delivery_eta_min': DEFAULT_ETA}
    tracking_info_enabled_statuses = set(
        [
            'created',
            'checked_out',
            'reserved',
            'reserving',
            'assembled',
            'assembling',
            'delivering',
        ],
    )
    promise_enabled_statuses = set(
        [
            'created',
            'checked_out',
            'reserved',
            'reserving',
            'assembled',
            'assembling',
        ],
    )
    if response_order_status in tracking_info_enabled_statuses:
        if response_order_status in promise_enabled_statuses:
            eta_info['localized_promise'] = 'Заказ приедет к ~18:35'
            eta_info['promise_max'] = '2020-05-25T15:35:00+00:00'
        # We check proper translation in separate test
        eta_info['tracking_info'] = {'title': 'Ещё примерно 55 минута'}
    else:
        eta_info['tracking_info'] = {}

    expected_grocery_orders = []
    if order_status not in ('canceled', 'closed') or send_known_orders:
        resolution_response = (
            {'resolution': 'succeeded'}
            if response_order_status == 'closed'
            else {}
        )
        expected_grocery_orders = (
            []
            if response_order_status == 'closed' and not send_known_orders
            else [
                {
                    'id': order.order_id,
                    'short_order_id': order.short_order_id,
                    'delivery_type': 'courier',
                    'status': response_order_status,
                    'status_updated': TIME_START_ORDER,
                    'actions': expected_actions,
                    'payment_status': payment_status,
                    'cart_id': order.cart_id,
                    'location': order.location_as_point(),
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
                        'flat': order_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'country_iso2': country_iso2,
                    },
                    **courier_info,
                    **resolution_response,
                    **eta_info,
                },
            ]
        )

    assert response.status_code == 200
    assert response.json() == {
        'grocery_orders': expected_grocery_orders,
        'eats_orders': [eats_orders['payload']['trackedOrders'][0]],
    }


@pytest.mark.parametrize(
    'order_status, desired_order_status',
    [
        ('assembling', 'canceled'),
        ('delivering', 'canceled'),
        ('assembling', 'closed'),
        ('assembling', None),
    ],
)
@configs.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_desired_status(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_cart,
        order_status,
        desired_order_status,
        cargo,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
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


@configs.DISPATCH_GENERAL_CONFIG
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
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_cancel_action(
        taxi_grocery_orders_tracking,
        pgsql,
        cargo,
        grocery_depots,
        grocery_cart,
        pickuped_ts,
        has_cancel,
        eats_orders_tracking,
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

    cargo.set_data(cargo_courier_position_error=404)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    order_response = response.json()['grocery_orders'][0]

    if has_cancel:
        assert {'type': 'cancel'} in order_response['actions']
    else:
        assert {'type': 'cancel'} not in order_response['actions']


@pytest.mark.experiments3(
    name='grocery_tracking_payment_errors_enabled',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.parametrize(
    'error_code, error_title, error_subtitle',
    [
        (
            'some_code',
            COMMON_MONEY_ERROR_TEXT_TITLE,
            COMMON_MONEY_ERROR_TEXT_SUB_TITLE,
        ),
        (
            'not_enough_funds',
            NO_MONEY_ERROR_TEXT_TITLE,
            NO_MONEY_ERROR_TEXT_SUB_TITLE,
        ),
    ],
)
async def test_payment_error_text(
        taxi_grocery_orders_tracking,
        pgsql,
        cargo,
        grocery_depots,
        grocery_cart,
        eats_orders_tracking,
        error_code,
        error_title,
        error_subtitle,
):
    order = models.Order(
        pgsql=pgsql,
        status='canceled',
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='',
            dispatch_status='accepted',
            dispatch_cargo_status='performer_found',
            dispatch_courier_name='SomeCourierName',
            dispatch_pickuped_eta_ts=PICKUPED_TIME_OK_CANCEL_1,
        ),
        cancel_reason_type='payment_failed',
        cancel_reason_meta={'error_code': error_code},
    )

    grocery_cart.add_cart(cart_id=order.cart_id)

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, location=DEPOT_LOCATION,
    )

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    order_response = response.json()['grocery_orders'][0]

    assert order_response['tracking_info'] == {
        'title': error_title,
        'subtitle': error_subtitle,
    }


def compare_state_response(resp, ethalon):
    resp['grocery_orders'].sort(key=lambda kv: kv['id'])
    ethalon['grocery_orders'].sort(key=lambda kv: kv['id'])
    assert resp == ethalon


@configs.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_by_order_ids(
        taxi_grocery_orders_tracking,
        pgsql,
        load_json,
        testpoint,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
        now,
):
    order_statuses = [
        {'init': 'assembling', 'response': 'assembling'},
        {'init': 'reserved', 'response': 'created'},
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
    place_id = 'place_id'
    country_iso2 = 'country_iso2'
    order_left_at_door = True
    order_meet_outside = True
    order_no_door_call = True

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

    eats_orders = load_json('eda_orders_tracking_response.json')

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': [
                {'id': order_1.order_id},
                {'id': order_2.order_id},
            ],
        },
    )

    eta_info_first = {}
    eta_info_second = {}
    tracking_info_enabled_statuses = set(
        [
            'created',
            'checked_out',
            'reserved',
            'reserving',
            'assembled',
            'assembling',
            'delivering',
        ],
    )
    if order_statuses[0]['response'] in tracking_info_enabled_statuses:
        eta_info_first = {
            'localized_promise': 'Заказ приедет к ~18:35',
            'promise_max': '2020-05-25T15:35:00+00:00',
            'delivery_eta_min': DEFAULT_ETA,
        }
        # We check proper translation in separate test
        tracking_info = {'title': 'Ещё примерно 55 минута'}
        eta_info_first['tracking_info'] = tracking_info

    if order_statuses[1]['response'] in tracking_info_enabled_statuses:
        eta_info_second = {
            'localized_promise': 'Заказ приедет к ~18:35',
            'promise_max': '2020-05-25T15:35:00+00:00',
            'delivery_eta_min': DEFAULT_ETA,
        }
        # We check proper translation in separate test
        tracking_info = {'title': 'Ещё примерно 55 минута'}
        eta_info_second['tracking_info'] = tracking_info

    assert response.status_code == 200
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
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info_first,
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
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info_second,
                },
            ],
            'eats_orders': [eats_orders['payload']['trackedOrders'][0]],
        },
    )


@pytest.mark.parametrize(
    'first_status,second_status,result_is_second',
    [
        ('delivering', 'closed', False),
        ('delivering', 'canceled', False),
        ('closed', 'delivering', True),
        ('canceled', 'delivering', True),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_select_not_closed(
        taxi_grocery_orders_tracking,
        pgsql,
        first_status,
        second_status,
        result_is_second,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': []},
    )

    assert response.status_code == 200
    order_id = order_2.order_id if result_is_second else order_1.order_id

    assert len(response.json()['grocery_orders']) == 1
    assert len(response.json()['eats_orders']) == 1
    order = response.json()['grocery_orders'][0]
    assert order['id'] == order_id


@pytest.mark.config(
    GROCERY_ORDERS_NEW_SERVICE=True,
    GROCERY_ORDERS_ENABLE_PERFORMER_FOUND_STATUS=True,
)
@configs.EDIT_ADDRESS
@pytest.mark.now(TIME_START_ORDER)
async def test_select_all_orders_by_session(
        taxi_grocery_orders_tracking,
        pgsql,
        load_json,
        testpoint,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
        now,
):
    order_statuses = [
        {'init': 'delivering', 'response': 'assembled'},
        {'init': 'checked_out', 'response': 'created'},
        {'init': 'delivering', 'response': 'performer_found'},
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
    place_id = 'place_id'
    country_iso2 = 'country_iso2'
    order_left_at_door = True
    order_meet_outside = True
    order_no_door_call = True

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
    )
    order_3 = models.Order(
        pgsql=pgsql,
        status=order_statuses[2]['init'],
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='',
            dispatch_status='accepted',
            dispatch_cargo_status='performer_found',
            dispatch_courier_first_name='SomeCourierName',
        ),
        cart_id=f'{CART_ID_PREFIX}03',
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

    eats_orders = load_json('eda_orders_tracking_response.json')

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': []},
    )

    tracking_info = {'title': 'Ещё примерно 55 минута'}
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
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                    'tracking_info': tracking_info,
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
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                    'tracking_info': tracking_info,
                },
                {
                    'id': order_3.order_id,
                    'short_order_id': order_3.short_order_id,
                    'delivery_type': 'courier',
                    'status': order_statuses[2]['response'],
                    'status_updated': TIME_START_ORDER,
                    'payment_status': 'unknown',
                    'courier_info': {
                        'name': 'SomeCourierName',
                        'position': {'lat': 35.0, 'lon': 55.0},
                    },
                    'actions': [],
                    'cart_id': order_3.cart_id,
                    'location': order_3.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
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
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                    'tracking_info': tracking_info,
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
@configs.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_orders_by_bound_sessions(
        taxi_grocery_orders_tracking,
        pgsql,
        testpoint,
        eats_orders_tracking,
        session_in_pg,
        yandex_uid_in_pg,
        request_bound_sessions,
        request_yandex_uid,
        grocery_depots,
        grocery_cart,
        cargo,
):
    eats_orders_tracking.set_tracking_response(EMPTY_ORDERS_TRACKING)
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers_bounds,
        json={'known_orders': []},
    )

    eta_info = {
        'localized_promise': 'Заказ приедет к ~18:35',
        'promise_max': '2020-05-25T15:35:00+00:00',
        'delivery_eta_min': DEFAULT_ETA,
    }
    # We check proper translation in separate test
    tracking_info = {'title': 'Ещё примерно 55 минута'}
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
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
                    'need_track_payment': False,
                    'tracking_game_enabled': False,
                    **eta_info,
                },
            ],
            'eats_orders': [],
        }

    assert eats_orders_tracking.times_tracking_called() == 1


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
@configs.EDIT_ADDRESS
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.now(TIME_START_ORDER)
async def test_select_orders_not_closed_by_bound_sessions(
        taxi_grocery_orders_tracking,
        pgsql,
        testpoint,
        eats_orders_tracking,
        init_status,
        times_tracking_called,
        response_status,
        cancel_reason_type,
        resolution,
        grocery_depots,
        grocery_cart,
        cargo,
):
    eats_orders_tracking.set_tracking_response(EMPTY_ORDERS_TRACKING)

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
    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
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
        tracking_info = {'title': 'Ещё примерно 55 минута'}
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
                    'actions': [{'type': 'cancel'}, {'type': 'edit_address'}],
                    'courier_info': {},
                    'cart_id': order.cart_id,
                    'location': order.location_as_point(),
                    'depot_location': DEPOT_LOCATION,
                    'address': {
                        'country': order_country,
                        'city': order_city,
                        'street': order_street,
                        'house': order_house,
                        'entrance': order_entrance,
                        'floor': order_floor,
                        'flat': order_flat,
                        'doorcode': order_doorcode,
                        'left_at_door': order_left_at_door,
                        'meet_outside': order_meet_outside,
                        'no_door_call': order_no_door_call,
                        'place_id': place_id,
                        'country_iso2': country_iso2,
                    },
                    'client_price_template': '1000 $SIGN$$CURRENCY$',
                    'currency': 'RUB',
                    'currency_sign': '₽',
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

    assert (
        eats_orders_tracking.times_tracking_called() == times_tracking_called
    )


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
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_courier_position(
        taxi_grocery_orders_tracking,
        pgsql,
        init_status,
        response_status,
        cargo_error_code,
        has_dispatch_info,
        cargo_times_called,
        has_position,
        cargo,
        grocery_depots,
        grocery_cart,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
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
    ],
)
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_rover_open_hatch(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_cart,
        init_status,
        dispatch_status,
        dispatch_cargo_status,
        transport_type,
        result_status,
        has_open_action,
        cargo,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
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
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_depot_info(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_cart,
        delivery_type,
        address,
        directions,
        short_address,
        cargo,
        eats_orders_tracking,
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

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
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


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_just_created_order(
        pgsql,
        taxi_grocery_orders_tracking,
        grocery_cart,
        grocery_depots,
        eats_orders_tracking,
):

    # Fill in depot caches etc
    # await taxi_grocery_orders_tracking.tests_control(invalidate_caches=True)
    order = models.Order(
        pgsql=pgsql,
        status='reserving',
        yandex_uid=headers.YANDEX_UID,
        session=headers.DEFAULT_HEADERS['X-YaTaxi-Session'],
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS},
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
        session=headers.DEFAULT_HEADERS['X-YaTaxi-Session'],
        created=NOW_FOR_CACHE,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers={**headers.DEFAULT_HEADERS},
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


class TrackingInfoContext:
    tanker_keys = None
    arg_names_array = None

    def __init__(self, tanker_keys=None, arg_names=None):
        self.tanker_keys = tanker_keys if tanker_keys is not None else []
        self.arg_names_array = arg_names if arg_names is not None else []


@NOW
@configs.FORMATTER_CONFIGS
@configs.TRANSLATIONS_MARK
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.config(GROCERY_ORDERS_ENABLE_PERFORMER_FOUND_STATUS=True)
@pytest.mark.config(
    GROCERY_ORDERS_ROVER_STATUS_READY_FOR_OPEN='delivery_arrived',
)
@pytest.mark.experiments3(filename='tracking_info_titles.json')
@pytest.mark.experiments3(filename='tracking_info_titles_multi.json')
@pytest.mark.parametrize(
    'order_status,dispatch_status,dispatch_cargo_status,'
    'transport_type,matching_clause_alias,grocery_order_status,order_duration,'
    'timeslot',
    [
        (
            'draft',
            'created',
            'new',
            'car',
            'remaining_time_clause',
            'created',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'checked_out',
            'created',
            'new',
            'car',
            'remaining_time_clause',
            'created',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'reserving',
            'created',
            'new',
            'car',
            'remaining_time_clause',
            'created',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'reserved',
            'created',
            'new',
            'car',
            'remaining_time_clause',
            'created',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'assembling',
            'created',
            'new',
            'car',
            'remaining_time_clause',
            'assembling',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'assembled',
            'created',
            'new',
            'car',
            'assembled_clause',
            'assembled',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'created',
            'accepted',
            'car',
            'assembled_clause',
            'assembled',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'accepted',
            'performer_lookup',
            'car',
            'assembled_clause',
            'assembled',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'accepted',
            'performer_found',
            'car',
            'performer_found_clause',
            'performer_found',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'delivering',
            'pickuped',
            'car',
            'remaining_time_clause',
            'delivering',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'delivering',
            'pickuped',
            'rover',
            'remaining_time_clause',
            'delivering',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'delivering',
            'delivery_arrived',
            'car',
            'courier_arrived_to_client_clause',
            'delivery_arrived',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'delivering',
            'delivering',
            'delivery_arrived',
            'rover',
            'courier_arrived_to_client_clause',
            'delivery_arrived',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'closed',
            'closed',
            'delivered',
            'car',
            'order_closed_clause',
            'closed',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'closed',
            'closed',
            'delivered_finish',
            'car',
            'order_closed_clause',
            'closed',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'pending_cancel',
            'revoked',
            'cancelled',
            'car',
            'order_closed_clause',
            'closed',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'canceled',
            'revoked',
            'cancelled',
            'car',
            'order_closed_clause',
            'closed',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'canceled',
            'failed',
            'failed',
            'car',
            'order_closed_clause',
            'closed',
            DEFAULT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
        (
            'reserved',
            'created',
            'new',
            'car',
            'long_slot_order_created',
            'created',
            DEFAULT_ORDER_DURATION,
            SUPER_TIMESLOT,
        ),
        (
            'closed',
            'closed',
            'delivered',
            'car',
            'order_closed_with_early_delivery_clause',
            'closed',
            SHORT_ORDER_DURATION,
            DEFAULT_TIMESLOT,
        ),
    ],
)
async def test_tracking_info(
        taxi_grocery_orders_tracking,
        grocery_depots,
        grocery_cart,
        taxi_config,
        cargo,
        eats_orders_tracking,
        now,
        experiments3,
        testpoint,
        pgsql,
        order_status,
        dispatch_status,
        dispatch_cargo_status,
        transport_type,
        matching_clause_alias,
        grocery_order_status,
        order_duration,
        timeslot,
):
    taxi_config.set(
        GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={'__default__': 'ru'},
    )
    dispatch_id = consts.DEFAULT_DISPATCH_ID
    cart_id = cart.DEFAULT_CART_ID
    depot_id = models.DEFAULT_DEPOT_ID

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=dispatch_id,
        dispatch_status=dispatch_status,
        dispatch_cargo_status=dispatch_cargo_status,
        dispatch_transport_type=transport_type,
    )
    grocery_cart.set_cart_data(cart_id=cart_id)
    grocery_depots.add_depot(legacy_depot_id=depot_id, location=[13, 37])
    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        dispatch_status_info=dispatch_status_info,
        cart_id=cart_id,
        depot_id=depot_id,
        created=now,
        status_updated=now + datetime.timedelta(minutes=order_duration),
        timeslot_start=None if timeslot is None else timeslot['start'],
        timeslot_end=None if timeslot is None else timeslot['end'],
        timeslot_request_kind=None if timeslot is None else 'wide_slot',
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_orders_tracking_info',
    )

    context = TrackingInfoContext()

    @testpoint('tracking_info_args')
    def _testpoint_tracking_info_args(param):
        context.tanker_keys.append(param['tanker_key'])
        context.arg_names_array.append(param['arg_names'])

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )
    assert response.status_code == 200

    exp3_match = (await exp3_recorder.get_match_tries(ensure_ntries=1))[0]
    assert exp3_match.clause_alias == matching_clause_alias
    if exp3_match.clause_alias == 'remaining_time_clause':
        assert _testpoint_tracking_info_args.times_called == 3
        assert context.tanker_keys == [
            'order_remaining_time',
            'multiorder_catalog_title',
            'multiorder_catalog_eta',
        ]
        assert context.arg_names_array == [['minutes'], ['price'], ['minutes']]
    elif exp3_match.clause_alias == 'assembled_clause':
        assert _testpoint_tracking_info_args.times_called == 3
        assert context.tanker_keys == [
            'title_order_assembled',
            'multiorder_catalog_title',
            'multiorder_catalog_eta',
        ]
        assert context.arg_names_array == [[], ['price'], ['minutes']]
    elif exp3_match.clause_alias == 'performer_found_clause':
        assert _testpoint_tracking_info_args.times_called == 3
        assert context.tanker_keys == [
            'title_performer_found',
            'multiorder_catalog_title',
            'multiorder_catalog_eta',
        ]
        assert context.arg_names_array == [[], ['price'], ['minutes']]
    elif exp3_match.clause_alias == 'courier_arrived_to_client_clause':
        assert _testpoint_tracking_info_args.times_called == 4
        assert context.tanker_keys == [
            'courier_arrived_to_client_title',
            'courier_arrived_to_client_subtitle',
            'multiorder_catalog_title',
            'multiorder_catalog_eta',
        ]
        assert context.arg_names_array == [[], [], ['price'], ['minutes']]
    elif exp3_match.clause_alias == 'order_closed_with_early_delivery_clause':
        assert _testpoint_tracking_info_args.times_called == 2
        assert context.tanker_keys == [
            'order_early_delivery_title',
            'order_early_delivery_subtitle',
        ]
        assert context.arg_names_array == [['early_delivery_time_delta'], []]
    elif exp3_match.clause_alias == 'long_slot_order_created':
        assert _testpoint_tracking_info_args.times_called == 5
        assert context.tanker_keys == [
            'long_slot_created_title',
            'long_slot_created_subtitle',
            'multiorder_long_slot_title',
            'multiorder_long_slot_subtitle',
            'multiorder_long_slot_eta',
        ]
        assert context.arg_names_array == [
            [],
            ['slot_end', 'slot_start'],
            [],
            [],
            [],
        ]
    elif exp3_match.clause_alias == 'order_closed_clause':
        assert _testpoint_tracking_info_args.times_called == 0
    else:
        assert False, exp3_match.clause_alias

    grocery_orders = response.json()['grocery_orders']
    assert len(grocery_orders) == 1

    assert grocery_orders[0]['status'] == grocery_order_status


@NOW
@configs.FORMATTER_CONFIGS
@configs.TRANSLATIONS_MARK
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.experiments3(filename='tracking_info_titles.json')
@pytest.mark.experiments3(filename='tracking_info_titles_multi.json')
@pytest.mark.parametrize('dispatch_in_batch', [None, True, False])
@pytest.mark.parametrize('batch_order_num', [None, 0, 1])
async def test_tracking_info_batch(
        taxi_grocery_orders_tracking,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
        now,
        experiments3,
        testpoint,
        pgsql,
        dispatch_in_batch,
        batch_order_num,
):
    order_status = 'delivering'
    dispatch_status = 'delivering'
    dispatch_cargo_status = 'pickuped'
    transport_type = 'car'
    grocery_order_status = 'delivering'

    dispatch_id = consts.DEFAULT_DISPATCH_ID
    cart_id = cart.DEFAULT_CART_ID
    depot_id = models.DEFAULT_DEPOT_ID

    dispatch_status_meta = {
        'cargo_dispatch': {
            'dispatch_in_batch': dispatch_in_batch,
            'batch_order_num': batch_order_num,
        },
    }

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=dispatch_id,
        dispatch_status=dispatch_status,
        dispatch_cargo_status=dispatch_cargo_status,
        dispatch_transport_type=transport_type,
        dispatch_status_meta=dispatch_status_meta,
    )
    grocery_cart.set_cart_data(cart_id=cart_id)
    grocery_depots.add_depot(legacy_depot_id=depot_id, location=[13, 37])
    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        dispatch_status_info=dispatch_status_info,
        cart_id=cart_id,
        depot_id=depot_id,
        created=now,
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_orders_tracking_info',
    )

    class Context:
        tanker_keys = []
        arg_names_array = []

    context = Context()

    @testpoint('tracking_info_args')
    def _testpoint_tracking_info_args(param):
        context.tanker_keys.append(param['tanker_key'])
        context.arg_names_array.append(param['arg_names'])

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )
    assert response.status_code == 200

    grocery_orders = response.json()['grocery_orders']
    assert len(grocery_orders) == 1

    assert grocery_orders[0]['status'] == grocery_order_status

    assert _testpoint_tracking_info_args.times_called == 3
    exp3_match = (await exp3_recorder.get_match_tries(ensure_ntries=1))[0]
    if dispatch_in_batch is True and batch_order_num and batch_order_num > 0:
        assert exp3_match.clause_alias == 'delivering_enqueued_clause'
        assert context.tanker_keys == [
            'title_delivering_enqueued',
            'multiorder_catalog_title',
            'multiorder_catalog_eta',
        ]
        assert context.arg_names_array == [[], ['price'], ['minutes']]
    else:
        assert exp3_match.clause_alias == 'remaining_time_clause'
        assert context.tanker_keys == [
            'order_remaining_time',
            'multiorder_catalog_title',
            'multiorder_catalog_eta',
        ]
        assert context.arg_names_array == [['minutes'], ['price'], ['minutes']]


@NOW
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.config(GROCERY_ORDERS_DEFAULT_DEVICE_PIXEL_RATIO=2.0)
@pytest.mark.parametrize(
    ['device_pixel_ratio', 'image_suffix', 'enabled'],
    [
        (None, '1.5', True),
        (0.9, '1.0', True),
        (1.0, '1.0', True),
        (1.1, '1.0', True),
        (1.4, '1.5', True),
        (1.5, '1.5', True),
        (1.6, '1.5', True),
        (1.0, '1.0', False),
    ],
)
async def test_tracking_info_images(
        taxi_grocery_orders_tracking,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
        now,
        testpoint,
        pgsql,
        experiments3,
        load_json,
        device_pixel_ratio,
        image_suffix,
        enabled,
):
    order_status = 'delivering'
    dispatch_status = 'delivering'
    dispatch_cargo_status = 'pickuped'

    dispatch_id = consts.DEFAULT_DISPATCH_ID
    cart_id = cart.DEFAULT_CART_ID
    depot_id = models.DEFAULT_DEPOT_ID

    exp3 = load_json('tracking_info_images.json')
    exp3['configs'][0]['default_value']['enabled'] = enabled
    experiments3.add_experiments_json(exp3)

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=dispatch_id,
        dispatch_status=dispatch_status,
        dispatch_cargo_status=dispatch_cargo_status,
    )
    grocery_cart.set_cart_data(cart_id=cart_id)
    grocery_depots.add_depot(legacy_depot_id=depot_id, location=[13, 37])
    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        dispatch_status_info=dispatch_status_info,
        cart_id=cart_id,
        depot_id=depot_id,
        created=now,
    )

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={
            'known_orders': [{'id': order.order_id}],
            'device_pixel_ratio': device_pixel_ratio,
        },
    )
    assert response.status_code == 200

    grocery_orders = response.json()['grocery_orders']
    assert len(grocery_orders) == 1

    tracking_info = grocery_orders[0]['tracking_info']
    if enabled:
        assert (
            tracking_info['courier_image'] == f'courier_image@{image_suffix}'
        )
        assert (
            tracking_info['grocery_image'] == f'grocery_image@{image_suffix}'
        )
        assert (
            tracking_info['destination_image']
            == f'destination_image@{image_suffix}'
        )
    else:
        assert 'courier_image' not in tracking_info
        assert 'grocery_image' not in tracking_info
        assert 'destination_image' not in tracking_info


@NOW
@configs.FORMATTER_CONFIGS
@configs.TRANSLATIONS_MARK
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.translations(
    grocery_orders={
        f'title_tpl_arg_{tpl_arg}': {'ru': f'%({tpl_arg})s'}
        for tpl_arg in LOCALIZATION_TPL_ARGS
    },
)
@pytest.mark.parametrize(
    'tpl_arg,actual_value',
    zip(LOCALIZATION_TPL_ARGS, LOCALIZATION_TPL_PARAMS),
)
async def test_tracking_info_tpl_args(
        taxi_grocery_orders_tracking,
        grocery_depots,
        grocery_cart,
        cargo,
        eats_orders_tracking,
        pgsql,
        now,
        experiments3,
        testpoint,
        tpl_arg,
        actual_value,
):
    dispatch_id = consts.DEFAULT_DISPATCH_ID
    cart_id = cart.DEFAULT_CART_ID
    depot_id = models.DEFAULT_DEPOT_ID

    dispatch_status_meta = {
        'cargo_dispatch': {
            'batch_order_num': BATCH_ORDER_NUM,
            'dispatch_in_batch': True,
        },
    }
    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=dispatch_id,
        dispatch_status='delivering',
        dispatch_cargo_status='pickuped',
        dispatch_status_meta=dispatch_status_meta,
        dispatch_courier_first_name=COURIER_SHORT_NAME,
    )
    grocery_cart.set_cart_data(cart_id=cart_id)
    grocery_depots.add_depot(legacy_depot_id=depot_id, location=[13, 37])
    order = models.Order(
        short_order_id=SHORT_ORDER_ID,
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=dispatch_status_info,
        cart_id=cart_id,
        depot_id=depot_id,
        created=now,
    )

    @testpoint('set_order_created')
    def _set_order_created(order_id):
        assert order_id == order.order_id
        return '2020-05-25T17:43:45+03:00'

    experiments3.add_config(
        name='grocery_orders_tracking_info',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'tracking_info': {'title': f'title_tpl_arg_{tpl_arg}'},
                },
            },
        ],
    )
    experiments3.add_config(
        name='grocery_orders_tracking_multiorder',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'multiorder_info': {}},
            },
        ],
    )
    await taxi_grocery_orders_tracking.invalidate_caches(clean_update=False)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )
    assert response.status_code == 200

    grocery_orders = response.json()['grocery_orders']
    assert len(grocery_orders) == 1

    title = grocery_orders[0]['tracking_info']['title']
    assert title == str(actual_value)


def _stringtime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')


def _compare_to_old_tracking(old_json, new_json):
    if new_json is None:
        assert old_json is None
        return
    if (
            'multiorder_catalog_eta' in new_json
            and 'multiorder_catalog_title' in new_json
    ):
        del new_json['multiorder_catalog_eta']
        del new_json['multiorder_catalog_title']
    elif 'multiorder_catalog_subtitle' in new_json:
        del new_json['multiorder_catalog_subtitle']
    assert old_json == new_json


@configs.PAYMENTS_CLIENT_MAPPINGS_EXP
@configs.TRACKING_PAYMENTS_ERROR
@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
@pytest.mark.parametrize(
    'payment_method_type, country_iso3, translation',
    [
        ('card', 'RUS', 'rus card mapped tanker key translation'),
        ('card', 'ISR', 'mapped tanker key translation'),
        ('applepay', 'RUS', 'mapped tanker key translation'),
    ],
)
async def test_payments_client_mappings(
        taxi_grocery_orders_tracking,
        pgsql,
        cargo,
        grocery_depots,
        grocery_cart,
        eats_orders_tracking,
        payment_method_type,
        country_iso3,
        translation,
):
    order = models.Order(
        pgsql=pgsql,
        status='canceled',
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id='',
            dispatch_status='accepted',
            dispatch_cargo_status='performer_found',
            dispatch_courier_name='SomeCourierName',
            dispatch_pickuped_eta_ts=PICKUPED_TIME_OK_CANCEL_1,
        ),
        cancel_reason_type='payment_failed',
        cancel_reason_meta={'error_code': 'not_enough_funds'},
    )

    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        payment_method={'type': payment_method_type, 'id': '123'},
        cart_id=order.cart_id,
    )

    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id,
        location=DEPOT_LOCATION,
        country_iso3=country_iso3,
    )

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )

    order_response = response.json()['grocery_orders'][0]

    assert order_response['tracking_info'] == {
        'title': f'title {translation}',
        'subtitle': f'subtitle {translation}',
    }


@pytest.mark.config(GROCERY_ORDERS_NEW_SERVICE=True)
async def test_israel_courier_forced_pedestrian(
        taxi_grocery_orders_tracking,
        eats_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_cart,
        cargo,
):
    dispatch_info = models.DispatchStatusInfo(
        dispatch_id='some_dispatch_id',
        dispatch_status='delivering',
        dispatch_cargo_status='performer_found',
        dispatch_transport_type='car',
        dispatch_car_number='777',
        dispatch_car_model='mercedes',
        dispatch_car_color='blue',
        dispatch_car_color_hex='#322',
    )
    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        cart_id=CART_ID,
        created=NOW_FOR_CACHE,
        dispatch_status_info=dispatch_info,
    )
    grocery_cart.add_cart(cart_id=order.cart_id)
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3='ISR',
    )

    eats_orders_tracking.set_tracking_error_code(500)

    response = await taxi_grocery_orders_tracking.post(
        '/lavka/v1/orders-tracking/v1/state',
        headers=headers.DEFAULT_HEADERS,
        json={'known_orders': [{'id': order.order_id}]},
    )
    assert response.status_code == 200
    assert len(response.json()['grocery_orders']) == 1

    order_found = response.json()['grocery_orders'][0]

    assert order_found['id'] == order.order_id

    assert order_found['courier_info']['transport_type'] == 'pedestrian'
    assert 'car_number' not in order_found['courier_info']
