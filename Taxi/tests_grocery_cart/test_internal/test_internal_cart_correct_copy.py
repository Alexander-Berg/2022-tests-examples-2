# pylint: disable=too-many-lines
import copy
import decimal
import json

import pytest


from tests_grocery_cart import common
from tests_grocery_cart import experiments


SELECT_ALL_CART_FIELDS_SQL = """
SELECT * FROM cart.carts where cart_id = %s
"""

SELECT_ALL_CHECKOUT_FIELDS_SQL = """
SELECT * FROM cart.checkout_data where cart_id = %s
"""

SELECT_ALL_CART_ITEMS_FIELDS_SQL = """
SELECT * FROM cart.cart_items where cart_id = %s
"""

SET_ALL_CART_ITEMS_FIELDS_SQL = """
UPDATE cart.cart_items SET
    price = '123.34',
    quantity = '3',
    currency = 'RUB',
    full_price = '200.01',
    title = 'some title',
    reserved = '5',
    vat = '10.00',
    refunded_quantity = '5.00',
    cashback = '13.01',
    is_expiring = False,
    supplier_tin = 'supplier-tin'
WHERE cart_id = %s AND item_id = %s
"""

MUTABLE_CART_FIELDS = [
    'cart_id',
    'updated',
    'idempotency_token',
    'promocode_discount',
    'cashback_to_pay',
]


def _check_items_after_commit(cart_items, result_items):
    assert len(cart_items) == len(result_items)

    for cart_item in cart_items:
        found = False
        for result_item in result_items:
            if cart_item.item_id != result_item['item_id']:
                continue

            quantity = decimal.Decimal(result_item['quantity'])
            assert cart_item.quantity == quantity
            found = True
            break
        assert found, cart_item


def _get_promocode_discount(items_pricing):
    result = decimal.Decimal(0)

    for item in items_pricing['items']:
        for sub_item in item['sub_items']:
            result += decimal.Decimal(
                sub_item['paid_with_promocode'],
            ) * decimal.Decimal(sub_item['quantity'])

    return result


def _get_cashback_discount(items_pricing):
    result = decimal.Decimal(0)

    for item in items_pricing['items']:
        for sub_item in item['sub_items']:
            result += decimal.Decimal(
                sub_item['paid_with_cashback'],
            ) * decimal.Decimal(sub_item['quantity'])

    return result


@pytest.fixture
def _correct_cart(
        overlord_catalog,
        cart,
        taxi_grocery_cart,
        fetch_items,
        grocery_p13n,
        fetch_cart,
        eats_promocodes,
):
    async def _do(
            init_items,
            correcting_items,
            correcting_type=None,
            result_items=None,
            items_pricing_after_checkout=None,
            items_pricing_after_commit=None,
            cashback_to_pay=None,
            promocode_fixed_value=None,
    ):
        update_request = {}
        for item in init_items:
            item_id = item['item_id']
            quantity = item['quantity']
            price = item['price']

            update_request[item_id] = {'q': quantity, 'p': price}

            overlord_catalog.add_product(product_id=item_id, price=price)

        await cart.modify(update_request)

        if cashback_to_pay is not None:
            grocery_p13n.set_cashback_info_response(
                payment_available=True, balance='9999',
            )
            await cart.set_payment('card', 'card-x123')
            await cart.set_cashback_flow('charge')

        if promocode_fixed_value is not None:
            await cart.apply_promocode('test_code')

        response = await cart.checkout(
            cashback_to_pay=cashback_to_pay,
            order_flow_version='grocery_flow_v1',
        )
        assert 'checkout_unavailable_reason' not in response, response

        if items_pricing_after_checkout is not None:
            cart_pg = fetch_cart(cart.cart_id)
            assert (
                cart_pg.items_pricing.get('items')
                == items_pricing_after_checkout
            )

        request = {
            'cart_id': cart.cart_id,
            'correcting_cart_version': cart.cart_version,
            'correcting_items': correcting_items,
            'correcting_type': correcting_type,
        }

        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/copy',
            headers=common.TAXI_HEADERS,
            json=request,
        )
        assert response.status_code == 200
        child_cart_id = response.json()['child_cart_id']

        updated_cart = fetch_cart(child_cart_id)

        cart_version = cart.cart_version + 1

        assert updated_cart.cart_version == cart_version
        assert updated_cart.status == 'correcting'
        assert updated_cart.child_cart_id is None

        if items_pricing_after_commit is not None:
            assert (
                updated_cart.items_pricing.get('items')
                == items_pricing_after_commit
            )
            assert updated_cart.promocode_discount == _get_promocode_discount(
                updated_cart.items_pricing,
            )
            assert updated_cart.cashback_to_pay == _get_cashback_discount(
                updated_cart.items_pricing,
            )

    return _do


