import copy
import json
import uuid

import pytest

from . import configs
from . import headers
from . import models

USER_ENTRANCE = 'entrance-123'

DISPATCH_LOCALE = 'ru'

NOW_TIME = '2020-05-25T17:43:45+00:00'
POSTPONE_TIME = '2020-05-25T17:44:45+00:00'

DEFAULT_DISPATCH = {
    'driver_id': 'driver_id_123',
    'courier_name': 'Ivan Ivanov',
    'courier_full_name': 'Ivan Ivanov Ivanovich',
}

POSTAL_CODE = 'postal_god_damn_code'

ORDER_DATA = {
    'personal_phone_id': '1a2a3a',
    'phone': '+79991234567',
    'eats_user_id': '12345',
    'eats_courier_id': 'eats_courier_id_123',
    'balance_client_id': 'balance_client_id:qwe',
    'user_comment': 'Домофон не работает :(',
    'order_place_id': 'order_place_id',
    'order_location': [30.0, 50.0],
    'postal_code': POSTAL_CODE,
    'due_time_point': '2020-05-25T17:43:45+00:00',
    'depot_location': '10.000000,20.000000',
    'depot_country': 'Россия',
    'depot_city': 'Москва',
    'depot_street': 'Парковая',
    'depot_house': '10',
    'depot_place_id': 'place-id',
    'locale': DISPATCH_LOCALE,
    'depot_phone_number': '8(123)123-4545',
    'directions': 'За первой дверью налево и подняться по лестнице.',
    'max_eta': 25,
    'min_eta': 10,
    'delivery_cost': 0,
    'additional_phone_code': '2282',
    'delivery_common_comment': 'delivery_common_comment',
}

CART_ID = '00000000-0000-0000-0000-d98013100500'
OFFER_ID = 'offer-id'
CART_VERSION = 4
LOCATION_IN_RUSSIA = [37, 55]
LOCATION_IN_ISRAEL = [34.865849, 32.054721]
RUSSIAN_PHONE_NUMBER = '+79993537429'
ISRAELIAN_PHONE_NUMBER = '+972542188598'
AUSTRALIAN_PHONE_NUMBER = '+991234561'
PLACE_ID = 'yamaps://12345'
FLOOR = '13'
FLAT = '666'
DOORCODE = '42'
DOORCODE_EXTRA = 'doorcode_extra'
BUILDING_NAME = 'building_name'
DOORBELL_NAME = 'doorbell_name'
LEFT_AT_DOOR = False
MEET_OUTSIDE = True
NO_DOOR_CALL = True
COMMENT = 'comment'
DEPOT_ID = '2809'
ENTRANCE = '3333'
REGION_ID = 102
LOG_TAGS = ['hot', 'n', 'cold']

PROCESSING_FLOW_VERSION = 'grocery_flow_v1'

SUBMIT_BODY = {
    'cart_id': CART_ID,
    'cart_version': CART_VERSION,
    'offer_id': OFFER_ID,
    'position': {
        'location': LOCATION_IN_RUSSIA,
        'place_id': PLACE_ID,
        'floor': FLOOR,
        'flat': FLAT,
        'doorcode': DOORCODE,
        'doorcode_extra': DOORCODE_EXTRA,
        'building_name': BUILDING_NAME,
        'doorbell_name': DOORBELL_NAME,
        'postal_code': POSTAL_CODE,
        'left_at_door': LEFT_AT_DOOR,
        'meet_outside': MEET_OUTSIDE,
        'no_door_call': NO_DOOR_CALL,
        'comment': COMMENT,
        'entrance': ENTRANCE,
    },
    'flow_version': PROCESSING_FLOW_VERSION,
}


def get_new_uuid():
    return str(uuid.uuid4())


