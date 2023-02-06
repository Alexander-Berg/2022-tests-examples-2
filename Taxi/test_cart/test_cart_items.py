from tests_grocery_cart.plugins import keys

BASIC_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
}
TAXI_HEADERS = {
    **BASIC_HEADERS,
    'X-YaTaxi-Session': 'taxi:1234',
    'X-YaTaxi-User': 'eats_user_id=12345',
    'X-Yandex-UID': 'some_uid',
}


def ensure_cart_items_order(cart, *items):
    assert {item['id'] for item in cart['items']} == {*items}


async def test_order_preserved_modify(cart):
    ensure_cart_items_order(
        await cart.modify({'item2': {'q': 1, 'p': 345}}), 'item2',
    )
    ensure_cart_items_order(
        await cart.modify({'item1': {'q': 1, 'p': 345}}), 'item2', 'item1',
    )
    ensure_cart_items_order(
        await cart.modify({'item2': {'q': 2, 'p': 345}}), 'item2', 'item1',
    )
    ensure_cart_items_order(
        await cart.modify(
            {'item4': {'q': 1, 'p': '345'}, 'item3': {'q': 1, 'p': '345'}},
        ),
        'item2',
        'item1',
        'item3',
        'item4',
    )
    ensure_cart_items_order(
        await cart.modify({'item1': {'q': 0, 'p': 345}}),
        'item2',
        'item3',
        'item4',
    )
    ensure_cart_items_order(
        await cart.modify({'item1': {'q': 4, 'p': 345}}),
        'item2',
        'item3',
        'item4',
        'item1',
    )


async def test_order_preserved_retrieve(cart, taxi_grocery_cart):
    ensure_cart_items_order(
        await cart.modify({'item2': {'q': 2, 'p': 345}}), 'item2',
    )
    ensure_cart_items_order(
        await cart.modify(
            {'item4': {'q': 1, 'p': '345'}, 'item3': {'q': 1, 'p': '345'}},
        ),
        'item2',
        'item3',
        'item4',
    )

    request = {'position': {'location': keys.DEFAULT_DEPOT_LOCATION}}
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/retrieve', json=request, headers=TAXI_HEADERS,
    )
    ensure_cart_items_order(response.json(), 'item2', 'item3', 'item4')
