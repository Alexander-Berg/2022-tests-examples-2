# pylint: disable=too-many-lines
import copy
import decimal

from grocery_mocks import grocery_p13n as modifiers  # pylint: disable=E0401
import pytest
import pytz

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

HEADER_TAXI_SESSION = 'taxi:uuu'
HEADER_YANDEX_UID = '13579'
HEADER_EATS_ID = '97531'
HEADERS_WITH_YANDEX_UID = {
    'X-YaTaxi-Session': HEADER_TAXI_SESSION,
    'X-Yandex-UID': HEADER_YANDEX_UID,
    'X-YaTaxi-User': f'eats_user_id={HEADER_EATS_ID}',
    'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
}

BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
}

TAXI_HEADERS = BASIC_HEADERS
EDA_HEADERS = {'X-YaTaxi-User': 'eats_user_id=12345', **BASIC_HEADERS}
EDA_HEADERS_2 = {'X-YaTaxi-User': 'k=v, eats_user_id=12345', **BASIC_HEADERS}


@pytest.mark.parametrize('headers', [TAXI_HEADERS, EDA_HEADERS, EDA_HEADERS_2])
async def test_basic(
        taxi_grocery_cart, now, pgsql, headers, grocery_coupons, grocery_p13n,
):
    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    headers['User-Agent'] = keys.DEFAULT_USER_AGENT
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'depot_id' not in response_json
    assert len(response_json['cart_id']) == 36
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute('SELECT cart_version, updated, depot_id FROM cart.carts')
    carts = list(cursor)
    assert len(carts) == 1, carts
    cart = carts[0]
    assert cart[0] == 1
    assert cart[2] == keys.DEFAULT_LEGACY_DEPOT_ID
    assert _to_utc(cart[1]) >= now, cart[1]
    assert grocery_p13n.discount_modifiers_times_called == 1


@pytest.mark.parametrize(
    'test_case, headers, cart_id, item_id, depot_id',
    [
        (
            'eda_cart_id_not_found_1',
            EDA_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee333',
            'item_id_1',
            '111',
        ),
        (
            'eda_cart_id_not_found_2',
            EDA_HEADERS_2,
            '11111111-2222-aaaa-bbbb-cccdddeee333',
            'item_id_1',
            '111',
        ),
        (
            'eda_cart_checked_out_1',
            EDA_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee011',
            'item_id_11',
            '111',
        ),
        (
            'eda_cart_checked_out_2',
            EDA_HEADERS_2,
            '11111111-2222-aaaa-bbbb-cccdddeee011',
            'item_id_11',
            '111',
        ),
        (
            'taxi_cart_id_not_found',
            TAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee333',
            'item_id_2',
            '222',
        ),
        (
            'taxi_cart_checked_out',
            TAXI_HEADERS,
            '11111111-2222-aaaa-bbbb-cccdddeee012',
            'item_id_12',
            '222',
        ),
    ],
)
@pytest.mark.pgsql('grocery_cart', files=['non_existing_cart.sql'])
async def test_update_nonexisting_cart(
        taxi_grocery_cart, test_case, headers, cart_id, item_id, depot_id,
):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        headers=headers,
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart_id,
            'cart_version': 1,
            'items': [
                {
                    'id': item_id,
                    'price': '345',
                    'quantity': '1',
                    'currency': 'RUB',
                },
            ],
        },
    )
    assert response.status_code == 404


async def test_update_400(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [
                {
                    'id': 'item_id',
                    'price': '345',
                    'quantity': '1',
                    'currency': 'RUB',
                },
                {
                    'id': 'item_id',
                    'price': '345',
                    'quantity': '1',
                    'currency': 'RUB',
                },
            ],
        },
        headers=TAXI_HEADERS,
    )
    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 'REPEATED_IDS'


