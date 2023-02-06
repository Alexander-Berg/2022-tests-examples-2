import copy

import pytest

from . import headers
from . import models

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
COMMENT = 'comment'
DEPOT_ID = '2809'
ENTRANCE = '3333'

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
        'left_at_door': LEFT_AT_DOOR,
        'comment': COMMENT,
        'entrance': ENTRANCE,
    },
    'flow_version': PROCESSING_FLOW_VERSION,
}

GROCERY_ORDERS_CHECK_LOCAL_PHONE_NUMBER_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_check_local_phone_number',
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

GROCERY_ALLOWED_PHONE_NUMBERS_CONFIG = pytest.mark.experiments3(
    name='grocery_allowed_phone_numbers',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'allowed_any_ISR',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'ISR',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': {'any_allowed': True},
        },
        {
            'title': 'Only +7, +99 RUS',
            'predicate': {'type': 'true'},
            'value': {'any_allowed': False, 'allowed_prefixes': ['7', '99']},
        },
    ],
    is_config=True,
)


@GROCERY_ORDERS_CHECK_LOCAL_PHONE_NUMBER_EXPERIMENT
@pytest.mark.parametrize(
    'phone_number', [RUSSIAN_PHONE_NUMBER, ISRAELIAN_PHONE_NUMBER],
)
@pytest.mark.parametrize(
    'country,location',
    [
        (models.Country.Russia, LOCATION_IN_RUSSIA),
        (models.Country.Israel, LOCATION_IN_ISRAEL),
    ],
)
async def test_phone_number(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        personal,
        yamaps_local,
        country,
        location,
        phone_number,
):
    if country == models.Country.Israel:
        yamaps_local.set_data(location=','.join(map(str, location)))
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID, country_iso3=country.country_iso3,
    )
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    body = copy.deepcopy(SUBMIT_BODY)
    body['position']['location'] = location
    personal.phone = phone_number
    personal.personal_phone_id = headers.PERSONAL_PHONE_ID

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    if (
            (
                country == models.Country.Russia
                and phone_number == RUSSIAN_PHONE_NUMBER
            )
            or (
                country == models.Country.Israel
                and phone_number == ISRAELIAN_PHONE_NUMBER
            )
    ):
        assert response.status_code == 200
    else:
        assert response.json()['code'] == 'need_local_phone_number'
        assert response.status_code == 400


@GROCERY_ALLOWED_PHONE_NUMBERS_CONFIG
@pytest.mark.parametrize(
    'country,location,phone_number,allowed',
    [
        (
            models.Country.Russia,
            LOCATION_IN_RUSSIA,
            ISRAELIAN_PHONE_NUMBER,
            False,
        ),
        (
            models.Country.Russia,
            LOCATION_IN_RUSSIA,
            RUSSIAN_PHONE_NUMBER,
            True,
        ),
        (
            models.Country.Russia,
            LOCATION_IN_RUSSIA,
            AUSTRALIAN_PHONE_NUMBER,
            True,
        ),
        (
            models.Country.Israel,
            LOCATION_IN_ISRAEL,
            ISRAELIAN_PHONE_NUMBER,
            True,
        ),
        (
            models.Country.Israel,
            LOCATION_IN_ISRAEL,
            RUSSIAN_PHONE_NUMBER,
            True,
        ),
        (
            models.Country.Israel,
            LOCATION_IN_ISRAEL,
            AUSTRALIAN_PHONE_NUMBER,
            True,
        ),
    ],
)
async def test_prefix_phone_number(
        taxi_grocery_orders,
        grocery_cart,
        grocery_depots,
        personal,
        yamaps_local,
        country,
        location,
        phone_number,
        allowed,
):
    if country == models.Country.Israel:
        yamaps_local.set_data(location=','.join(map(str, location)))
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID, country_iso3=country.country_iso3,
    )
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})

    body = copy.deepcopy(SUBMIT_BODY)
    body['position']['location'] = location
    personal.phone = phone_number
    personal.personal_phone_id = headers.PERSONAL_PHONE_ID

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )

    if allowed:
        assert response.status_code == 200
    else:
        assert response.json()['code'] == 'need_local_phone_number'
        assert response.status_code == 400