def _compare_checkout_data_with_child(
        pgsql, cart_id, child_cart_id, expected_values,
):
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(SELECT_ALL_CHECKOUT_FIELDS_SQL, (cart_id,))
    row = cursor.fetchone()

    cursor.execute(SELECT_ALL_CHECKOUT_FIELDS_SQL, (child_cart_id,))
    row_child = cursor.fetchone()

    if row is None or row_child is None:
        assert (
            False
        ), f'Checkout data for cart {cart_id} or {child_cart_id} not found'

    for [column, field, child_field] in zip(
            cursor.description, row, row_child,
    ):
        if field != child_field:
            if column.name == 'cart_version':
                assert int(field) == int(child_field) - 1
            elif column.name in expected_values:
                assert child_field == expected_values[column.name]
            else:
                assert column.name in MUTABLE_CART_FIELDS


def _compare_cart_with_child_cart(
        pgsql, cart_id, child_cart_id, expected_values,
):
    _compare_checkout_data_with_child(
        pgsql, cart_id, child_cart_id, expected_values,
    )
    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(SELECT_ALL_CART_FIELDS_SQL, (cart_id,))
    row = cursor.fetchone()

    cursor.execute(SELECT_ALL_CART_FIELDS_SQL, (child_cart_id,))
    row_child = cursor.fetchone()

    if row is None or row_child is None:
        assert False, f'Cart {cart_id} or {child_cart_id} not found'

    null_keys = []
    child_null_keys = []
    different_fields_keys = []

    for [column, field, child_field] in zip(
            cursor.description, row, row_child,
    ):
        if field is not None and child_field is None:
            child_null_keys += [column.name]

        if field is None or child_field is None:
            null_keys += [column.name]

        if field != child_field:
            different_fields_keys += [column.name]

    # child_cart_id and order_id are null
    child_null_keys = sorted(child_null_keys)
    assert child_null_keys == ['child_cart_id', 'order_id']

    # child_cart_id and order_id are null
    null_keys = sorted(null_keys)
    assert null_keys == ['child_cart_id', 'order_id']

    # child_cart_id, cart_id and status
    assert len(different_fields_keys) == 5, different_fields_keys
    different_fields_keys = sorted(different_fields_keys)
    # add fields here ONLY if they MUST NOT be copied (if not sure, DON'T)
    assert different_fields_keys == [
        'cart_id',
        'child_cart_id',
        'order_id',
        'status',
        'yandex_uid',
    ]

    # If fail, add new field to copy_cart_with_correcting_items.sql
    # and add not null values for this fields in conftest cart

    cursor.execute(SELECT_ALL_CART_ITEMS_FIELDS_SQL, (cart_id,))
    row = cursor.fetchone()

    cursor.execute(SELECT_ALL_CART_ITEMS_FIELDS_SQL, (child_cart_id,))
    row_child = cursor.fetchone()

    if row is None or row_child is None:
        raise RuntimeError(f'Cart {cart_id} or {child_cart_id} not found')

    null_keys = []
    different_fields_keys = []

    for [column, field, child_field] in zip(
            cursor.description, row, row_child,
    ):
        if field is None or child_field is None:
            null_keys += [column.name]

        if field != child_field:
            different_fields_keys += [column.name]

    assert not null_keys

    # quantity, cart_id, updated
    assert len(different_fields_keys) == 3
    different_fields_keys = sorted(different_fields_keys)
    assert different_fields_keys == ['cart_id', 'quantity', 'updated']

    # If fail, add new field to copy_cart_with_correcting_items.sql
    # and add not null values for this fields in mock cart


