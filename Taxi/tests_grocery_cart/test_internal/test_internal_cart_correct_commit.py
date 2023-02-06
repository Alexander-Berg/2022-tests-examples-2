import decimal

import pytest

from tests_grocery_cart import common


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
            cashback_to_pay=None,
            promocode_fixed_value=None,
            delete_before_checkout_item_ids=None,
    ):
        update_request = {}
        for item in init_items:
            item_id = item['item_id']
            quantity = item['quantity']
            price = item['price']

            update_request[item_id] = {'q': quantity, 'p': price}

            overlord_catalog.add_product(product_id=item_id, price=price)

        await cart.modify(update_request)

        if delete_before_checkout_item_ids:
            update_request = {}
            for item in init_items:
                item_id = item['item_id']
                quantity = (
                    '0'
                    if item_id in delete_before_checkout_item_ids
                    else item['quantity']
                )
                price = item['price']

                update_request[item_id] = {'q': quantity, 'p': price}

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

        json = {
            'cart_id': cart.cart_id,
            'correcting_cart_version': cart.cart_version,
            'correcting_items': correcting_items,
            'correcting_type': correcting_type,
        }

        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/copy',
            headers=common.TAXI_HEADERS,
            json=json,
        )
        assert response.status_code == 200
        child_cart_id = response.json()['child_cart_id']

        items_before_commit = fetch_items(child_cart_id)

        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/commit',
            headers=common.TAXI_HEADERS,
            json={
                'cart_id': cart.cart_id,
                'cart_version': cart.cart_version + 1,
                'correcting_type': correcting_type,
            },
        )
        assert response.status_code == 200

        cart_version = cart.cart_version + 2
        assert response.json() == {'cart_version': cart_version}

        updated_cart = cart.fetch_db()
        assert updated_cart.cart_version == cart_version
        assert updated_cart.status == 'checked_out'
        assert updated_cart.child_cart_id is None

        cart_items = cart.fetch_items()

        if result_items is not None:
            _check_items_after_commit(cart_items, result_items)

        # Check that all fields was copied
        assert items_before_commit == cart_items

    return _do


async def test_basic(_correct_cart, fetch_cart, cart):
    item_id = 'item-1'
    new_quantity = '1'

    await _correct_cart(
        init_items=[
            {'item_id': item_id, 'price': '100', 'quantity': '3'},
            {'item_id': 'item-2', 'price': '200', 'quantity': '2'},
        ],
        correcting_items=[{'item_id': item_id, 'new_quantity': new_quantity}],
        result_items=[
            {'item_id': item_id, 'price': '100', 'quantity': new_quantity},
            {'item_id': 'item-2', 'price': '200', 'quantity': '2'},
        ],
    )


async def test_idempotency(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = 2
    new_quantity = 1
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': cart.cart_id,
            'correcting_cart_version': cart.cart_version,
            'correcting_items': [
                {'item_id': item_id, 'new_quantity': str(new_quantity)},
            ],
        },
    )
    assert response.status_code == 200

    json = {'cart_id': cart.cart_id, 'cart_version': cart.cart_version}

    for _ in range(2):
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/commit',
            headers=common.TAXI_HEADERS,
            json=json,
        )
        assert response.status_code == 200

        cart_version = cart.cart_version + 1
        assert response.json() == {'cart_version': cart_version}


async def test_race_during_commit(
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

    json = {
        'cart_id': cart.cart_id,
        'correcting_cart_version': cart.cart_version,
        'correcting_items': [{'item_id': item_id, 'new_quantity': '1'}],
    }

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/copy',
        headers=common.TAXI_HEADERS,
        json=json,
    )
    assert response.status_code == 200

    make_race_call = True

    json = {'cart_id': cart.cart_id, 'cart_version': cart.cart_version}

    @testpoint('start_correct_commit')
    async def _start_correct_commit(data):
        nonlocal make_race_call

        if not make_race_call:
            return {}
        make_race_call = False

        race_headers = common.TAXI_HEADERS.copy()
        race_headers['X-Idempotency-Token'] = race_idempotency_token
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/correct/commit',
            headers=race_headers,
            json=json,
        )
        assert response.status_code == 200
        cart_version = cart.cart_version + 1
        assert response.json()['cart_version'] == cart_version

        updated_cart = cart.fetch_db()
        assert updated_cart.cart_version == cart_version

        return {}

    headers = common.TAXI_HEADERS.copy()
    headers['X-Idempotency-Token'] = idempotency_token

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/commit', headers=headers, json=json,
    )

    cart_version = cart.cart_version + 1
    assert response.status_code == 409

    updated_cart = cart.fetch_db()
    assert updated_cart.cart_version == cart_version


async def test_commit_not_copied_cart(
        taxi_grocery_cart, cart, overlord_catalog,
):
    item_id = 'item_id_1'
    quantity = 2
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    json = {'cart_id': cart.cart_id, 'cart_version': cart.cart_version}

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/commit',
        headers=common.TAXI_HEADERS,
        json=json,
    )
    assert response.status_code == 409


async def test_version_mismatched(taxi_grocery_cart, cart, overlord_catalog):
    item_id = 'item_id_1'
    quantity = 2
    price = '345'
    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    json = {'cart_id': cart.cart_id, 'cart_version': cart.cart_version + 1}

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/correct/commit',
        headers=common.TAXI_HEADERS,
        json=json,
    )
    assert response.status_code == 409


def _item_in_items_v2(item_id, quantity, items_v2):
    for item_v2 in items_v2:
        if (
                item_v2['info']['item_id'] == item_id
                and item_v2['sub_items'][0]['quantity'] == quantity
        ):
            return True

    return False


async def test_return_item_into_cart_after_checkout(_correct_cart, cart):
    item_id = 'item-1'
    quantity = '4'

    await _correct_cart(
        init_items=[
            {'item_id': item_id, 'price': '100', 'quantity': '3'},
            {'item_id': 'item-2', 'price': '200', 'quantity': '2'},
        ],
        correcting_items=[
            {
                'item_id': item_id,
                'new_quantity': quantity,
                'price': '100',
                'full_price': '100',
                'currency': 'RUB',
                'title': 'some_title',
                'vat': '20',
                'supplier_tin': 'supplier-tin',
            },
        ],
        correcting_type='add',
        result_items=[
            {'item_id': item_id, 'price': '100', 'quantity': quantity},
            {'item_id': 'item-2', 'price': '200', 'quantity': '2'},
        ],
        delete_before_checkout_item_ids=[item_id],
    )

    response = await cart.internal_retrieve_raw()

    items_v2 = response['items_v2']

    assert _item_in_items_v2(item_id, quantity, items_v2)
