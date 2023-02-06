import copy
import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks import grocery_cart as mock_grocery_cart
# pylint: enable=import-error
import pytest

from . import models

CART_ID = 'a49609bd-741d-410e-9f04-476f46ad43c7'
LOCATION_IN_RUSSIA = [37, 55]
PLACE_ID = 'yamaps://12345'
REGION_ID = 213
DEPOT_ID = '301924'
YANDEX_UID = '123378'
PERSONAL_PHONE_ID = '37281ejwxdewmo'
LOCALE = 'ru'
URI = (
    'ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.00'
    '1&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%'
    'D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%92%D0%B0%D1%80%D1'
    '%88%D0%B0%D0%B2%D1%81%D0%BA%D0%BE%D0%B5%20%D1%88%D'
    '0%BE%D1%81%D1%81%D0%B5%2C%20141%D0%90%D0%BA1%2C%20%D0%BF'
    '%D0%BE%D0%B4%D1%8A%D0%B5%D0%B7%D0%B4%201%20%7B3457'
    '696635%7D'
)
IDEMPOTENCY_TOKEN = 's6372e231'
MARKET_BATCHING_TAGS = ['market_batching']
FLAT = '1337'
COMMENT = 'deliver fast'
DOORCODE = '42'
ENTRANCE = '3333'
FLOOR = '13'

POSITION = {
    'location': LOCATION_IN_RUSSIA,
    'place_id': PLACE_ID,
    'flat': FLAT,
    'comment': COMMENT,
    'doorcode': DOORCODE,
    'entrance': ENTRANCE,
    'floor': FLOOR,
}

CART_POSITION = {'location': LOCATION_IN_RUSSIA, 'uri': PLACE_ID}

MAKE_REQUEST = {
    'position': POSITION,
    'yandex_uid': YANDEX_UID,
    'personal_phone_id': PERSONAL_PHONE_ID,
    'locale': LOCALE,
    'items': [{'id': 'item_1:st-pa', 'quantity': '1'}],
}

HANDLER = pytest.mark.parametrize(
    'handler', ['internal/v1/orders/v1/make', 'admin/orders/v1/make'],
)

DEFAULT_ORDER_TIMEOUT_MINUTES = 100
NOW = '2020-03-13T07:19:00+00:00'

CART_HANDLER = pytest.mark.parametrize(
    'cart_handler',
    [mock_grocery_cart.Handler.create, mock_grocery_cart.Handler.checkout],
)


@HANDLER
@CART_HANDLER
@pytest.mark.config(GROCERY_ORDERS_ALLOW_TO_USE_POSTPONED_FLOW=True)
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'yandex_uid, grocery_flow, use_wide_timeslot',
    [
        (YANDEX_UID, 'tristero_flow_v2', False),
        (None, 'tristero_no_auth_flow_v1', False),
        (YANDEX_UID, 'postponed_order_no_payment_flow_v1', True),
    ],
)
async def test_basic_make(
        taxi_grocery_orders,
        grocery_depots,
        grocery_cart,
        pgsql,
        processing,
        handler,
        yandex_uid,
        grocery_flow,
        cart_handler,
        use_wide_timeslot,
):
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID,
        region_id=REGION_ID,
        location=LOCATION_IN_RUSSIA,
    )

    items = [
        {'id': 'item_1:st-pa', 'quantity': '1'},
        {'id': 'item_2:st-pa', 'quantity': '1'},
    ]

    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    body = copy.deepcopy(MAKE_REQUEST)
    body['items'] = items
    body['yandex_uid'] = yandex_uid

    if use_wide_timeslot:
        body['timeslot'] = {'start': timeslot_start, 'end': timeslot_end}
        body['request_kind'] = timeslot_request_kind

    fields_to_check = {
        'additional_data': {
            'device_coordinates': {'location': LOCATION_IN_RUSSIA, 'uri': URI},
            'city': 'Moscow',
            'street': 'Varshavskoye Highway',
            'house': '141Ак1',
            'comment': COMMENT,
            'flat': FLAT,
            'doorcode': DOORCODE,
            'entrance': ENTRANCE,
            'floor': FLOOR,
        },
    }

    if cart_handler == mock_grocery_cart.Handler.create:
        fields_to_check['items'] = [
            {'product_id': item['id'], 'quantity': item['quantity']}
            for item in items
        ]
        fields_to_check['position'] = CART_POSITION
        fields_to_check['yandex_uid'] = yandex_uid
        fields_to_check['locale'] = LOCALE

    grocery_cart.check_request(
        fields_to_check=fields_to_check,
        headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
        handler=cart_handler,
    )

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == 200
    assert 'order_id' in response.json()

    order_id = response.json()['order_id']

    assert grocery_cart.create_times_called() == 1
    assert grocery_cart.checkout_times_called() == 1

    order = models.Order(pgsql=pgsql, order_id=order_id, insert_in_pg=False)
    order.update()

    assert order.region_id == REGION_ID
    assert order.cart_id == CART_ID
    assert order.place_id == PLACE_ID
    assert order.yandex_uid == yandex_uid
    assert order.personal_phone_id == PERSONAL_PHONE_ID
    assert order.grocery_flow_version == grocery_flow
    if use_wide_timeslot:
        assert order.wms_logistic_tags == [
            *MARKET_BATCHING_TAGS,
            timeslot_request_kind,
        ]
    else:
        assert order.wms_logistic_tags == [*MARKET_BATCHING_TAGS]

    assert order.offer_id == mock_grocery_cart.DEFAULT_OFFER_ID

    if use_wide_timeslot:
        assert (
            order.timeslot_start - _stringtime(timeslot_start)
        ).total_seconds() == 0
        assert (
            order.timeslot_end - _stringtime(timeslot_end)
        ).total_seconds() == 0
        assert order.timeslot_request_kind == timeslot_request_kind

    assert order.is_dispatch_request_started is None

    events = list(processing.events(scope='grocery', queue='processing'))

    assert len(events) == 2
    assert events[0].payload['order_id'] == order.order_id
    assert events[0].payload['reason'] == 'created'
    if use_wide_timeslot:
        assert (
            events[0].payload['order_info']['timeslot_request_kind']
            == timeslot_request_kind
        )
        assert (
            events[0].payload['order_info']['market_slot_begin']
            == timeslot_start
        )
        assert (
            events[0].payload['order_info']['market_slot_end'] == timeslot_end
        )

    assert events[1].payload['reason'] == 'cancel'
    assert events[1].payload['cancel_reason_message'] == 'Order timed out'
    if use_wide_timeslot:
        assert (
            _stringtime(events[1].due) - _stringtime(timeslot_end)
        ).total_seconds() == (60 * DEFAULT_ORDER_TIMEOUT_MINUTES)
    else:
        assert (
            _stringtime(events[1].due) - _stringtime(NOW)
        ).total_seconds() == (60 * DEFAULT_ORDER_TIMEOUT_MINUTES)

    # Check idempotency

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == 200
    assert response.json()['order_id'] == order_id