@pytest.mark.translations(
    discount_descriptions={
        'test_mastercard_discount_on_cart': {
            'ru': (
                'Скидка %(discount_template)s по карте Mastercard '
                'на экране корзины'
            ),
        },
    },
)
@pytest.mark.parametrize('headers', [TAXI_HEADERS, EDA_HEADERS, EDA_HEADERS_2])
async def test_basic_with_items(
        taxi_grocery_cart,
        mockserver,
        pgsql,
        headers,
        offers,
        experiments3,
        grocery_surge,
        overlord_catalog,
        grocery_p13n,
):
    item_id = 'item_id_1'
    item_price = '100'
    item_discount_price = '77'
    item_count = '20'

    offer_id = 'some_offer_id'
    common.create_offer(offers, experiments3, grocery_surge, offer_id=offer_id)

    discount_value = int(item_price) - int(item_discount_price)

    discount_description = {
        'discount_value': f'{discount_value} $SIGN$$CURRENCY$',
        'description_template': (
            f'Скидка {discount_value} $SIGN$$CURRENCY$ по карте Mastercard'
        ),
        'cart_description_template': (
            f'Скидка {discount_value} $SIGN$$CURRENCY$ по карте Mastercard на '
            f'экране корзины'
        ),
        'type': 'mastercard',
    }
    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=(
            lambda request_headers, request_body: 'X-YaTaxi-Session'
            in request_headers
        ),
    )
    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(discount_value - 0.2),
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
        meta={
            'picture': 'mastercard',
            'subtitle_tanker_key': 'test_mastercard_discount_on_cart',
            'payment_method_subtitle': 'test_mastercard_discount',
        },
    )

    overlord_catalog.add_product(
        product_id=item_id, price=item_price, in_stock=item_count,
    )

    item = {
        'id': item_id,
        'price': item_price,
        'quantity': '1',
        'currency': 'RUB',
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'offer_id': offer_id,
            'items': [item],
        },
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['available_for_checkout'] is False
    assert response_json['checkout_unavailable_reason'] == 'price-mismatch'
    assert response_json['hide_price_mismatch'] is True
    assert response_json['offer_id'] == offer_id
    assert response_json['discount_descriptions'] == [discount_description]

    assert len(response_json['items']) == 1
    response_item = response_json['items'][0]
    assert response_item == {
        'id': item_id,
        'price': item_price,
        'catalog_price': item_discount_price,
        'catalog_price_template': f'{item_price} $SIGN$$CURRENCY$',
        'catalog_total_price_template': f'{item_price} $SIGN$$CURRENCY$',
        'currency': 'RUB',
        'quantity': '1',
        'quantity_limit': item_count,
        'title': f'title for {item_id}',
        'subtitle': f'subtitle for {item_id}',
        'image_url_template': f'url for {item_id}',
        'image_url_templates': [f'url for {item_id}'],
        'restrictions': [],
    }

    cart_id = response_json['cart_id']
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        f'SELECT item_id, price, quantity, currency, status '
        f'FROM cart.cart_items WHERE cart_id::text=\'{cart_id}\'',
    )
    items = list(cursor)
    assert len(items) == 1, items
    pg_item = items[0]
    assert pg_item[0] == item['id']
    assert pg_item[1] == decimal.Decimal(item['price'])
    assert pg_item[2] == decimal.Decimal(item['quantity'])
    assert pg_item[3] == item['currency']
    assert pg_item[4] == 'in_cart'


@pytest.mark.parametrize(
    ('expected_code', 'headers', 'product'),
    [
        (404, TAXI_HEADERS, 'item'),
        (200, EDA_HEADERS, 'item'),
        (200, EDA_HEADERS, 'parcel'),
        (200, EDA_HEADERS_2, 'item'),
    ],
)
async def test_delete_item_eda(
        taxi_grocery_cart, pgsql, load, expected_code, headers, product,
):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(load(f'eda_one_{product}.sql'))

    item = {
        'id': 'item_id_1' if product == 'item' else 'item_id_1:st-pa',
        'price': '345',
        'quantity': '0',
        'currency': 'RUB',
    }

    existing_cart_id = '8da556be-0971-4f3b-a454-d980130662cc'
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': existing_cart_id,
            'cart_version': 1,
            'items': [item],
        },
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        cart_id = response_json['cart_id']
        assert not response_json['items']
        cursor.execute(
            f'SELECT item_id, price, quantity, currency, status '
            f'FROM cart.cart_items '
            f'WHERE cart_id::text=\'{cart_id}\'',
        )
        items = list(cursor)

        assert len(items) == 1

        quantity = items[0][2]
        status = items[0][4]

        assert quantity == 0
        assert status == 'deleted_before_checkout'


@pytest.mark.parametrize(
    ('expected_code', 'headers', 'product'),
    [
        (200, TAXI_HEADERS, 'item'),
        (200, TAXI_HEADERS, 'parcel'),
        (404, EDA_HEADERS, 'item'),
        (404, EDA_HEADERS_2, 'item'),
    ],
)
async def test_delete_item_taxi(
        taxi_grocery_cart, pgsql, load, expected_code, headers, product,
):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(load(f'taxi_one_{product}.sql'))

    item = {
        'id': 'item_id_1' if product == 'item' else 'item_id_1:st-pa',
        'price': '345',
        'quantity': '0',
        'currency': 'RUB',
    }

    existing_cart_id = '8da556be-0971-4f3b-a454-d980130662cc'
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': existing_cart_id,
            'cart_version': 1,
            'items': [item],
        },
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        cart_id = response_json['cart_id']
        assert not response_json['items']
        cursor.execute(
            f'SELECT item_id, price, quantity, currency, status '
            f'FROM cart.cart_items '
            f'WHERE cart_id::text=\'{cart_id}\'',
        )
        items = list(cursor)

        assert len(items) == 1

        quantity = items[0][2]
        status = items[0][4]

        assert quantity == 0
        assert status == 'deleted_before_checkout'


