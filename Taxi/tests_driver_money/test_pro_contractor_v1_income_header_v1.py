URL = '/pro-contractor/v1/income/header/v1'


async def test_header(taxi_driver_money, load_json):
    response = await taxi_driver_money.post(
        URL,
        json={'tz': 'Moscow/Europe', 'group_by': 'day'},
        headers={
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_header.json')