@GROCERY_ORDERS_CHECK_LOCAL_PHONE_NUMBER_EXPERIMENT
@pytest.mark.parametrize(
    'gift_phone,gift_phone_normalized,location,country,resp_code',
    [
        pytest.param(
            '8(999)123-42-12',
            '+79991234212',
            LOCATION_IN_RUSSIA,
            models.Country.Russia,
            200,
            id='RUS local',
        ),
        pytest.param(
            '+7 (999) 123-42-12',
            '+79991234212',
            LOCATION_IN_RUSSIA,
            models.Country.Russia,
            200,
            id='RUS international',
        ),
        pytest.param(
            '072 234-5678',
            '+972722345678',
            LOCATION_IN_ISRAEL,
            models.Country.Israel,
            200,
            id='ISR local',
        ),
        pytest.param(
            '+972 72 234-5678',
            '+972722345678',
            LOCATION_IN_ISRAEL,
            models.Country.Israel,
            200,
            id='ISR international',
        ),
        pytest.param(
            '972 72 234-5678',
            '+972722345678',
            LOCATION_IN_ISRAEL,
            models.Country.Israel,
            200,
            id='omit "+"',
        ),
        pytest.param(
            '8(999)123-42-12',
            '+79991234212',
            LOCATION_IN_ISRAEL,
            models.Country.Israel,
            400,
            id='RUS in ISR',
        ),
        pytest.param(
            '972 72 234-5678',
            '+972722345678',
            LOCATION_IN_RUSSIA,
            models.Country.Russia,
            400,
            id='ISR in RUS',
        ),
    ],
)
async def test_gift_order_phone_number_normalization(
        taxi_grocery_orders,
        grocery_cart,
        personal,
        gift_phone,
        gift_phone_normalized,
        location,
        country,
        resp_code,
        yamaps_local,
        grocery_depots,
):
    if country == models.Country.Israel:
        yamaps_local.set_data(location=','.join(map(str, location)))
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID, country_iso3=country.country_iso3,
    )
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    gift_phone_id = '1a1a2b2b3c3c'

    body = copy.deepcopy(SUBMIT_BODY)
    body['position']['location'] = location
    body['gift_by_phone'] = {'phone_number': gift_phone}

    personal.check_request(
        phone=gift_phone_normalized, personal_phone_id=gift_phone_id,
    )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers.NO_YANDEX_USER_HEADERS,
    )
    assert response.status_code == resp_code
    if resp_code == 400:
        assert response.json()['code'] == 'need_local_phone_number'


@pytest.mark.parametrize(
    'has_phone',
    [pytest.param(True, id='Found phone'), pytest.param(False, id='No phone')],
)
async def test_no_phone_id(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        user_api,
        has_phone,
):
    grocery_depots.add_depot(legacy_depot_id=DEPOT_ID)
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    phone_id = 'some_long_old_phone_id'

    body = copy.deepcopy(SUBMIT_BODY)
    headers_local = copy.deepcopy(headers.DEFAULT_HEADERS)
    del headers_local['X-YaTaxi-PhoneId']

    user_api.check_request(
        check_request_flag=True, personal_phone_id=headers.PERSONAL_PHONE_ID,
    )

    if has_phone:
        user_api.set_phone_id(phone_id)

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/submit',
        json=body,
        headers=headers_local,
    )

    assert response.status_code == 200
    order_res = models.Order(
        pgsql=pgsql, order_id=response.json()['order_id'], insert_in_pg=False,
    )
    order_res.update()

    if has_phone:
        assert order_res.phone_id == phone_id
    else:
        assert order_res.phone_id is None