@pytest.mark.parametrize(
    ('expected_code', 'headers', 'product'),
    [
        (404, TAXI_HEADERS, 'item'),
        (200, EDA_HEADERS, 'item'),
        (400, EDA_HEADERS, 'parcel'),
        (200, EDA_HEADERS_2, 'item'),
    ],
)
async def test_update_item_eda(
        taxi_grocery_cart,
        pgsql,
        overlord_catalog,
        load,
        expected_code,
        headers,
        product,
        grocery_p13n,
):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(load(f'eda_one_{product}.sql'))

    item = {
        'id': 'item_id_1' if product == 'item' else 'item_id_1:st-pa',
        'price': '345',
        'quantity': '2',
        'currency': 'RUB',
    }

    overlord_catalog.add_product(
        product_id=item['id'], price=item['price'], in_stock='10',
    )

    existing_cart_id = '8da556be-0971-4f3b-a454-d980130662cc'

    headers['User-Agent'] = keys.DEFAULT_USER_AGENT
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': existing_cart_id,
            'cart_version': 1,
            'items': [item],
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        cart_id = response_json['cart_id']
        assert len(response_json['items']) == 1
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(
            f'SELECT item_id, price, quantity, currency '
            f'FROM cart.cart_items '
            f'WHERE cart_id::text=\'{cart_id}\' and status=\'in_cart\'',
        )
        items = list(cursor)
        assert len(items) == 1, items
        pg_item = items[0]
        assert pg_item[0] == item['id']
        assert pg_item[1] == decimal.Decimal(item['price'])
        assert pg_item[2] == decimal.Decimal(item['quantity'])
        assert pg_item[3] == item['currency']

        assert grocery_p13n.discount_modifiers_times_called == 1


async def test_accepted_differ_from_overlord_price(
        pgsql, overlord_catalog, cart,
):
    item_id = 'item_id_1'
    accepted_price = '350'
    overlord_price = '500'

    overlord_catalog.add_product(
        product_id=item_id, price=overlord_price, in_stock='10',
    )

    response = await cart.modify({item_id: {'q': 1, 'p': accepted_price}})

    diff = response['diff_data']['products']
    assert len(diff) == 1
    diff = diff[0]
    assert diff == {
        'price': {
            'actual_template': '500 $SIGN$$CURRENCY$',
            'diff_template': '150 $SIGN$$CURRENCY$',
            'previous_template': '350 $SIGN$$CURRENCY$',
            'trend': 'increase',
        },
        'product_id': 'item_id_1',
    }

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        f'SELECT price '
        f'FROM cart.cart_items '
        f'WHERE cart_id::text=\'{cart.cart_id}\' and status=\'in_cart\'',
    )

    items = list(cursor)
    assert len(items) == 1
    pg_item = items[0]

    # Store in db user accepted price to show correct diff data.
    assert pg_item[0] == decimal.Decimal(accepted_price)


@pytest.mark.parametrize(
    ('expected_code', 'headers', 'product'),
    [
        (404, TAXI_HEADERS, 'item'),
        (200, EDA_HEADERS, 'item'),
        (400, EDA_HEADERS, 'parcel'),
        (200, EDA_HEADERS_2, 'item'),
    ],
)
async def test_add_item_eda(
        taxi_grocery_cart,
        pgsql,
        overlord_catalog,
        load,
        expected_code,
        headers,
        product,
):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(load(f'eda_one_{product}.sql'))

    item = {
        'id': 'item_id_2' if product == 'item' else 'item_id_2:st-pa',
        'price': '345',
        'quantity': '2',
        'currency': 'RUB',
    }

    overlord_catalog.add_product(
        product_id=item['id'], price=item['price'], in_stock='10',
    )

    existing_cart_id = '8da556be-0971-4f3b-a454-d980130662cc'
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': existing_cart_id,
            'cart_version': 1,
            'items': [item],
        },
        headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        cart_id = response_json['cart_id']
        assert len(response_json['items']) == 2
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(
            f'SELECT item_id, price, quantity, currency '
            f'FROM cart.cart_items '
            f'WHERE cart_id::text=\'{cart_id}\' and status=\'in_cart\'',
        )
        items = list(cursor)
        assert len(items) == 2, items
        for pg_item in items:
            if pg_item[0] == 'item_id_2':
                assert pg_item[0] == item['id']
                assert pg_item[1] == decimal.Decimal(item['price'])
                assert pg_item[2] == decimal.Decimal(item['quantity'])
                assert pg_item[3] == item['currency']