async def test_basic_copy(
        taxi_grocery_cart, cart, overlord_catalog, fetch_items,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity = 4
    new_quantity = 2
    price = '345'

    overlord_catalog.add_product(product_id=item_id_1, price=price)
    overlord_catalog.add_product(product_id=item_id_2, price=price)

    await cart.modify(
        {
            item_id_1: {'q': quantity, 'p': price},
            item_id_2: {'q': quantity, 'p': price},
        },
    )
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {'item_id': item_id_1, 'new_quantity': str(new_quantity)},
        ],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 200

    updated_cart = cart.fetch_db()
    cart_version = cart.cart_version + 1
    assert response.json() == {
        'cart_version': cart_version,
        'child_cart_id': updated_cart.child_cart_id,
    }

    assert updated_cart.cart_version == cart_version
    assert updated_cart.status == 'checked_out'

    # Original cart - nothing changed
    items = cart.fetch_items()
    assert len(items) == 2

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(quantity)

    item = items[1]
    assert item.item_id == item_id_2
    assert item.quantity == decimal.Decimal(quantity)

    # Copied cart - quantity changed
    child_cart_id = updated_cart.child_cart_id
    items = fetch_items(child_cart_id)
    assert len(items) == 2

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(new_quantity)

    item = items[1]
    assert item.item_id == item_id_2
    assert item.quantity == decimal.Decimal(quantity)


async def test_no_delete_item(
        taxi_grocery_cart, cart, overlord_catalog, fetch_items,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity = 4
    new_quantity = 2
    price = '345'

    overlord_catalog.add_product(product_id=item_id_1, price=price)
    overlord_catalog.add_product(product_id=item_id_2, price=price)

    await cart.modify(
        {
            item_id_1: {'q': quantity, 'p': price},
            item_id_2: {'q': quantity, 'p': price},
        },
    )
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {'item_id': item_id_1, 'new_quantity': str(new_quantity)},
            {'item_id': item_id_2, 'new_quantity': '0'},
        ],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 200

    updated_cart = cart.fetch_db()

    cart_version = cart.cart_version + 1
    assert response.json() == {
        'cart_version': cart_version,
        'child_cart_id': updated_cart.child_cart_id,
    }

    assert updated_cart.cart_version == cart_version
    assert updated_cart.status == 'checked_out'

    # Original cart - nothing changed
    items = cart.fetch_items()
    assert len(items) == 2

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(quantity)

    item = items[1]
    assert item.item_id == item_id_2
    assert item.quantity == decimal.Decimal(quantity)

    # Copied cart - quantity changed
    child_cart_id = updated_cart.child_cart_id
    items = fetch_items(child_cart_id)
    assert len(items) == 2

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(new_quantity)

    item = items[1]
    assert item.item_id == item_id_2
    assert item.quantity == decimal.Decimal('0')


async def test_add_quantity(
        taxi_grocery_cart, cart, overlord_catalog, fetch_items,
):
    item_id_1 = 'item_id_1'
    quantity = 4
    new_quantity = 6
    price = '345'

    overlord_catalog.add_product(product_id=item_id_1, price=price)

    await cart.modify({item_id_1: {'q': quantity, 'p': price}})
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {'item_id': item_id_1, 'new_quantity': str(new_quantity)},
        ],
        'correcting_type': 'add',
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 200

    updated_cart = cart.fetch_db()

    cart_version = cart.cart_version + 1
    assert response.json() == {
        'cart_version': cart_version,
        'child_cart_id': updated_cart.child_cart_id,
    }

    assert updated_cart.cart_version == cart_version
    assert updated_cart.status == 'checked_out'

    # Original cart - nothing changed
    items = cart.fetch_items()
    assert len(items) == 1

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(quantity)

    # Copied cart - quantity changed
    child_cart_id = updated_cart.child_cart_id
    items = fetch_items(child_cart_id)
    assert len(items) == 1

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(new_quantity)