@HANDLER
@pytest.mark.parametrize(
    'items',
    [
        [
            {'id': 'item_1:st-pa', 'quantity': '1'},
            {'id': 'item_2:st-pa', 'quantity': '2'},
        ],
        [
            {'id': 'item_1', 'quantity': '1'},
            {'id': 'item_2:st-pa', 'quantity': '1'},
        ],
    ],
)
async def test_incorrect_items(taxi_grocery_orders, items, handler):
    body = copy.deepcopy(MAKE_REQUEST)
    body['items'] = items

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == 400


@HANDLER
async def test_empty_personal_phone_id(taxi_grocery_orders, handler):
    body = copy.deepcopy(MAKE_REQUEST)
    body['personal_phone_id'] = ''

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == 400


@HANDLER
@pytest.mark.parametrize('code', [400, 500])
async def test_cart_create_error(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        code,
        handler,
):
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID,
        region_id=REGION_ID,
        location=LOCATION_IN_RUSSIA,
    )

    items = [
        {'id': 'item_1:st-pa', 'quantity': '1'},
        {'id': 'item_2:st-pa', 'quantity': '1'},
    ]

    body = copy.deepcopy(MAKE_REQUEST)
    body['items'] = items

    grocery_cart.check_request(
        fields_to_check={
            'items': [
                {'product_id': item['id'], 'quantity': item['quantity']}
                for item in items
            ],
            'position': CART_POSITION,
            'yandex_uid': YANDEX_UID,
            'locale': LOCALE,
        },
        headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
        handler=mock_grocery_cart.Handler.create,
    )

    grocery_cart.set_create_error(code=code)

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == code
    assert grocery_cart.checkout_times_called() == 0


@HANDLER
@pytest.mark.parametrize('code', [400, 500])
async def test_cart_checkout_error(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        code,
        handler,
):
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID,
        region_id=REGION_ID,
        location=LOCATION_IN_RUSSIA,
    )

    items = [
        {'id': 'item_1:st-pa', 'quantity': '1'},
        {'id': 'item_2:st-pa', 'quantity': '1'},
    ]

    body = copy.deepcopy(MAKE_REQUEST)
    body['items'] = items

    grocery_cart.check_request(
        fields_to_check={
            'items': [
                {'product_id': item['id'], 'quantity': item['quantity']}
                for item in items
            ],
            'position': CART_POSITION,
            'yandex_uid': YANDEX_UID,
            'locale': LOCALE,
        },
        headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
        handler=mock_grocery_cart.Handler.create,
    )

    grocery_cart.set_checkout_error(code=code)

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == 500

    assert grocery_cart.create_times_called() == 1
    assert grocery_cart.checkout_times_called() > 0


@HANDLER
async def test_cart_checkout_error400(
        taxi_grocery_orders,
        grocery_depots,
        grocery_cart,
        pgsql,
        processing,
        handler,
):
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_cart.set_checkout_unavailable_reason(reason='parcel-wrong-depot')
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID,
        region_id=REGION_ID,
        location=LOCATION_IN_RUSSIA,
    )

    items = [
        {'id': 'item_1:st-pa', 'quantity': '1'},
        {'id': 'item_2:st-pa', 'quantity': '1'},
    ]

    body = copy.deepcopy(MAKE_REQUEST)
    body['items'] = items
    body['yandex_uid'] = YANDEX_UID

    grocery_cart.check_request(
        fields_to_check={
            'items': [
                {'product_id': item['id'], 'quantity': item['quantity']}
                for item in items
            ],
            'position': CART_POSITION,
            'yandex_uid': YANDEX_UID,
            'locale': LOCALE,
        },
        headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
        handler=mock_grocery_cart.Handler.create,
    )

    response = await taxi_grocery_orders.post(
        handler, json=body, headers={'X-Idempotency-Token': IDEMPOTENCY_TOKEN},
    )

    assert response.status_code == 400


def _stringtime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')
