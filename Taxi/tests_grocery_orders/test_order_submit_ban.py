import pytest

from . import headers

CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_VERSION = 4
OFFER_ID = 'offer-id'
LOCATION_IN_RUSSIA = [37.0, 55.0]
PLACE_ID = 'yamaps://12345'
FLOOR = '13'
FLAT = '666'
DOORCODE = '42'
DOORCODE_EXTRA = 'doorcode_extra'
BUILDING_NAME = 'building_name'
DOORBELL_NAME = 'doorbell_name'
LEFT_AT_DOOR = False
ENTRANCE = '3333'
COMMENT = 'comment'

PROCESSING_FLOW_VERSION = None

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
        'left_at_door': LEFT_AT_DOOR,
        'entrance': ENTRANCE,
        'comment': COMMENT,
    },
    'flow_version': PROCESSING_FLOW_VERSION,
}

DEPOT_ID = '2809'
REGION_ID = 102

BANNED_APPMETRICA_DEVICE_ID0 = 'device_id0'
BANNED_APPMETRICA_DEVICE_ID1 = 'device_id1'
BANNED_USER_TAG = 'banned'
YANDEX_UID_BANNED_IN_USER_PROFILES = 'bad_guy'

BANNED_ERROR_CODE = 'try_again_later'
BANNED_BY_APPMETRICA_MESSAGE = 'Banned by appmetrica_device_id'
BANNED_BY_ANTIFRAUD_MESSAGE = 'Banned by antifraud'
BANNED_IN_USER_PROFILES_MESSAGE = 'Banned by support'

GROCERY_ORDERS_SUBMIT_BANLISTS = pytest.mark.experiments3(
    name='grocery_orders_submit_banlists',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Banlist matching rules',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'appmetrica_device_id',
                                'set_elem_type': 'string',
                                'set': [BANNED_APPMETRICA_DEVICE_ID0],
                            },
                        },
                    ],
                },
                'type': 'any_of',
            },
            'value': {
                'code': BANNED_ERROR_CODE,
                'message': BANNED_BY_APPMETRICA_MESSAGE,
            },
        },
        {
            'title': 'Wrong manually typed OrderSubmitBadRequestCode',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'appmetrica_device_id',
                                'set_elem_type': 'string',
                                'set': [BANNED_APPMETRICA_DEVICE_ID1],
                            },
                        },
                    ],
                },
                'type': 'any_of',
            },
            'value': {
                'code': 'user_is_banned',
                'message': BANNED_BY_APPMETRICA_MESSAGE,
            },
        },
        {
            'title': 'Banned by antifraud',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'is_fraud',
                    'arg_type': 'bool',
                    'value': True,
                },
            },
            'value': {
                'code': BANNED_ERROR_CODE,
                'message': BANNED_BY_ANTIFRAUD_MESSAGE,
            },
        },
        {
            'title': 'Will be banned by user-profiles',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'type': 'contains',
                            'init': {
                                'arg_name': 'user_tags',
                                'set_elem_type': 'string',
                                'value': BANNED_USER_TAG,
                            },
                        },
                    ],
                },
                'type': 'any_of',
            },
            'value': {
                'code': BANNED_ERROR_CODE,
                'message': BANNED_IN_USER_PROFILES_MESSAGE,
            },
        },
    ],
    is_config=True,
    default_value={'code': '', 'message': ''},
)


GROCERY_ORDERS_USE_PROFILES_BANLIST = pytest.mark.experiments3(
    name='grocery_orders_use_profiles_banlist',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'use_profiles': True},
        },
    ],
    is_config=True,
)


def enable_antifraud_eats_cycle(enable_antifraud: bool, experiments3):
    experiments3.add_config(
        name='grocery_orders_enable_antifraud',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={
            'enable_eats_order_cycle': enable_antifraud,
            'enable_grocery_order_cycle': False,
        },
    )


@GROCERY_ORDERS_SUBMIT_BANLISTS
@pytest.mark.parametrize(
    'handle_path',
    ['/lavka/v1/orders/v1/submit', '/lavka/v1/orders/v2/submit'],
)
@pytest.mark.parametrize(
    'device_id,is_banned',
    [
        (BANNED_APPMETRICA_DEVICE_ID0, True),
        (BANNED_APPMETRICA_DEVICE_ID1, False),
        (headers.APPMETRICA_DEVICE_ID, False),
    ],
)
async def test_prefix_device_id_banlists(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        personal,
        yamaps_local,
        handle_path,
        device_id,
        is_banned,
):
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, region_id=REGION_ID)
    grocery_cart.set_grocery_flow_version(PROCESSING_FLOW_VERSION)

    submit_headers = headers.DEFAULT_HEADERS.copy()
    submit_headers['X-AppMetrica-DeviceId'] = device_id

    response = await taxi_grocery_orders.post(
        handle_path, json=SUBMIT_BODY, headers=submit_headers,
    )

    if is_banned:
        assert response.json()['code'] == BANNED_ERROR_CODE
        assert response.json()['message'] == BANNED_BY_APPMETRICA_MESSAGE
        assert response.status_code == 400
    else:
        assert response.status_code == 200