@pytest.fixture
def _prepare(
        pgsql,
        grocery_cart,
        grocery_supply,
        grocery_depots,
        grocery_dispatch,
        yamaps_local,
):
    def _do(
            dispatch_id,
            init_status='delivering',
            dispatch_status='idle',
            delivery_zone_type=None,
            transport_type=None,
            courier_service=None,
            init_in_pg=True,
    ):
        order = models.Order(
            pgsql=pgsql,
            status=init_status,
            location=str(tuple(ORDER_DATA['order_location'])),
            personal_phone_id=ORDER_DATA['personal_phone_id'],
            additional_phone_code=ORDER_DATA['additional_phone_code'],
            delivery_common_comment=ORDER_DATA['delivery_common_comment'],
            eats_user_id=ORDER_DATA['eats_user_id'],
            comment=ORDER_DATA['user_comment'],
            locale=ORDER_DATA['locale'],
            place_id=ORDER_DATA['order_place_id'],
            postal_code=ORDER_DATA['postal_code'],
            entrance=USER_ENTRANCE,
            dispatch_flow='grocery_dispatch',
            meet_outside=MEET_OUTSIDE,
            no_door_call=NO_DOOR_CALL,
        )

        if init_in_pg:
            order.upsert(
                dispatch_status_info=models.DispatchStatusInfo(
                    dispatch_id=dispatch_id,
                    dispatch_status='accepted',
                    dispatch_cargo_status='accepted',
                    dispatch_driver_id=DEFAULT_DISPATCH['driver_id'],
                    dispatch_courier_name=DEFAULT_DISPATCH['courier_name'],
                    dispatch_transport_type=transport_type,
                ),
            )

        yamaps_local.set_data(
            country=ORDER_DATA['depot_country'],
            city=ORDER_DATA['depot_city'],
            street=ORDER_DATA['depot_street'],
            house=ORDER_DATA['depot_house'],
            location=ORDER_DATA['depot_location'],
            text_addr='some_string_address',
            place_id=ORDER_DATA['depot_place_id'],
            lang=ORDER_DATA['locale'],
        )

        grocery_cart.set_cart_data(cart_id=order.cart_id)
        grocery_cart.set_order_conditions(
            delivery_cost=ORDER_DATA['delivery_cost'],
            max_eta=ORDER_DATA['max_eta'],
            min_eta=ORDER_DATA['min_eta'],
        )
        grocery_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )
        grocery_cart.set_delivery_type('courier')
        grocery_cart.set_delivery_zone_type(delivery_zone_type)

        cart_items = []

        # Log tags are weirdly implemeted
        grocery_cart.set_logistic_tags(LOG_TAGS)
        for item in grocery_cart.get_items():
            cart_items.append({**item.as_object(), 'item_tags': LOG_TAGS})

        grocery_depots.add_depot(
            legacy_depot_id=order.depot_id,
            location=[
                float(value)
                for value in ORDER_DATA['depot_location'].split(',')
            ],
            address='some_string_address',
            phone_number=ORDER_DATA['depot_phone_number'],
            directions=ORDER_DATA['directions'],
        )

        grocery_dispatch.set_data(
            order_id=order.order_id,
            short_order_id=order.short_order_id,
            depot_id=order.depot_id,
            dispatch_id=dispatch_id,
            status=dispatch_status,
            location=order.location,
            zone_type=delivery_zone_type,
            created_at=order.created,
            due_time_point=ORDER_DATA['due_time_point'],
            max_eta=ORDER_DATA['max_eta'],
            accept_language=ORDER_DATA['locale'],
            eats_profile_id=ORDER_DATA['eats_courier_id'],
            additional_phone_code=ORDER_DATA['additional_phone_code'],
            delivery_common_comment=ORDER_DATA['delivery_common_comment'],
            door_code_extra=SUBMIT_BODY['position']['doorcode_extra'],
            doorbell_name=SUBMIT_BODY['position']['doorbell_name'],
            postal_code=SUBMIT_BODY['position']['postal_code'],
            building_name=SUBMIT_BODY['position']['building_name'],
            leave_under_door=SUBMIT_BODY['position']['left_at_door'],
            meet_outside=SUBMIT_BODY['position']['meet_outside'],
            no_door_call=SUBMIT_BODY['position']['no_door_call'],
        )

        grocery_dispatch.set_data(
            items=cart_items,
            status=dispatch_status,
            dispatch_id=dispatch_id,
            performer_name='Andrey',
            performer_id='123',
            eats_profile_id=ORDER_DATA['eats_courier_id'],
            transport_type=transport_type,
        )

        grocery_supply.check_courier_info(
            courier_id=ORDER_DATA['eats_courier_id'],
        )
        grocery_supply.set_courier_response(
            response={
                'courier_id': ORDER_DATA['eats_courier_id'],
                'transport_type': transport_type,
                'full_name': DEFAULT_DISPATCH['courier_full_name'],
                'billing_client_id': ORDER_DATA['balance_client_id'],
                'courier_service': courier_service,
            },
        )

        return order

    return _do


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
@pytest.mark.parametrize('transport_type', ['rover', 'bicycle'])
async def test_performer_info(
        taxi_grocery_orders, grocery_dispatch, _prepare, transport_type,
):
    dispatch_track_version = 10

    dispatch_id = get_new_uuid()
    order = _prepare(dispatch_id=dispatch_id, transport_type=transport_type)

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': DEFAULT_DISPATCH['driver_id'],
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
        },
    )
    assert response.status_code == 200

    assert grocery_dispatch.times_performer_info_called() == 1

    order.update()
    assert order.dispatch_performer.driver_id == DEFAULT_DISPATCH['driver_id']
    assert (
        order.dispatch_performer.eats_courier_id
        == ORDER_DATA['eats_courier_id']
    )
    assert (
        order.dispatch_performer.courier_full_name
        == DEFAULT_DISPATCH['courier_full_name']
    )
    assert (
        order.dispatch_performer.balance_client_id
        == ORDER_DATA['balance_client_id']
    )


