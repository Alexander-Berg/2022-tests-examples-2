from tests_grocery_dispatch import constants as const


async def test_check_price(taxi_grocery_dispatch, cargo):
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/check-price',
        {
            'depot_id': const.DEPOT_ID,
            'client_location': {'lat': 25.1, 'lon': 16.7},
        },
    )

    assert response.status == 200
    assert response.json()['price'] == 100