async def test_no_products_in_overlord(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [
                {
                    'id': 'test_item',
                    'price': '123',
                    'quantity': '1',
                    'currency': 'RUB',
                },
            ],
        },
        headers=EDA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['items'][0]['quantity_limit'] == '0'


async def test_depot_not_found(cart, grocery_depots):
    grocery_depots.clear_depots()
    response = await cart.modify({'test_item': {'q': '1', 'p': '123'}})
    assert response['checkout_unavailable_reason'] == 'cannot_find_depot'


async def test_add_to_existing(taxi_grocery_cart, overlord_catalog):
    item_id = 'item_id'
    overlord_catalog.add_product(product_id=item_id, price='345')

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={'position': keys.DEFAULT_POSITION, 'items': []},
        headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['cart_version'] == 1
    assert response_json['items'] == []

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'cart_id': response_json['cart_id'],
            'cart_version': response_json['cart_version'],
            'position': keys.DEFAULT_POSITION,
            'items': [
                {
                    'id': item_id,
                    'price': '345',
                    'quantity': '1',
                    'currency': 'RUB',
                },
            ],
        },
        headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['available_for_checkout']


async def test_idempotency(cart, overlord_catalog):
    overlord_catalog.add_product(product_id='item2', price='345')

    # Create
    await cart.modify({'item2': {'q': 1, 'p': 345}})
    assert cart.cart_version == 1

    # Update
    await cart.modify(
        {'item2': {'q': 0, 'p': 345}}, headers={'X-Idempotency-Token': 'i1'},
    )
    assert cart.cart_version == 2

    cart_data = cart.fetch_db()
    assert cart_data.idempotency_token == 'i1'

    # Update with other token, conflict
    cart.cart_version = 1
    with pytest.raises(cart.HttpError) as exc:
        await cart.modify(
            {'item2': {'q': 0, 'p': 345}},
            headers={'X-Idempotency-Token': 'i2'},
        )
    assert exc.value.status_code == 409

    # Update with original token, ok
    await cart.modify(
        {'item2': {'q': 0, 'p': 345}}, headers={'X-Idempotency-Token': 'i1'},
    )
    assert cart.cart_version == 2


async def test_idempotency_same_update(cart, overlord_catalog):
    overlord_catalog.add_product(product_id='item1', price='345')
    overlord_catalog.add_product(product_id='item2', price='345')

    await cart.modify(
        {'item1': {'q': 1, 'p': 345}}, headers={'X-Idempotency-Token': 'i1'},
    )
    await cart.modify(
        {'item2': {'q': 2, 'p': 345}}, headers={'X-Idempotency-Token': 'i2'},
    )
    cart.cart_version = 1
    with pytest.raises(cart.HttpError) as exc:
        await cart.modify(
            {'item2': {'q': 3, 'p': 345}},
            headers={'X-Idempotency-Token': 'i3'},
        )
    assert exc.value.status_code == 409

    data = await cart.retrieve()
    assert {(item['id'], item['quantity']) for item in data['items']} == {
        ('item1', '1'),
        ('item2', '2'),
    }


async def test_update_checked_out_cart(
        taxi_grocery_cart, cart, overlord_catalog,
):
    overlord_catalog.add_product(product_id='item1', price='345')
    overlord_catalog.add_product(product_id='item2', price='345')

    def _fetch_cart_version():
        cart_db = cart.fetch_db()
        return cart_db.cart_version

    await cart.modify({'item1': {'q': 1, 'p': 345}})
    assert _fetch_cart_version() == 1

    json = {
        'position': keys.DEFAULT_POSITION,
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'offer_id': cart.offer_id,
    }
    response = await taxi_grocery_cart.post(
        '/internal/v2/cart/checkout', headers=TAXI_HEADERS, json=json,
    )

    assert response.status_code == 200
    assert _fetch_cart_version() == 1

    was_404 = False
    try:
        await cart.modify({'item2': {'q': 1, 'p': 345}})
    except common.CartHttpError as error:
        assert error.status_code == 404
        was_404 = True

    assert _fetch_cart_version() == 1
    assert was_404


def _to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.UTC).replace(tzinfo=None)
    return stamp


