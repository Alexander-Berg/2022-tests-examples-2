import pytest

from tests_grocery_eats_gateway import headers


@pytest.mark.parametrize('status_code', [200, 404, 400])
async def test_basic(taxi_grocery_eats_gateway, grocery_orders, status_code):
    grocery_orders.set_open_rover_response(status_code=status_code)
    response = await taxi_grocery_eats_gateway.post(
        '/orders/v1/open_rover?order_id=order-id',
        headers=headers.DEFAULT_HEADERS,
    )

    assert grocery_orders.open_rover_times_called() == 1
    assert response.status_code == status_code

    if status_code == 400:
        assert response.json()['message'] == 'Bad request'
