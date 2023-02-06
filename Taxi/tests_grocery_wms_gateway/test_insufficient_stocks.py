async def test_basic(taxi_grocery_wms_gateway):
    response = await taxi_grocery_wms_gateway.post(
        '/v1/insufficient_stocks',
        json={
            'external_id': 'abcde0000f',
            'stocks': [
                {'product_id': 'lllll0012', 'available': 2, 'required': 5},
            ],
            'timestamp': '2020-02-17T11:46:35+03:00',
        },
    )

    assert response.status_code == 200