@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_update_delivery_type(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'delivery_type': 'eats_dispatch',
        },
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )
    assert response.status_code == 200

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'delivery_type': 'eats_dispatch',
        },
        headers={'X-Yandex-Uid': '4355', **TAXI_HEADERS},
    )
    assert response.status_code == 200

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'delivery_type': 'rover',
        },
        headers={'X-Yandex-Uid': '4355', **TAXI_HEADERS},
    )
    assert response.status_code == 200

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'delivery_type': 'pickup',
        },
        headers={'X-Yandex-Uid': '34532', **TAXI_HEADERS},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'DELIVERY_TYPE_NOT_ALLOWED'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'delivery_type': 'pickup',
        },
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'delivery_type,item_id,available_delivery_types',
    [
        ('pickup', 'item-id:st-md', ['pickup']),
        ('eats_dispatch', 'item-id', ['pickup', 'eats_dispatch', 'rover']),
    ],
)
@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_new_cart_delivery_type(
        cart, delivery_type, item_id, available_delivery_types,
):
    response = await cart.modify(
        products={item_id: {'q': 1, 'p': 1}},
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )

    assert set(response['available_delivery_types']) == set(
        available_delivery_types,
    )
    assert response['delivery_type'] == delivery_type


@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_change_available_delivery_types(cart):
    item_id = 'item-id'
    response = await cart.modify(
        products={item_id: {'q': 1, 'p': 1}},
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )

    assert set(response['available_delivery_types']) == set(
        ['pickup', 'eats_dispatch', 'rover'],
    )
    assert response['delivery_type'] == 'eats_dispatch'

    markdown_item = 'item-xxx:st-md'
    response = await cart.modify(
        products={markdown_item: {'q': 1, 'p': 1}},
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )

    assert response['available_delivery_types'] == ['pickup']
    assert response['delivery_type'] == 'pickup'

    item_id = 'item-id-1'
    response = await cart.modify(
        products={item_id: {'q': 1, 'p': 1}},
        headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
    )

    assert response['available_delivery_types'] == ['pickup']
    assert response['delivery_type'] == 'pickup'

    try:
        await cart.modify(
            products={},
            delivery_type='eats_dispatch',
            headers={'X-Yandex-Uid': '8484', **TAXI_HEADERS},
        )
    except common.CartHttpError as exc:
        assert exc.status_code == 400
    else:
        assert False


@pytest.mark.pgsql('grocery_cart', files=['localized_product.sql'])
@pytest.mark.parametrize('locale', ['ru', 'en', 'he'])
async def test_localized_products_response(
        taxi_grocery_cart, overlord_catalog, locale, load_json,
):
    localized = load_json('expected_product_localization.json')
    overlord_catalog.add_product(product_id='localized_product', price='345')

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee005',
            'cart_version': 1,
            'items': [
                {
                    'id': 'localized_product',
                    'price': '345',
                    'quantity': '2',
                    'currency': 'RUB',
                },
            ],
        },
        headers={
            'X-YaTaxi-Session': 'eats:123',
            'X-Request-Language': locale,
            'X-Idempotency-Token': common.UPDATE_IDEMPOTENCY_TOKEN,
            'X-YaTaxi-User': 'eats_user_id=12345',
        },
    )
    assert response.status_code == 200

    item = response.json()['items'][0]
    assert item['title'] == localized[locale]['title']
    assert item['subtitle'] == localized[locale]['subtitle']


async def test_invalid_currency(taxi_grocery_cart, overlord_catalog):
    overlord_catalog.add_product(product_id='test_product', price='345')

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [
                {
                    'id': 'test_product',
                    'price': '345',
                    'quantity': '2',
                    'currency': 'USD',
                },
            ],
        },
        headers=TAXI_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['checkout_unavailable_reason'] == 'price-mismatch'


# Проверяем случаи когда:
# 1. хотят создать пустую корзину, передают товар с quantity=0.
# Возвращаем 400 с кодом ошибки INVALID_PARAMS
# 2. удаляют все товары из корзины. Проверяем что новая схема
# скидок отрабатывает корректно
@pytest.mark.parametrize(
    'cart_id',
    [
        pytest.param(
            '11111111-2222-aaaa-bbbb-cccdddeee001',
            marks=[pytest.mark.pgsql('grocery_cart', files=['one_item.sql'])],
            id='clear_cart',
        ),
        pytest.param(None, id='create_empty_cart'),
    ],
)
async def test_empty_cart_creation(
        taxi_grocery_cart,
        offers,
        experiments3,
        grocery_surge,
        overlord_catalog,
        grocery_p13n,
        cart_id,
):
    item_id = 'item_id_1'
    item_price = '100'
    item_count = '20'

    offer_id = 'some_offer_id'
    common.create_offer(offers, experiments3, grocery_surge, offer_id=offer_id)

    grocery_p13n.add_modifier(
        product_id=item_id,
        value='20',
        discount_type=modifiers.DiscountType.PAYMENT_METHOD_DISCOUNT,
    )

    overlord_catalog.add_product(
        product_id=item_id, price=item_price, in_stock=item_count,
    )

    item = {
        'id': item_id,
        'price': item_price,
        'quantity': '0',
        'currency': 'RUB',
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'cart_id': cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'offer_id': offer_id,
            'items': [item],
        },
        headers={
            **BASIC_HEADERS,
            'X-YaTaxi-Session': 'eats:123',
            'X-YaTaxi-User': 'eats_user_id=12345',
        },
    )
    if cart_id is not None:
        assert response.status_code == 200
        assert response.json()['items'] == []
    else:
        assert response.status_code == 400
        assert response.json()['code'] == 'INVALID_PARAMS'
        assert (
            response.json()['message']
            == 'Trying to create cart with zero quantity elements: "item_id_1"'
        )