@pytest.mark.config(GROCERY_ORDERS_HANDLE_PERFORMER_INFO=True)
async def test_performer_info_empty(
        taxi_grocery_orders, grocery_dispatch, _prepare, processing,
):
    dispatch_track_version = 10

    dispatch_id = get_new_uuid()
    transport_type = 'pedestrian'
    order = _prepare(dispatch_id=dispatch_id, transport_type=transport_type)

    fake_performer_id = 'null'

    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=dispatch_id,
        dispatch_status='accepted',
        dispatch_cargo_status='accepted',
        dispatch_driver_id=fake_performer_id,
        dispatch_courier_name=DEFAULT_DISPATCH['courier_name'],
        dispatch_transport_type=transport_type,
    )

    dispatch_performer = models.DispatchPerformer(
        driver_id=fake_performer_id,
        courier_full_name=DEFAULT_DISPATCH['courier_full_name'],
    )

    order.upsert(
        dispatch_status_info=dispatch_status_info,
        dispatch_performer=dispatch_performer,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/performer-info',
        json={
            'order_id': order.order_id,
            'driver_id': fake_performer_id,
            'dispatch_track_version': dispatch_track_version,
            'payload': {},
        },
    )
    assert response.status_code == 200

    assert grocery_dispatch.times_performer_info_called() == 0

    order.update()
    assert order.dispatch_performer.driver_id == fake_performer_id
    assert order.dispatch_performer.eats_courier_id is None
    assert (
        order.dispatch_performer.courier_full_name
        == DEFAULT_DISPATCH['courier_full_name']
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1
    event = events[0]

    assert event.payload == {
        'order_id': order.order_id,
        'reason': 'courier_info_update',
        'flow_version': 'grocery_flow_v1',
        'depot_id': order.depot_id,
        'related_orders': [order.order_id],
    }


@configs.DISPATCH_SUPPLY_CONFIG
@pytest.mark.now('2020-11-12T13:00:50.283761+00:00')
async def test_dispatch_create_request(
        taxi_grocery_orders,
        grocery_dispatch,
        eats_core_eater,
        experiments3,
        _prepare,
        processing,
        grocery_wms_gateway,
):
    dispatch_id = get_new_uuid()
    order = _prepare(
        dispatch_id=dispatch_id,
        init_status='assembling',
        delivery_zone_type='pedestrian',
        init_in_pg=False,
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/dispatch/register',
        json={
            'order_id': order.order_id,
            'due_time_point': ORDER_DATA['due_time_point'],
            'payload': {},
        },
    )
    assert response.status_code == 200

    order.update()

    assert grocery_dispatch.times_create_called() == 1
    assert order.dispatch_status_info.dispatch_id == dispatch_id
    assert order.dispatch_status_info.dispatch_status == 'created'


@pytest.mark.parametrize(
    'has_dispatch_status_info,status,cargo_status',
    [
        (True, 'created', 'new'),
        (True, 'accepted', 'accepted'),
        (False, None, None),
    ],
)
@pytest.mark.parametrize(
    'init_status',
    ['closed', 'delivering', 'checked_out', 'canceled', 'reserved'],
)
async def test_dispatch_cancel(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_payments,
        grocery_dispatch,
        init_status,
        has_dispatch_status_info,
        status,
        cargo_status,
):
    order_state = models.OrderState(
        wms_reserve_status='success', hold_money_status='success',
    )

    if has_dispatch_status_info:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id=get_new_uuid(),
            dispatch_status=status,
            dispatch_cargo_status=cargo_status,
        )
        grocery_dispatch.set_data(dispatch_id=dispatch_status_info.dispatch_id)
    else:
        dispatch_status_info = models.DispatchStatusInfo()

    order = models.Order(
        pgsql=pgsql,
        status=init_status,
        state=order_state,
        dispatch_status_info=dispatch_status_info,
        dispatch_flow='grocery_dispatch',
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    version = order.order_version

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )

    response = await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': True,
            'times_called': 1,
            'payload': {},
        },
    )

    order.update()

    want_status = init_status
    if init_status not in ('closed', 'canceled'):
        want_status = 'canceled'

    something_must_change = init_status != want_status

    assert response.status_code == 200
    if something_must_change:
        assert order.status == want_status
        assert order.order_version == version + 1

        assert grocery_payments.times_cancel_called() == 1

        if has_dispatch_status_info:
            assert grocery_dispatch.times_cancel_called() == 1
            assert order.dispatch_status_info.dispatch_status == 'revoked'
        else:
            assert grocery_dispatch.times_cancel_called() == 0
    else:
        assert order.status == init_status
        assert grocery_payments.times_cancel_called() == 0
        assert grocery_dispatch.times_cancel_called() == 0


