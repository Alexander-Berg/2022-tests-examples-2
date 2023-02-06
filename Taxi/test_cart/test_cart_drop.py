BASIC_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Request-Language': 'en',
    'X-Request-Application': 'app_name=android',
}


async def test_basic(taxi_grocery_cart, pgsql):
    cart_id = '00000000-0000-0000-0000-000000000001'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/drop',
        headers=BASIC_HEADERS,
        json={'cart_id': cart_id},
    )
    assert response.status_code == 200

    db = pgsql['grocery_cart']
    cursor = db.cursor()
    cursor.execute('SELECT * FROM cart.carts')
    carts = list(cursor)
    assert not carts
    cursor.execute('SELECT * FROM cart.cart_items')
    cart_items = list(cursor)
    assert not cart_items


async def test_two_carts(taxi_grocery_cart, pgsql):
    cart_id = '00000000-0000-0000-0000-000000000001'

    other_cart_id = '00000000-0000-0000-0000-000000000002'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/drop',
        headers=BASIC_HEADERS,
        json={'cart_id': cart_id},
    )
    assert response.status_code == 200

    db = pgsql['grocery_cart']
    cursor = db.cursor()
    cursor.execute('SELECT * FROM cart.carts')
    carts = list(cursor)
    assert len(carts) == 1
    assert carts[0][0] == other_cart_id

    cursor.execute('SELECT * FROM cart.cart_items')
    cart_items = list(cursor)
    assert len(cart_items) == 2
    for cart_item in cart_items:
        assert cart_item[0] == other_cart_id


async def test_no_cart(taxi_grocery_cart, pgsql):
    cart_id = '00000000-0000-0000-0000-000000000001'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/drop',
        headers=BASIC_HEADERS,
        json={'cart_id': cart_id},
    )
    assert response.status_code == 404


async def test_checked_out_cart(taxi_grocery_cart, pgsql):
    cart_id = '00000000-0000-0000-0000-000000000001'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/drop',
        headers=BASIC_HEADERS,
        json={'cart_id': cart_id},
    )
    assert response.status_code == 404

    db = pgsql['grocery_cart']
    cursor = db.cursor()
    cursor.execute('SELECT * FROM cart.carts')
    carts = list(cursor)
    assert carts
    cursor.execute('SELECT * FROM cart.cart_items')
    cart_items = list(cursor)
    assert cart_items


async def test_empty_cart(taxi_grocery_cart, pgsql):
    cart_id = '00000000-0000-0000-0000-000000000001'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/drop',
        headers=BASIC_HEADERS,
        json={'cart_id': cart_id},
    )
    assert response.status_code == 200

    db = pgsql['grocery_cart']
    cursor = db.cursor()
    cursor.execute('SELECT * FROM cart.carts')
    carts = list(cursor)
    assert not carts