async def test_add_new_item(
        taxi_grocery_cart, cart, overlord_catalog, fetch_items,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity_1 = 4
    new_quantity_2 = 3
    price = '345'

    overlord_catalog.add_product(product_id=item_id_1, price=price)

    await cart.modify({item_id_1: {'q': quantity_1, 'p': price}})
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {
                'item_id': item_id_2,
                'new_quantity': str(new_quantity_2),
                'price': price,
                'full_price': price,
                'currency': 'RUB',
                'title': 'title_2',
                'vat': '10.00',
            },
        ],
        'correcting_type': 'add',
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 200

    updated_cart = cart.fetch_db()

    cart_version = cart.cart_version + 1
    assert response.json() == {
        'cart_version': cart_version,
        'child_cart_id': updated_cart.child_cart_id,
    }

    assert updated_cart.cart_version == cart_version
    assert updated_cart.status == 'checked_out'

    # Original cart - nothing changed
    items = cart.fetch_items()
    assert len(items) == 1

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(quantity_1)

    # Copied cart - item added
    child_cart_id = updated_cart.child_cart_id
    items = fetch_items(child_cart_id)
    assert len(items) == 2

    item = items[0]
    assert item.item_id == item_id_1
    assert item.quantity == decimal.Decimal(quantity_1)

    item = items[1]
    assert item.item_id == item_id_2
    assert item.quantity == decimal.Decimal(new_quantity_2)


async def test_no_required_item_field(
        taxi_grocery_cart, cart, overlord_catalog,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity_1 = 4
    new_quantity_2 = 3
    price = '345'

    overlord_catalog.add_product(product_id=item_id_1, price=price)

    await cart.modify({item_id_1: {'q': quantity_1, 'p': price}})
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {'item_id': item_id_2, 'new_quantity': str(new_quantity_2)},
        ],
        'correcting_type': 'add',
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 400


async def test_new_item_when_removing(
        taxi_grocery_cart, cart, overlord_catalog,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity_1 = 4
    new_quantity_2 = 3
    price = '345'

    overlord_catalog.add_product(product_id=item_id_1, price=price)

    await cart.modify({item_id_1: {'q': quantity_1, 'p': price}})
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {'item_id': item_id_2, 'new_quantity': str(new_quantity_2)},
        ],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 400


async def test_copy_all_cart_fields(
        taxi_grocery_cart, cart, pgsql, overlord_catalog,
):
    item_id = 'item_id_1'
    quantity = 4
    new_quantity = 2
    price = '345'

    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    cart.update_db(
        cart_version=1,
        payment_method_type='google-pay',
        payment_method_id='1234',
        payment_method_meta='{}',
        idempotency_token='token123',
        status='checked_out',
        user_type='taxi',
        user_id='1345',
        promocode='promo123',
        delivery_type='pickup',
        cashback_flow='charge',
        delivery_cost='100',
        order_id='123456',
        personal_phone_id='personal-phone-id-123',
        tips_amount='5',
        tips_amount_type='absolute',
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        timeslot_request_kind=timeslot_request_kind,
        anonym_id='anonym_id',
    )

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(SET_ALL_CART_ITEMS_FIELDS_SQL, (cart.cart_id, item_id))

    initial_items_pricing = {
        'items': [
            {
                'item_id': 'item_id_1',
                'sub_items': [
                    {
                        'price': '260',
                        'item_id': 'item_id_1',
                        'quantity': '4',
                        'full_price': '345',
                        'paid_with_cashback': '40',
                        'paid_with_promocode': '45',
                    },
                ],
            },
        ],
        'share_policy': 'default',
    }

    cart.set_items_pricing(json.dumps(initial_items_pricing))

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [
            {'item_id': item_id, 'new_quantity': str(new_quantity)},
        ],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )

    assert response.status_code == 200

    orig_cart = cart.fetch_db()
    cart_version = cart.cart_version + 1
    assert response.json() == {
        'cart_version': cart_version,
        'child_cart_id': orig_cart.child_cart_id,
    }

    expected_items_pricing = copy.deepcopy(initial_items_pricing)

    expected_items_pricing['items'][0]['sub_items'][0]['quantity'] = '2'

    expected_values = {'items_pricing': expected_items_pricing}

    _compare_cart_with_child_cart(
        pgsql=pgsql,
        cart_id=orig_cart.cart_id,
        child_cart_id=orig_cart.child_cart_id,
        expected_values=expected_values,
    )


