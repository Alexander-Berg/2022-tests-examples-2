import pytest

URL = '/pro-contractor/v1/income/chart/v1'
NOW = '2022-06-01T00:00:00+03'


@pytest.mark.now(NOW)
async def test_chart_post(taxi_driver_money, load_json):
    response = await taxi_driver_money.post(
        URL,
        json={
            'tz': 'Europe/Moscow',
            'income_type_id': 'market_courier',
            'group_by': 'day',
            'from': '2022-06-01T00:00:00+03',
            'to': '2022-06-01T00:00:00+03',
        },
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