@pytest.mark.now(keys.TS_NOW)
async def test_additional_offer_info_log(
        taxi_grocery_cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        testpoint,
        grocery_depots,
):
    offer_id = '0'
    user_id = '123456abcd'

    delivery_cost = '100'
    next_delivery_cost = '50'
    next_delivery_threshold = '350'
    min_eta = 20
    max_eta = 10
    minimum_order = '300'

    actual_delivery = {
        'cost': delivery_cost,
        'next_cost': next_delivery_cost,
        'next_threshold': next_delivery_threshold,
    }
    legacy_depot_id = keys.DEFAULT_LEGACY_DEPOT_ID

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=offer_id,
        depot_id=legacy_depot_id,
        min_eta=str(min_eta),
        max_eta=str(max_eta),
        is_surge=True,
        minimum_order=minimum_order,
        delivery=actual_delivery,
    )

    location_str = (
        str(float(keys.DEFAULT_DEPOT_LOCATION[1]))
        + ';'
        + str(float(keys.DEFAULT_DEPOT_LOCATION[0]))
    )

    @testpoint('yt_offer_additional_info')
    def yt_offer_additional_info(offer_additional_info):
        assert offer_additional_info['version'] == 1
        assert offer_additional_info['offer_id'] == offer_id
        assert offer_additional_info['doc'] == {
            'active_zone': 'foot',
            'foot': {
                'delivery_cost': delivery_cost,
                'delivery_conditions': [
                    {
                        'delivery_cost': delivery_cost,
                        'order_cost': minimum_order,
                    },
                    {
                        'delivery_cost': next_delivery_cost,
                        'order_cost': next_delivery_threshold,
                    },
                ],
                'is_surge': True,
                'is_manual': False,
                'next_delivery_cost': next_delivery_cost,
                'next_delivery_threshold': next_delivery_threshold,
                'max_eta_minutes': str(max_eta),
                'min_eta_minutes': str(min_eta),
                'surge_minimum_order': minimum_order,
            },
        }
        assert offer_additional_info['params'] == {
            'lat_lon': location_str,
            'depot_id': legacy_depot_id,
        }
        assert offer_additional_info['user_id'] == user_id

    json = {'position': keys.DEFAULT_POSITION, 'items': []}

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json=json,
        headers={**TAXI_HEADERS, **{'X-YaTaxi-UserId': user_id}},
    )

    assert response.status_code == 200
    assert yt_offer_additional_info.times_called == 1


@pytest.mark.now(keys.TS_NOW)
async def test_additional_offer_info_log_native_surge(
        taxi_grocery_cart,
        experiments3,
        pgsql,
        overlord_catalog,
        offers,
        grocery_surge,
        umlaas_eta,
        testpoint,
        grocery_depots,
):
    user_id = '123456abcd'

    delivery_cost = '100'
    next_delivery_cost = '50'
    next_delivery_threshold = '350'
    min_eta = 20
    max_eta = 10
    minimum_order = '300'

    depot_id = '100'
    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_location(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        min_eta=str(min_eta),
        max_eta=str(max_eta),
        minimum_order=minimum_order,
        delivery={
            'cost': delivery_cost,
            'next_cost': next_delivery_cost,
            'next_threshold': next_delivery_threshold,
        },
        depot_id=depot_id,
        offer_time=keys.TS_NOW,
        is_surge=True,
    )

    location_str = (
        str(float(keys.DEFAULT_DEPOT_LOCATION[1]))
        + ';'
        + str(float(keys.DEFAULT_DEPOT_LOCATION[0]))
    )

    @testpoint('yt_offer_additional_info')
    def yt_offer_additional_info(offer_additional_info):
        assert offer_additional_info['version'] == 1
        assert offer_additional_info['offer_id'] == str(
            offers.created_times - 1,
        )
        assert offer_additional_info['doc'] == {
            'active_zone': 'foot',
            'foot': {
                'delivery_cost': delivery_cost,
                'delivery_conditions': [
                    {
                        'delivery_cost': delivery_cost,
                        'order_cost': minimum_order,
                    },
                    {
                        'delivery_cost': next_delivery_cost,
                        'order_cost': next_delivery_threshold,
                    },
                ],
                'is_surge': True,
                'is_manual': False,
                'next_delivery_cost': next_delivery_cost,
                'next_delivery_threshold': next_delivery_threshold,
                'max_eta_minutes': str(max_eta),
                'min_eta_minutes': str(min_eta),
                'surge_minimum_order': minimum_order,
            },
        }
        assert offer_additional_info['params'] == {
            'lat_lon': location_str,
            'depot_id': depot_id,
        }
        assert offer_additional_info['user_id'] == user_id

    json = {'position': keys.DEFAULT_POSITION, 'items': []}

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json=json,
        headers={**TAXI_HEADERS, **{'X-YaTaxi-UserId': user_id}},
    )

    assert response.status_code == 200
    assert yt_offer_additional_info.times_called == 1


