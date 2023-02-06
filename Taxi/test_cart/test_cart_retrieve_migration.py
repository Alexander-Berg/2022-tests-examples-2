import pytest

ZUSER_ID_HASH = 'z0000000000000000000000000000000'
ZUSER_ID = 'taxi:' + ZUSER_ID_HASH
AUTHORIZED_USER_ID = '11111111111111111111111111111111'
EATS_USER_ID = '12345'
ZUSER_HEADERS = {
    'X-YaTaxi-Session': ZUSER_ID,
    'X-Idempotency-Token': 'zuser-idempotency',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}
AUTH_HEADERS_TAXI = {
    'X-YaTaxi-Session': 'taxi:' + AUTHORIZED_USER_ID,
    'X-Idempotency-Token': 'auth-idempotency',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-Yandex-UID': 'some_uid',
}
AUTH_HEADERS_EATS = {
    'X-YaTaxi-Session': 'eats:' + AUTHORIZED_USER_ID,
    'X-Idempotency-Token': 'auth-idempotency',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}
AUTH_HEADERS = {
    'X-YaTaxi-User': f'eats_user_id={EATS_USER_ID}',
    **AUTH_HEADERS_TAXI,
}
AUTH_HEADERS_EATS_SESSION = {
    'X-YaTaxi-User': f'eats_user_id={EATS_USER_ID}',
    **AUTH_HEADERS_EATS,
}
AUTH_HEADERS_NO_EATS_USER = {**AUTH_HEADERS_TAXI}
SA_BOUND_USER_HEADERS = {'X-YaTaxi-Bound-Sessions': ZUSER_ID}
PA_BOUND_USER_HEADERS = {'X-YaTaxi-Bound-UserIds': ZUSER_ID_HASH}


async def test_migration_by_id(cart_factory, overlord_catalog):
    overlord_catalog.add_product(product_id='item1', price='345')

    zuser_cart = cart_factory(headers=ZUSER_HEADERS)
    await zuser_cart.modify({'item1': {'q': 1, 'p': '345'}})

    user_cart = cart_factory(
        cart_id=zuser_cart.cart_id,
        cart_version=zuser_cart.cart_version,
        headers=AUTH_HEADERS,
    )

    with pytest.raises(user_cart.HttpError) as exc:
        await user_cart.retrieve()
    assert exc.value.status_code == 404

    await user_cart.retrieve(headers=SA_BOUND_USER_HEADERS)

    cart = user_cart.fetch_db()
    assert cart.user_type == 'eats_user_id'
    assert cart.user_id == EATS_USER_ID


async def test_migration_by_user(cart_factory, overlord_catalog):
    overlord_catalog.add_product(product_id='item1', price='345')

    zuser_cart = cart_factory(headers=ZUSER_HEADERS)
    await zuser_cart.modify({'item1': {'q': 1, 'p': '345'}})

    user_cart = cart_factory(headers=AUTH_HEADERS)

    with pytest.raises(user_cart.HttpError) as exc:
        await user_cart.retrieve()
    assert exc.value.status_code == 404

    await user_cart.retrieve(headers=SA_BOUND_USER_HEADERS)

    cart = user_cart.fetch_db()
    assert cart.user_type == 'eats_user_id'
    assert cart.user_id == EATS_USER_ID


async def test_retrieve_priority(cart_factory, pgsql):
    user_cart = cart_factory(headers=AUTH_HEADERS_EATS_SESSION)
    cart = await user_cart.retrieve(headers=SA_BOUND_USER_HEADERS)
    # z-user matched first
    assert cart['cart_id'] == '22222222-2222-2222-2222-222222222222'

    cursor = pgsql['grocery_cart'].cursor()
    cursor.execute(
        'DELETE FROM cart.carts where cart_id=%s', (user_cart.cart_id,),
    )

    user_cart = cart_factory(headers=AUTH_HEADERS_EATS_SESSION)
    cart = await user_cart.retrieve(headers=SA_BOUND_USER_HEADERS)

    assert cart['cart_id'] == '11111111-1111-1111-1111-111111111111'


