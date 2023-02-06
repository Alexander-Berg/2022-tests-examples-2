import pytest


async def test_save_payment_method(cart, fetch_cart):
    await cart.init(['test_item'])

    cart_payment_type = 'card'
    await cart.set_payment(cart_payment_type)

    request_payment_id = 'request_payment_id-123'

    response = await cart.checkout(
        payment_method={'type': cart_payment_type, 'id': request_payment_id},
        order_flow_version='eats_payments',
    )

    assert 'checkout_unavailable_reason' not in response

    cart_from_pg = fetch_cart(cart.cart_id)

    assert cart_from_pg.payment_method_type == cart_payment_type
    assert cart_from_pg.payment_method_id == request_payment_id

    assert response['payment_method'] == {
        'type': cart_payment_type,
        'id': request_payment_id,
    }


# Для некоторых методов оплаты нормально не знать payment_id
# в момент cart/set-payment (потому что надо показать face id итд итп),
# поэтому фронт может прислать к нам что угодно,
# и на чекауте мы должны перезаписать то, что лежит в базе.
@pytest.mark.parametrize(
    'cart_payment_type', ['applepay', 'googlepay', 'cibus', 'sbp'],
)
async def test_another_payment_id_for_token_payment(
        cart, fetch_cart, cart_payment_type,
):
    await cart.init(['test_item'])

    cart_payment_id = 'cart_payment_id-123'
    await cart.set_payment(cart_payment_type, payment_id=cart_payment_id)

    request_payment_id = 'request_payment_id-123'

    assert cart_payment_id != request_payment_id

    response = await cart.checkout(
        payment_method={'type': cart_payment_type, 'id': request_payment_id},
        order_flow_version='eats_payments',
    )

    assert 'checkout_unavailable_reason' not in response

    cart_from_pg = fetch_cart(cart.cart_id)

    assert cart_from_pg.payment_method_type == cart_payment_type
    assert cart_from_pg.payment_method_id == request_payment_id

    assert response['payment_method'] == {
        'type': cart_payment_type,
        'id': request_payment_id,
    }


# Если сменяется payment_id для этих способов оплат, то происходит что-то
# странное (пользователь вырал одну карту, а пытаемся зачекаутить с другой).
@pytest.mark.parametrize('cart_payment_type', ['card', 'corp'])
async def test_error_if_changes_payment_id_for_not_token_payment(
        cart, fetch_cart, cart_payment_type,
):
    await cart.init(['test_item'])

    cart_payment_id = 'cart_payment_id-123'
    await cart.set_payment(cart_payment_type, payment_id=cart_payment_id)

    request_payment_id = 'request_payment_id-123'

    assert cart_payment_id != request_payment_id

    response = await cart.checkout(
        payment_method={'type': cart_payment_type, 'id': request_payment_id},
        required_status_code=400,
        order_flow_version='eats_payments',
    )

    assert response['code'] == 'BAD_PAYMENT_METHOD'

    cart_from_pg = fetch_cart(cart.cart_id)

    # проверяем, что в базе лежит тоже, что и лежало
    assert cart_from_pg.payment_method_type == cart_payment_type
    assert cart_from_pg.payment_method_id == cart_payment_id


async def test_another_payment_type(cart, fetch_cart):
    await cart.init(['test_item'])

    cart_payment_type = 'card'
    request_payment_type = 'corp'

    assert cart_payment_type != request_payment_type

    await cart.set_payment(cart_payment_type)

    response = await cart.checkout(
        payment_method={'type': request_payment_type, 'id': 'id'},
        required_status_code=400,
        order_flow_version='eats_payments',
    )

    assert response['code'] == 'BAD_PAYMENT_METHOD'

    cart_from_pg = fetch_cart(cart.cart_id)

    # проверяем, что в базе лежит тоже, что и лежало
    assert cart_from_pg.payment_method_type == cart_payment_type
    assert cart_from_pg.payment_method_id is None


# тест проверяет, что в случае неудачного чекаута, мы не модифицируем метод
# оплаты в базе
@pytest.mark.parametrize('is_successful_checkout', [True, False])
async def test_do_nothing_in_case_of_unsuccessful_checkout(
        cart, fetch_cart, is_successful_checkout,
):
    await cart.init(['test_item'])

    cart_payment_type = 'corp'
    await cart.set_payment(cart_payment_type)

    if not is_successful_checkout:
        await cart.set_cashback_flow('gain')

    request_payment_id = 'request_payment_id-123'
    response = await cart.checkout(
        payment_method={'type': cart_payment_type, 'id': request_payment_id},
        order_flow_version='eats_payments',
    )

    cart_from_pg = fetch_cart(cart.cart_id)

    assert cart_from_pg.payment_method_type == cart_payment_type

    if not is_successful_checkout:
        # проверяем, что в базе лежит тоже, что и лежало
        assert 'checkout_unavailable_reason' in response

        assert cart_from_pg.payment_method_id is None
        assert 'payment_method' not in response
    else:
        assert 'checkout_unavailable_reason' not in response
        assert cart_from_pg.payment_method_id == request_payment_id
        assert response['payment_method']['id'] == request_payment_id


async def test_error_if_no_payment_in_cart(cart, fetch_cart):
    await cart.init(['test_item'])

    response = await cart.checkout(
        payment_method={'type': 'card', 'id': 'id'},
        required_status_code=400,
        order_flow_version='eats_payments',
    )

    assert response['code'] == 'BAD_PAYMENT_METHOD'

    cart_from_pg = fetch_cart(cart.cart_id)

    # проверяем, что в базе лежит тоже, что и лежало
    assert cart_from_pg.payment_method_type is None
    assert cart_from_pg.payment_method_id is None

    assert 'payment_method' not in response


async def test_ignore_payment_meta(cart, fetch_cart):
    await cart.init(['test_item'])

    cart_payment_type = 'card'
    cart_payment_meta = {}
    await cart.set_payment(cart_payment_type, payment_meta=cart_payment_meta)

    response = await cart.checkout(
        payment_method={'type': cart_payment_type, 'id': 'qwe'},
        order_flow_version='eats_payments',
    )

    cart_from_pg = fetch_cart(cart.cart_id)

    assert cart_from_pg.payment_method_meta == cart_payment_meta

    assert response['payment_method']['meta'] == cart_payment_meta
