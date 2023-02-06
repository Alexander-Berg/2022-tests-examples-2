import datetime
import decimal

import pytest

from tests_grocery_cart.plugins import keys

IDEMPOTENCY_TOKEN = '123456789'

CREATE_HEADERS = {
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}


@pytest.mark.parametrize(
    'yandex_uid, personal_phone_id',
    [('yandex-uid-123', None), (None, 'personal_phone_id-123')],
)
async def test_basic(
        taxi_grocery_cart,
        tristero_parcels,
        fetch_items,
        fetch_cart,
        yandex_uid,
        personal_phone_id,
        grocery_p13n,
):
    tristero_suffix = ':st-pa'
    item_id_1 = 'item_id_1' + tristero_suffix
    item_id_2 = 'item_id_2' + tristero_suffix

    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    tristero_parcels.add_parcel(parcel_id=item_id_1)
    tristero_parcels.add_parcel(parcel_id=item_id_2)

    json = {
        'items': [
            {'product_id': item_id_1, 'quantity': '1'},
            {'product_id': item_id_2, 'quantity': '1'},
        ],
        'yandex_uid': yandex_uid,
        'locale': 'ru',
        'position': keys.DEFAULT_POSITION,
        'personal_phone_id': personal_phone_id,
        'timeslot': {'start': timeslot_start, 'end': timeslot_end},
        'request_kind': timeslot_request_kind,
        'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/create',
        json=json,
        headers={**CREATE_HEADERS, 'User-Agent': keys.DEFAULT_USER_AGENT},
    )

    grocery_p13n.set_modifiers_request_check(on_modifiers_request=None)

    assert response.status_code == 200
    assert 'cart_id' in response.json()
    assert response.json()['cart_version'] == 1

    cart_id = response.json()['cart_id']

    items = fetch_items(cart_id)
    assert len(items) == 2

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(1)

    item = items[1]
    assert item.item_id == item_id_2
    assert item.quantity == decimal.Decimal(1)

    cart = fetch_cart(cart_id)

    assert cart.user_type == 'taxi'
    assert cart.user_id == 'tristero_user_id'
    assert cart.session == ''
    assert cart.idempotency_token == IDEMPOTENCY_TOKEN
    assert cart.status == 'editing'
    assert cart.delivery_type == 'eats_dispatch'
    assert cart.timeslot_start == _stringtime(timeslot_start)
    assert (
        cart.timeslot_start - _stringtime(timeslot_start)
    ).total_seconds() == 0
    assert (cart.timeslot_end - _stringtime(timeslot_end)).total_seconds() == 0
    assert cart.timeslot_request_kind == timeslot_request_kind

    assert grocery_p13n.discount_modifiers_times_called == 1

    # Check idempotency

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/create', json=json, headers=CREATE_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['cart_id'] == cart_id
    assert response_json['cart_version'] == 1
    assert 'offer_id' in response_json


@pytest.mark.parametrize(
    'items',
    [
        [
            {'product_id': 'item_id_1:st-pa', 'quantity': '1'},
            {'product_id': 'item_id_2', 'quantity': '1'},
        ],
        [
            {'product_id': 'item_id_1:st-pa', 'quantity': '1'},
            {'product_id': 'item_id_2:st-pa', 'quantity': '2'},
        ],
    ],
)
async def test_incorrect_items(taxi_grocery_cart, tristero_parcels, items):
    yandex_uid = '123'

    tristero_parcels.add_parcel(parcel_id=items[0]['product_id'])
    tristero_parcels.add_parcel(parcel_id=items[1]['product_id'])

    json = {
        'items': items,
        'yandex_uid': yandex_uid,
        'locale': 'ru',
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/create', json=json, headers=CREATE_HEADERS,
    )

    assert response.status_code == 400


async def test_no_yandex_uid_or_phone(taxi_grocery_cart, tristero_parcels):
    tristero_suffix = ':st-pa'
    item_id_1 = 'item_id_1' + tristero_suffix
    item_id_2 = 'item_id_2' + tristero_suffix

    tristero_parcels.add_parcel(parcel_id=item_id_1)
    tristero_parcels.add_parcel(parcel_id=item_id_2)

    json = {
        'items': [
            {'product_id': item_id_1, 'quantity': '1'},
            {'product_id': item_id_2, 'quantity': '1'},
        ],
        'locale': 'ru',
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/create', json=json, headers=CREATE_HEADERS,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'yandex_uid, personal_phone_id',
    [('yandex-uid-123', None), (None, 'personal_phone_id-123')],
)
async def test_create_cart_with_products(
        taxi_grocery_cart,
        overlord_catalog,
        fetch_items,
        fetch_cart,
        yandex_uid,
        personal_phone_id,
):
    item_id = 'item_id_1'
    item_price = '100'
    item_count = '20'
    user_type = 'taxi'
    user_id = '1234566754321'
    session = user_type + ':' + user_id
    currency = 'GBP'

    overlord_catalog.add_product(
        product_id=item_id, price=item_price, in_stock=item_count,
    )

    json = {
        'items': [
            {
                'product_id': item_id,
                'quantity': item_count,
                'price': item_price,
                'currency': currency,
            },
        ],
        'yandex_uid': yandex_uid,
        'locale': 'ru',
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'personal_phone_id': personal_phone_id,
    }

    headers = {
        'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-Session': session,
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/create', json=json, headers=headers,
    )

    assert response.status_code == 200
    assert 'cart_id' in response.json()
    assert response.json()['cart_version'] == 1

    cart_id = response.json()['cart_id']

    items = fetch_items(cart_id)
    assert len(items) == 1

    item = items[0]
    assert item.item_id == item_id
    assert item.quantity == decimal.Decimal(item_count)
    assert item.price == decimal.Decimal(item_price)
    assert item.currency == currency

    cart = fetch_cart(cart_id)

    assert cart.user_type == 'yandex_taxi'
    assert cart.user_id == user_id
    assert cart.session == session
    assert cart.idempotency_token == IDEMPOTENCY_TOKEN
    assert cart.status == 'editing'
    assert cart.delivery_type == 'eats_dispatch'

    # Check idempotency

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/create', json=json, headers=headers,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['cart_id'] == cart_id
    assert response_json['cart_version'] == 1
    assert 'offer_id' in response_json


@pytest.mark.experiments3(
    name='grocery_orders_count_override',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always override',
            'predicate': {'type': 'true'},
            'value': {'orders_count': 100},
        },
    ],
    is_config=True,
)
async def test_orders_count_override(
        taxi_grocery_cart, overlord_catalog, mockserver,
):
    """ orders_count should be sent to p13n if
    orders count override is specified """
    item_id = 'item_id_1'
    item_price = '100'
    item_count = '20'
    user_type = 'taxi'
    user_id = '1234566754321'
    session = user_type + ':' + user_id

    overlord_catalog.add_product(
        product_id=item_id, price=item_price, in_stock=item_count,
    )

    json = {
        'items': [
            {
                'product_id': item_id,
                'quantity': item_count,
                'price': item_price,
                'currency': 'GBP',
            },
        ],
        'locale': 'ru',
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'personal_phone_id': 'some_personal_phone_id',
    }

    headers = {
        'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-Session': session,
    }

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _discount_modifiers(request):
        assert request.json['orders_count'] == 100

        return {'modifiers': []}

    await taxi_grocery_cart.post(
        '/internal/v1/cart/create', json=json, headers=headers,
    )

    assert _discount_modifiers.times_called == 1


def _stringtime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')