# Test for migration zuser+eats_id defined (bug LAVKABACKEND-1295)
async def test_migration_by_id_with_eats_id(cart_factory, overlord_catalog):
    overlord_catalog.add_product(product_id='item1', price='345')

    zuser_cart = cart_factory(headers={**ZUSER_HEADERS})
    await zuser_cart.modify({'item1': {'q': 1, 'p': '345'}})

    user_cart = cart_factory(
        cart_id=zuser_cart.cart_id,
        cart_version=zuser_cart.cart_version,
        headers={**AUTH_HEADERS, 'X-YaTaxi-Session': ZUSER_ID},
    )

    await user_cart.retrieve()

    cart = user_cart.fetch_db()
    assert cart.user_type == 'eats_user_id'
    assert cart.user_id == EATS_USER_ID


@pytest.mark.parametrize('disable_migration', [None, True, False])
async def test_has_migration_not_checked_out(
        cart_factory, overlord_catalog, testpoint, disable_migration,
):
    @testpoint('has_cart_migration')
    def has_cart_migration(data):
        pass

    @testpoint('no_cart_migration')
    def no_cart_migration(data):
        pass

    overlord_catalog.add_product(product_id='item1', price='345')

    zuser_cart = cart_factory(headers={**ZUSER_HEADERS})
    await zuser_cart.modify({'item1': {'q': 1, 'p': '345'}})

    zuser_cart_db = zuser_cart.fetch_db()

    cart = cart_factory(
        cart_id=zuser_cart.cart_id,
        cart_version=zuser_cart.cart_version,
        headers={**AUTH_HEADERS, 'X-YaTaxi-Session': ZUSER_ID},
    )

    await cart.retrieve(
        allow_checked_out=True,
        disable_migration=disable_migration,
        headers={**AUTH_HEADERS, 'X-YaTaxi-Session': ZUSER_ID},
    )

    cart_db = cart.fetch_db()
    assert (zuser_cart_db.user_type == cart_db.user_type) == (
        disable_migration is True
    )

    assert no_cart_migration.has_calls == (disable_migration is True)
    assert has_cart_migration.times_called == (disable_migration is not True)


async def test_no_migration_checked_out(
        cart_factory, overlord_catalog, testpoint,
):
    @testpoint('has_cart_migration')
    def has_cart_migration(data):
        pass

    @testpoint('no_cart_migration')
    def no_cart_migration(data):
        pass

    overlord_catalog.add_product(product_id='item1', price='345')

    zuser_cart = cart_factory(headers={**ZUSER_HEADERS})
    await zuser_cart.modify({'item1': {'q': 1, 'p': '345'}})

    await zuser_cart.checkout(headers={**ZUSER_HEADERS})

    zuser_cart_db = zuser_cart.fetch_db()

    cart = cart_factory(
        cart_id=zuser_cart.cart_id,
        cart_version=zuser_cart.cart_version,
        headers={**AUTH_HEADERS, 'X-YaTaxi-Session': ZUSER_ID},
    )

    await cart.retrieve(
        allow_checked_out=True,
        headers={**AUTH_HEADERS, 'X-YaTaxi-Session': ZUSER_ID},
    )

    cart_db = cart.fetch_db()
    assert zuser_cart_db.user_type == cart_db.user_type
    assert zuser_cart_db.user_id == cart_db.user_id

    assert no_cart_migration.times_called == 1
    assert has_cart_migration.times_called == 0


# Test for retrieve by yandex_uid
async def test_migration_by_yandex_uid(cart_factory, overlord_catalog):
    overlord_catalog.add_product(product_id='item1', price='345')

    some_user_cart = cart_factory(
        headers={**AUTH_HEADERS_TAXI, 'X-YaTaxi-Session': 'random_session'},
    )
    await some_user_cart.modify({'item1': {'q': 1, 'p': '345'}})

    cart_result = await some_user_cart.retrieve(
        allow_checked_out=True,
        headers={
            **AUTH_HEADERS_NO_EATS_USER,
            'X-YaTaxi-Session': 'another_random_session',
        },
    )

    assert some_user_cart.cart_id == cart_result['cart_id']
