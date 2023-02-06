import pytest

PARK_ID = '12345'
PARK_NAME = 'someParkName'
MOCK_RETURN = {'driver_profiles': [], 'parks': [{'name': PARK_NAME}]}
RESPONSE = {'status': 'ok', 'name': PARK_NAME}


@pytest.fixture
def parks_request(mockserver):
    @mockserver.json_handler(
        '/taximeter-xservice.taxi.yandex.net/fm-api/auth/grants',
    )
    def mock_parks(request):
        return {'grants': [{'grant_type': 'update_posting'}]}


def test_auth_check_base(taxi_marketplace_api, mockserver, db, parks_request):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def mock_callback(request):
        return MOCK_RETURN

    response = taxi_marketplace_api.post(
        '/v1/auth/check',
        headers={
            'X-YaTaxi-API-Key': 'marketplace_api_key',
            'x-real-ip': '192.168.123.123',
            'Authorization': 'Bearer 12345',
        },
        json={'grant': 'update_posting', 'company': PARK_ID},
    )
    assert response.status_code == 200
    assert response.json() == RESPONSE
