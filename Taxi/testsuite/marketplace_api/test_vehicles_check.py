import pytest


@pytest.fixture
def tracker_response_classify_cars(mockserver):
    @mockserver.json_handler('/tracker/service/classify-cars')
    def mock_geotracks_response(request):
        return [{'classes': ['econom']}, {'classes': ['vip']}]


def test_vehicles_check(
        taxi_marketplace_api, tracker_response_classify_cars, mockserver,
):
    response = taxi_marketplace_api.post(
        '/v1/vehicles/check',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
        },
        json={
            'vehicles': [
                {
                    'zone_name': 'moscow',
                    'brand_code': 'lamborghini',
                    'model_code': 'diablo',
                    'year': 2010,
                    'classes': ['econom', 'vip'],
                },
                {
                    'zone_name': 'bibirevo',
                    'brand_code': 'lada',
                    'model_code': 'samara',
                    'year': 2000,
                    'classes': ['econom', 'vip'],
                },
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
