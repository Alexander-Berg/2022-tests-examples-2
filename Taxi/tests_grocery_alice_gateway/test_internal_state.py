# pylint: disable=import-error
from grocery_mocks.models import cart
# pylint: enable=import-error

YANDEX_UID = '1234567'
CART_ID = '6984f901-5fbf-4a29-8620-6e91561a7401'


async def test_basic(
        taxi_grocery_alice_gateway,
        pgsql,
        testpoint,
        grocery_cart,
        mockserver,
        load_json,
):
    @mockserver.json_handler(
        '/grocery-orders-tracking/internal/v1/orders-state',
    )
    def mock_state(request):
        assert request.json == {'yandex_uid': YANDEX_UID}
        return load_json('orders_tracking_response.json')

    grocery_cart.set_order_conditions(delivery_cost=10, max_eta=15)
    grocery_cart.add_cart(cart_id=CART_ID)
    grocery_cart.set_items(
        items=[
            cart.GroceryCartItem(item_id='id1', quantity='2'),
            cart.GroceryCartItem(item_id='id2', quantity='3'),
            cart.GroceryCartItem(item_id='id3', quantity='3'),
            cart.GroceryCartItem(item_id='id4', quantity='3'),
        ],
        cart_id=CART_ID,
    )

    response = await taxi_grocery_alice_gateway.post(
        '/internal/v1/orders/v1/state', json={'yandex_uid': YANDEX_UID},
    )

    assert mock_state.times_called == 1
    assert response.status_code == 200
