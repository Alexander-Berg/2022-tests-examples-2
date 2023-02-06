async def test_basic(taxi_grocery_wms_gateway):
    response = await taxi_grocery_wms_gateway.get(
        '/v1/ping', headers={'X-Yandex-UID': '1234'},
    )

    assert response.status_code == 200