def _disable_surge_for_newbies(experiments3, config_name):
    experiments3.add_config(
        name=config_name,
        consumers=['grocery-surge-client/surge'],
        clauses=[
            {
                'title': 'No surge for newbies',
                'predicate': {
                    'init': {
                        'arg_name': 'user_orders_completed',
                        'arg_type': 'int',
                        'value': 0,
                    },
                    'type': 'eq',
                },
                'value': {'surge': False},
            },
        ],
        default_value={'surge': True},
    )


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_cart_get_offer_and_surge_native': {
            'tag': 'total_paid_orders_count',
        },
    },
)
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.parametrize(
    'user_orders_count, card_orders_count, is_surge',
    [(10, None, True), (None, 10, True), (0, 0, False), (None, None, False)],
)
async def test_user_orders_count_is_passed_to_surge(
        taxi_grocery_cart,
        experiments3,
        pgsql,
        overlord_catalog,
        offers,
        grocery_surge,
        umlaas_eta,
        grocery_marketing,
        user_orders_count,
        card_orders_count,
        is_surge,
        grocery_depots,
):
    _disable_surge_for_newbies(experiments3, 'grocery-p13n-surge')

    if user_orders_count is not None:
        grocery_marketing.add_user_tag(
            'total_paid_orders_count',
            user_orders_count,
            user_id=HEADER_YANDEX_UID,
        )

    payment_id = '1'

    if card_orders_count is not None:
        grocery_marketing.add_payment_id_tag(
            'total_paid_orders_count',
            card_orders_count,
            payment_id=payment_id,
        )

    depot_id = '100'
    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_location(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )

    grocery_surge.add_record(
        legacy_depot_id=depot_id,
        timestamp=keys.TS_NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    position = keys.DEFAULT_POSITION

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={'position': position, 'items': []},
        headers=HEADERS_WITH_YANDEX_UID,
    )
    assert response.status_code == 200
    assert grocery_marketing.retrieve_v2_times_called == 1

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-payment',
        json={
            'position': position,
            'cart_id': response.json()['cart_id'],
            'payment_method': {'type': 'card', 'id': payment_id},
            'cart_version': response.json()['cart_version'],
        },
        headers=HEADERS_WITH_YANDEX_UID,
    )

    assert response.status_code == 200
    assert response.json()['is_surge'] == is_surge
    assert grocery_marketing.retrieve_v2_times_called == 2


# рубли округляются до целого числа. Во всех случаях цена из оверлорда
# превратится в 50 если в запросе цена не 50, то будет diff_data
@pytest.mark.parametrize(
    'has_price_mismatch,overlord_price,request_price',
    [(True, '50.7', '50.7'), (True, '50', '50.7'), (False, '50.7', '50')],
)
async def test_overlord_price_round(
        overlord_catalog,
        cart,
        has_price_mismatch,
        overlord_price,
        request_price,
):
    item_id = 'item_id_1'
    overlord_catalog.add_product(
        product_id=item_id, price=overlord_price, in_stock='10',
    )

    response = await cart.modify({item_id: {'q': 1, 'p': request_price}})
    if has_price_mismatch:
        assert response['diff_data']['products'][0]['product_id'] == item_id
    else:
        assert response['available_for_checkout'] is True


# проверяем повышение цен согласно эксперименту grocery_price_rise_map
# повышающий коэфициент = 3
@experiments.GROCERY_PRICE_RISE_MAP
async def test_price_rise_map(overlord_catalog, cart):
    item_id = 'item_id_1'
    overlord_catalog.add_product(product_id=item_id, price='10', in_stock='10')

    response = await cart.modify({item_id: {'q': 1, 'p': '30'}})
    assert response['available_for_checkout'] is True
    assert response['items'][0]['catalog_price'] == '30'
    assert (
        response['items'][0]['catalog_price_template'] == '30 $SIGN$$CURRENCY$'
    )
    assert (
        response['items'][0]['catalog_total_price_template']
        == '30 $SIGN$$CURRENCY$'
    )


