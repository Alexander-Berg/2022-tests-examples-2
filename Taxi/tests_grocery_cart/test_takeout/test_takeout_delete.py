import pytest


YANDEX_UID = 'some_uid'

BASIC_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-Session': 'taxi:1234',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Yandex-UID': YANDEX_UID,
}


async def _do_delete(taxi_grocery_cart, yandex_uid):
    response = await taxi_grocery_cart.post(
        '/internal/v1/takeout/delete', json={'yandex_uid': yandex_uid},
    )
    assert response.status_code == 200


async def _setup_cart(cart, overlord_catalog):
    item_id = 'some_item_id'
    price = '10'
    quantity = '1'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=quantity,
    )
    await cart.modify({item_id: {'q': quantity, 'p': price}})
    cart.update_db({'yandex_uid': YANDEX_UID})


async def test_basic(taxi_grocery_cart, cart, overlord_catalog):
    await _setup_cart(cart, overlord_catalog)
    response = await cart.retrieve(headers=BASIC_HEADERS)
    assert response

    await _do_delete(taxi_grocery_cart, YANDEX_UID)

    with pytest.raises(Exception):
        await cart.retrieve(headers=BASIC_HEADERS)


async def test_dont_delete_checked_out_carts(
        taxi_grocery_cart, cart, overlord_catalog,
):
    await _setup_cart(cart, overlord_catalog)
    await cart.checkout()

    response = await cart.retrieve(
        headers=BASIC_HEADERS, allow_checked_out=True,
    )
    assert response

    await _do_delete(taxi_grocery_cart, YANDEX_UID)

    response = await cart.retrieve(
        headers=BASIC_HEADERS, allow_checked_out=True,
    )
    assert response