@GROCERY_ORDERS_SUBMIT_BANLISTS
@GROCERY_ORDERS_USE_PROFILES_BANLIST
@pytest.mark.parametrize(
    'handle_path',
    ['/lavka/v1/orders/v1/submit', '/lavka/v1/orders/v2/submit'],
)
@pytest.mark.parametrize(
    'yandex_uid,is_banned',
    [(YANDEX_UID_BANNED_IN_USER_PROFILES, True), ('not_a_bad_guy', False)],
)
async def test_banned_in_user_profiles(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        grocery_user_profiles,
        personal,
        yamaps_local,
        handle_path,
        yandex_uid,
        is_banned,
):
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, region_id=REGION_ID)
    grocery_cart.set_grocery_flow_version(PROCESSING_FLOW_VERSION)

    grocery_user_profiles.add_user_banned(
        yandex_uid=YANDEX_UID_BANNED_IN_USER_PROFILES,
    )

    submit_headers = headers.DEFAULT_HEADERS.copy()
    submit_headers['X-Yandex-UID'] = yandex_uid

    response = await taxi_grocery_orders.post(
        handle_path, json=SUBMIT_BODY, headers=submit_headers,
    )

    if is_banned:
        assert response.json()['code'] == BANNED_ERROR_CODE
        assert response.json()['message'] == BANNED_IN_USER_PROFILES_MESSAGE
        assert grocery_user_profiles.times_check_user_called() == 1
        assert response.status_code == 400
    else:
        assert response.status_code == 200


@GROCERY_ORDERS_SUBMIT_BANLISTS
@pytest.mark.parametrize(
    'is_banned, antifraud_enabled',
    [(True, True), (False, True), (False, False)],
)
async def test_antifraud(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        personal,
        yamaps_local,
        experiments3,
        antifraud,
        is_banned,
        antifraud_enabled,
):
    client_price = '1.23'
    short_address = 'Moscow, Varshavskoye Highway 141Ак1 12'

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_cart.default_cart.set_client_price(client_price)
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, region_id=REGION_ID)
    grocery_cart.set_grocery_flow_version(PROCESSING_FLOW_VERSION)

    enable_antifraud_eats_cycle(antifraud_enabled, experiments3)
    await taxi_grocery_orders.invalidate_caches()

    antifraud.set_is_fraud(is_banned)

    user_agent = 'user-agent'
    antifraud.check_antifraud_request(
        user_id=headers.YANDEX_UID,
        user_id_service='passport',
        user_personal_phone_id=headers.PERSONAL_PHONE_ID,
        client_ip=headers.USER_IP,
        user_agent=user_agent,
        application_type='yango_android',
        service_name='grocery',
        order_amount=client_price,
        order_currency=grocery_cart.get_items()[0].currency,
        short_address=short_address,
        address_comment=COMMENT,
        order_coordinates={
            'lon': LOCATION_IN_RUSSIA[1],
            'lat': LOCATION_IN_RUSSIA[0],
        },
        payment_method_id='id',
        payment_method='card',
        user_device_id=headers.APPMETRICA_DEVICE_ID,
    )
    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json=SUBMIT_BODY,
        headers={
            'X-Remote-IP': headers.USER_IP,
            'User-Agent': user_agent,
            **headers.DEFAULT_HEADERS,
        },
    )

    if antifraud_enabled:
        assert antifraud.times_antifraud_called() == 1
    else:
        assert antifraud.times_antifraud_called() == 0

    if is_banned:
        assert response.status_code == 400
        assert response.json()['code'] == BANNED_ERROR_CODE
        assert response.json()['message'] == BANNED_BY_ANTIFRAUD_MESSAGE
    else:
        assert response.status_code == 200


async def test_bad_fraud_response(
        taxi_grocery_orders,
        eats_core_eater,
        grocery_cart,
        grocery_depots,
        antifraud,
        experiments3,
):
    eats_core_eater.set_personal_email_id('email')

    pm_type = 'card'
    some_cart_id = '00000000-0000-0000-0000-d98013100500'
    offer_id = 'yyy'
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
        'payment_method_type': pm_type,
    }

    client_price = '1.23'

    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_cart.default_cart.set_client_price(client_price)
    grocery_cart.set_depot_id(depot_id=DEPOT_ID)
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID, region_id=REGION_ID)
    grocery_cart.set_grocery_flow_version(PROCESSING_FLOW_VERSION)

    antifraud.set_error_code(500)

    enable_antifraud_eats_cycle(True, experiments3)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/submit',
        json=submit_body,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