@pytest.mark.parametrize('is_has_gross_weight', [True, False])
async def test_heavy_cart(
        experiments3, cart, overlord_catalog, is_has_gross_weight,
):
    experiments.set_heavy_cart_settings(experiments3, True)

    measurements = {'width': 1, 'height': 2, 'depth': 3, 'net_weight': 3}
    if is_has_gross_weight:
        measurements['gross_weight'] = 3

    item_id = 'item_id_1'
    price = '10'

    overlord_catalog.add_product(
        product_id=item_id, price=price, measurements=measurements,
    )

    await cart.modify({item_id: {'q': 1, 'p': price}})
    response = await cart.modify({item_id: {'q': 3, 'p': price}})
    assert not response['available_for_checkout']
    assert response['checkout_unavailable_reason'] == 'too_heavy_cart'


# Проверяем, что возвращаем флаг есть ли замены для товара, если
# товара нет в наличии, если товар есть в наличии флаг не возвращается
@pytest.mark.parametrize(
    'product_substitutions,has_substitutions',
    [
        pytest.param(
            ['product-2', 'product-3'], True, id='with_substitutions',
        ),
        pytest.param([], False, id='no_substitutions'),
    ],
)
async def test_substitutions(
        cart,
        overlord_catalog,
        grocery_upsale,
        product_substitutions,
        has_substitutions,
):
    item_1 = 'item_1'
    item_2 = 'item_2'
    quantity = 1
    price = '345'

    overlord_catalog.add_product(product_id=item_1, price=price, in_stock='0')
    overlord_catalog.add_product(product_id=item_2, price=price, in_stock='1')
    grocery_upsale.add_product_substitutions(product_substitutions)

    response = await cart.modify(
        {
            item_1: {'q': quantity, 'p': price},
            item_2: {'q': quantity, 'p': '100'},
        },
    )
    products = response['diff_data']['products']
    assert products[0]['has_substitutions'] == has_substitutions
    assert 'has_substitutions' not in products[1]


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(taxi_grocery_cart, user_api, has_personal_phone_id):
    headers = copy.deepcopy(HEADERS_WITH_YANDEX_UID)
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'items': [],
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)


@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG_PROD
@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize('headers', [TAXI_HEADERS, EDA_HEADERS, EDA_HEADERS_2])
async def test_goal_reward(
        taxi_grocery_cart,
        mockserver,
        pgsql,
        headers,
        offers,
        experiments3,
        grocery_surge,
        overlord_catalog,
        grocery_p13n,
):
    item_id_with_suffix = 'item_id_1:st-gr'
    item_price = '0'
    item_count = '1'

    offer_id = 'some_offer_id'
    common.create_offer(offers, experiments3, grocery_surge, offer_id=offer_id)

    overlord_catalog.add_product(
        product_id=item_id_with_suffix, price=item_price, in_stock=item_count,
    )

    @mockserver.json_handler(
        '/grocery-goals/internal/v1/goals/v1/check/sku-rewards',
    )
    def mock_grocery_goals(request):
        assert request.json['skus'] == [item_id_with_suffix]
        return {'available': True}

    item = {
        'id': item_id_with_suffix,
        'price': item_price,
        'quantity': '1',
        'currency': 'RUB',
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update',
        json={
            'position': keys.DEFAULT_POSITION,
            'offer_id': offer_id,
            'items': [item],
        },
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json['items']) == 1
    response_item = response_json['items'][0]
    assert response_item == {
        'id': item_id_with_suffix,
        'price': item_price,
        'catalog_price': item_price,
        'catalog_price_template': f'{item_price} $SIGN$$CURRENCY$',
        'catalog_total_price_template': f'{item_price} $SIGN$$CURRENCY$',
        'currency': 'RUB',
        'quantity': '1',
        'quantity_limit': item_count,
        'title': f'title for {item_id_with_suffix}',
        'subtitle': f'subtitle for {item_id_with_suffix}',
        'image_url_template': f'url for {item_id_with_suffix}',
        'image_url_templates': [f'url for {item_id_with_suffix}'],
        'restrictions': [],
    }

    cart_id = response_json['cart_id']
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        f'SELECT item_id, price, quantity, currency, status '
        f'FROM cart.cart_items WHERE cart_id::text=\'{cart_id}\'',
    )
    items = list(cursor)
    assert len(items) == 1, items
    pg_item = items[0]
    assert pg_item[0] == item['id']
    assert pg_item[1] == decimal.Decimal(item['price'])
    assert pg_item[2] == decimal.Decimal(item['quantity'])
    assert pg_item[3] == item['currency']
    assert pg_item[4] == 'in_cart'

    assert mock_grocery_goals.times_called == 1

    assert (
        response_json['order_flow_version'] == 'integration_no_payment_flow_v1'
    )
