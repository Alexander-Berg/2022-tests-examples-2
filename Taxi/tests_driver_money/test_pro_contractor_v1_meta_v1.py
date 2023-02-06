import pytest

URL = '/pro-contractor/v1/meta/v1'
NOW = '2022-06-01T00:00:00+03'


@pytest.mark.now(NOW)
async def test_filtered_orders_post(taxi_driver_money, load_json):
    response = await taxi_driver_money.get(
        URL,
        params={'tz': 'Europe/Moscow'},
        headers={
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )

    import json
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