async def test_idempotency(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = 2
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [{'item_id': item_id, 'new_quantity': '1'}],
    }

    for _ in range(2):
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/copy',
            headers=common.TAXI_HEADERS,
            json=request,
        )
        assert response.status_code == 200

        orig_cart = cart.fetch_db()
        cart_version = cart.cart_version + 1
        assert response.json() == {
            'cart_version': cart_version,
            'child_cart_id': orig_cart.child_cart_id,
        }


async def test_race_during_copy(
        taxi_grocery_cart, cart, overlord_catalog, testpoint,
):
    item_id = 'item_id_1'
    quantity = 5
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    idempotency_token = 'edit-token'
    race_idempotency_token = 'edit-token-2'

    race_new_quantity = '4'
    request_new_quantity = '2'

    make_race_call = True

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
    }

    @testpoint('start_correct_copy')
    async def _start_correct_copy(data):
        nonlocal make_race_call

        if not make_race_call:
            return {}
        make_race_call = False

        request['correcting_items'] = [
            {'item_id': item_id, 'new_quantity': race_new_quantity},
        ]

        race_headers = common.TAXI_HEADERS.copy()
        race_headers['X-Idempotency-Token'] = race_idempotency_token
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/copy',
            headers=race_headers,
            json=request,
        )
        assert response.status_code == 200
        cart_version = cart.cart_version + 1
        assert response.json()['cart_version'] == cart_version

        updated_cart = cart.fetch_db()
        assert updated_cart.cart_version == cart_version

        return {}

    headers = common.TAXI_HEADERS.copy()
    headers['X-Idempotency-Token'] = idempotency_token
    request['correcting_items'] = [
        {'item_id': item_id, 'new_quantity': request_new_quantity},
    ]

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy', headers=headers, json=request,
    )

    cart_version = cart.cart_version + 1
    assert response.status_code == 409

    updated_cart = cart.fetch_db()
    assert updated_cart.cart_version == cart_version


async def test_correct_copy_not_checked_out_cart(
        taxi_grocery_cart, cart, overlord_catalog,
):
    item_id = 'item_id_1'
    quantity = 2
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [{'item_id': item_id, 'new_quantity': '1'}],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )
    assert response.status_code == 400


async def test_version_mismatched(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = 2
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    request = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version + 1,
        'correcting_items': [{'item_id': item_id, 'new_quantity': '1'}],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=request,
    )
    assert response.status_code == 409


@experiments.ITEMS_PRICING_ENABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'new_quantity_1, correcting_type',
    [
        pytest.param('0', None, id='full remove'),
        pytest.param('1', None, id='partial remove'),
        pytest.param('5', 'add', id='add quantity'),
    ],
)
async def test_items_pricing_with_cashback(
        _correct_cart, new_quantity_1, correcting_type,
):
    item_id_1 = 'item-1'
    item_id_2 = 'item-2'

    price_1 = '100'
    price_2 = '200'

    quantity_1 = '3'
    quantity_2 = '2'

    items_pricing_after_checkout = [
        {
            'item_id': item_id_1,
            'sub_items': [
                {
                    'full_price': price_1,
                    'item_id': f'{item_id_1}_0',
                    'paid_with_cashback': '20',
                    'paid_with_promocode': '0',
                    'price': '80',
                    'quantity': quantity_1,
                },
            ],
        },
        {
            'item_id': item_id_2,
            'sub_items': [
                {
                    'full_price': price_2,
                    'item_id': f'{item_id_2}_0',
                    'paid_with_cashback': '20',
                    'paid_with_promocode': '0',
                    'price': '180',
                    'quantity': quantity_2,
                },
            ],
        },
    ]

    items_pricing_after_commit = copy.deepcopy(items_pricing_after_checkout)

    assert items_pricing_after_commit[0]['item_id'] == item_id_1
    if correcting_type == 'add':
        items_pricing_after_commit[0]['sub_items'].append(
            copy.deepcopy(items_pricing_after_commit[0]['sub_items'][0]),
        )
        items_pricing_after_commit[0]['sub_items'][1]['quantity'] = str(
            int(new_quantity_1) - int(quantity_1),
        )
        items_pricing_after_commit[0]['sub_items'][1][
            'paid_with_promocode'
        ] = '0'
        items_pricing_after_commit[0]['sub_items'][1][
            'paid_with_cashback'
        ] = '0'
        items_pricing_after_commit[0]['sub_items'][1]['item_id'] = (
            item_id_1 + '_1'
        )
        items_pricing_after_commit[0]['sub_items'][1]['price'] = price_1
    else:
        items_pricing_after_commit[0]['sub_items'][0][
            'quantity'
        ] = new_quantity_1

    await _correct_cart(
        init_items=[
            {'item_id': item_id_1, 'price': '100', 'quantity': quantity_1},
            {'item_id': item_id_2, 'price': '200', 'quantity': quantity_2},
        ],
        correcting_items=[
            {'item_id': item_id_1, 'new_quantity': new_quantity_1},
        ],
        correcting_type=correcting_type,
        items_pricing_after_checkout=items_pricing_after_checkout,
        items_pricing_after_commit=items_pricing_after_commit,
        cashback_to_pay='100',
    )


