from tests_grocery_cart import common


async def test_refund(taxi_grocery_cart, cart, overlord_catalog):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    item_id_3 = 'item_id_3'
    quantity = 10

    price = '345'
    overlord_catalog.add_product(product_id=item_id_1, price=price)
    overlord_catalog.add_product(product_id=item_id_2, price=price)
    overlord_catalog.add_product(product_id=item_id_3, price=price)

    await cart.modify(
        {
            item_id_1: {'q': quantity, 'p': price},
            item_id_2: {'q': quantity, 'p': price},
            item_id_3: {'q': quantity, 'p': price},
        },
    )
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/refund',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': cart.cart_id,
            'item_refunds': [
                {'item_id': item_id_1, 'refunded_quantity': '1'},
                {'item_id': item_id_3, 'refunded_quantity': '5'},
            ],
        },
    )

    assert response.status_code == 200

    items = cart.fetch_items()
    assert items[0].refunded_quantity == 1
    assert items[1].refunded_quantity == 0
    assert items[2].refunded_quantity == 5


async def test_cart_not_found(taxi_grocery_cart, cart, overlord_catalog):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity = 10
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

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/refund',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': '00000000-0000-0000-0000-000000000000',
            'item_refunds': [{'item_id': item_id_1, 'refunded_quantity': '1'}],
        },
    )

    assert response.status_code == 404

    items = cart.fetch_items()
    for item in items:
        assert item.refunded_quantity == 0


async def test_idempotency(taxi_grocery_cart, cart, overlord_catalog):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity = 10
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

    async def refund():
        return await taxi_grocery_cart.post(
            '/internal/v1/cart/refund',
            headers=common.TAXI_HEADERS,
            json={
                'cart_id': cart.cart_id,
                'item_refunds': [
                    {'item_id': item_id_1, 'refunded_quantity': '2'},
                ],
            },
        )

    response1 = await refund()

    assert response1.status_code == 200

    items = cart.fetch_items()
    assert items[0].refunded_quantity == 2
    assert items[1].refunded_quantity == 0

    response2 = await refund()

    assert response2.status_code == 200

    items = cart.fetch_items()
    assert items[0].refunded_quantity == 2
    assert items[1].refunded_quantity == 0


async def test_refund_quantity_too_big(
        taxi_grocery_cart, cart, overlord_catalog,
):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    item_id_3 = 'item_id_3'
    quantity = 10

    price = '345'
    overlord_catalog.add_product(product_id=item_id_1, price=price)
    overlord_catalog.add_product(product_id=item_id_2, price=price)
    overlord_catalog.add_product(product_id=item_id_3, price=price)

    await cart.modify(
        {
            item_id_1: {'q': quantity, 'p': price},
            item_id_2: {'q': quantity, 'p': price},
            item_id_3: {'q': quantity, 'p': price},
        },
    )
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/refund',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': cart.cart_id,
            'item_refunds': [
                {'item_id': item_id_1, 'refunded_quantity': '1'},
                {'item_id': item_id_3, 'refunded_quantity': '11'},
            ],
        },
    )

    assert response.status_code == 400

    items = cart.fetch_items()
    assert items[0].refunded_quantity == 0
    assert items[1].refunded_quantity == 0
    assert items[2].refunded_quantity == 0


async def test_invalid_item_id(taxi_grocery_cart, cart, overlord_catalog):
    item_id_1 = 'item_id_1'
    item_id_2 = 'item_id_2'
    quantity = 10
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

    non_existing_item = 'i_do_not_exist'
    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/refund',
        headers=common.TAXI_HEADERS,
        json={
            'cart_id': cart.cart_id,
            'item_refunds': [
                {'item_id': item_id_1, 'refunded_quantity': '1'},
                {'item_id': non_existing_item, 'refunded_quantity': '5'},
            ],
        },
    )

    assert response.status_code == 400

    items = cart.fetch_items()
    for item in items:
        assert item.refunded_quantity == 0