@configs.GROCERY_DISPATCH_FLOW_EXPERIMENT
@pytest.mark.now(NOW_TIME)
async def test_dispatch_flow(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots,
):
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, region_id=REGION_ID)
    grocery_cart.set_grocery_flow_version(PROCESSING_FLOW_VERSION)

    grocery_cart_items = copy.deepcopy(grocery_cart.get_items())
    grocery_cart.set_items(grocery_cart_items)

    submit_headers = headers.DEFAULT_HEADERS.copy()
    submit_headers['X-YaTaxi-Bound-Sessions'] = 'eats:12345,taxi:6789'

    # Create order ------------------------------------------------------------
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit', json=SUBMIT_BODY, headers=submit_headers,
    )
    assert response.status_code == 200

    order_id = response.json()['order_id']
    order = models.Order(
        pgsql=pgsql,
        order_id=order_id,
        insert_in_pg=False,
        place_id='yamaps://12345',
        location='37.000000, 55.000000',
        currency=None,
    )
    order.update()

    assert order.order_id == order_id
    assert order.dispatch_flow == 'grocery_dispatch'


@pytest.mark.parametrize(
    'dispatch_status, expected_status, order_status_changed',
    [
        (200, 200, True),
        (404, 404, False),
        (409, 409, False),
        (425, 500, False),
        (500, 500, False),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_SEND_ASSEMBLED_CARGO=True)
async def test_assembled_set_state(
        taxi_grocery_orders,
        pgsql,
        processing,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        dispatch_status,
        expected_status,
        order_status_changed,
):
    dispatch_id = get_new_uuid()

    initial_status = 'assembling'
    order = models.Order(
        pgsql=pgsql,
        status=initial_status,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status='accepted',
            dispatch_cargo_status='performer_draft',
        ),
        dispatch_flow='grocery_dispatch',
    )
    order.update()
    assert order.state == models.OrderState()
    order.upsert(
        state=models.OrderState(
            wms_reserve_status='success', hold_money_status='success',
        ),
    )
    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        order_id=order.order_id,
        status='matching',
        order_ready_status=dispatch_status,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_delivery_type('pickup')

    assert order.status == initial_status
    assert order.order_version == 0

    response = await taxi_grocery_orders.post(
        '/processing/v1/set-state',
        json={
            'order_id': order.order_id,
            'state': 'assembled',
            'payload': {'success': True},
        },
    )
    assert response.status_code == expected_status

    order.update()
    if order_status_changed:
        assert order.status == 'assembled'
        assert order.order_version == 2  # 2 updates: state & status
    else:
        assert order.status == initial_status
        assert order.order_version == 0

    if order_status_changed:
        events = list(processing.events(scope='grocery', queue='processing'))
        assert len(events) == 1
        create_order_event = events[0]
        assert create_order_event.item_id == order.order_id
        assert create_order_event.payload == {
            'order_id': order.order_id,
            'reason': 'dispatch_ready',
            'flow_version': 'grocery_flow_v1',
            'order_version': order.order_version,
        }

    assert grocery_dispatch.times_order_ready_called() == 1