@experiments.ITEMS_PRICING_ENABLED
@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.CASHBACK_GROCERY_ORDER_ENABLED
@pytest.mark.parametrize(
    'new_quantity_1, correcting_type',
    [
        pytest.param('0', None, id='full remove'),
        pytest.param('1', None, id='partial remove'),
        pytest.param('5', 'add', id='add quantity'),
    ],
)
async def test_items_pricing_with_promocode(
        _correct_cart, new_quantity_1, correcting_type, grocery_coupons,
):
    item_id_1 = 'item-1'
    item_id_2 = 'item-2'

    price_1 = '100'
    price_2 = '200'

    quantity_1 = '3'
    quantity_2 = '2'

    promocode_fixed_value = '140'

    items_pricing_after_checkout = [
        {
            'item_id': item_id_1,
            'sub_items': [
                {
                    'full_price': price_1,
                    'item_id': f'{item_id_1}_0',
                    'price': '80',
                    'paid_with_cashback': '0',
                    'paid_with_promocode': '20',
                    'quantity': quantity_1,
                },
            ],
        },
        {
            'item_id': item_id_2,
            'sub_items': [
                {
                    'full_price': price_2,
                    'item_id': f'{item_id_2}_0',
                    'price': '160',
                    'paid_with_cashback': '0',
                    'paid_with_promocode': '40',
                    'quantity': quantity_2,
                },
            ],
        },
    ]

    items_pricing_after_commit = copy.deepcopy(items_pricing_after_checkout)

    assert items_pricing_after_commit[0]['item_id'] == item_id_1
    if correcting_type == 'add':
        items_pricing_after_commit[0]['sub_items'].append(
            copy.deepcopy(items_pricing_after_commit[0]['sub_items'][0]),
        )
        items_pricing_after_commit[0]['sub_items'][1]['quantity'] = str(
            int(new_quantity_1) - int(quantity_1),
        )
        items_pricing_after_commit[0]['sub_items'][1][
            'paid_with_promocode'
        ] = '0'
        items_pricing_after_commit[0]['sub_items'][1][
            'paid_with_cashback'
        ] = '0'
        items_pricing_after_commit[0]['sub_items'][1]['item_id'] = (
            item_id_1 + '_1'
        )
        items_pricing_after_commit[0]['sub_items'][1]['price'] = price_1
    else:
        items_pricing_after_commit[0]['sub_items'][0][
            'quantity'
        ] = new_quantity_1

    grocery_coupons.set_check_response_custom(
        promocode_type='fixed', value=promocode_fixed_value,
    )

    await _correct_cart(
        init_items=[
            {'item_id': item_id_1, 'price': '100', 'quantity': quantity_1},
            {'item_id': item_id_2, 'price': '200', 'quantity': quantity_2},
        ],
        correcting_items=[
            {'item_id': item_id_1, 'new_quantity': new_quantity_1},
        ],
        correcting_type=correcting_type,
        items_pricing_after_checkout=items_pricing_after_checkout,
        items_pricing_after_commit=items_pricing_after_commit,
        promocode_fixed_value=promocode_fixed_value,
    )
