import pytest


@pytest.mark.config(CAR_CACHE_BRANDS_UPDATE_ENABLED=True)
@pytest.mark.parametrize(
    'brand,prefix_filter,expected_code,' 'expected_response',
    [
        (
            'DAEWOO',
            '',
            200,
            {
                'models': [
                    {'id': 'MATIZ', 'text': 'Matiz'},
                    {'id': 'NEXIA', 'text': 'Nexia'},
                ],
            },
        ),
        (
            'BMW',
            'e',
            200,
            {
                'models': [
                    {'id': 'E3', 'text': 'E3'},
                    {'id': 'E9', 'text': 'E9'},
                ],
            },
        ),
        (
            'BMW',
            '5',
            200,
            {
                'models': [
                    {'id': '501', 'text': '501'},
                    {'id': '502', 'text': '502'},
                    {'id': '503', 'text': '503'},
                    {'id': '507', 'text': '507'},
                ],
            },
        ),
        ('BMW', 'sdfsdfdsf', 200, {'models': []}),
        ('AUDI', '', 500, None),
    ],
)
def test_car_models(
        taxi_driver_protocol,
        brand,
        prefix_filter,
        expected_code,
        expected_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    response = taxi_driver_protocol.get(
        '/driver/car/models',
        params={
            'db': '777',
            'session': 'session_1',
            'brand': brand,
            'filter': prefix_filter,
        },
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        response_json = response.json()
        response_json['models'] = sorted(
            response_json['models'], key=lambda x: x['id'],
        )
        expected_response['models'] = sorted(
            expected_response['models'], key=lambda x: x['id'],
        )
        assert response_json == expected_response
