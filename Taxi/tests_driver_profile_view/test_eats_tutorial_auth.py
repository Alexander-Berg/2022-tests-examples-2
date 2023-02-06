import json

import pytest

HANDLER = '/driver/v1/profile-view/v1/eats/tutorial/auth'

HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'parkid',
    'X-YaTaxi-Driver-Profile-Id': 'driverid',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.10 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.10 (1234)',
}

PARK_DRIVER_PROFILE_ID = 'parkid_driverid'

EATS_BINDINGS_HANDLER = (
    '/driver-profiles/v1/eats-couriers-binding'
    '/retrieve_by_park_driver_profile_id'
)

EATS_SERVICE_TOKEN_HANDLER = (
    '/eats-core-integration/internal-api/v1/courier/service-token'
)

EATS_TUTORIAL_URL = 'http://eats-courier-tutorial.ru'
EATS_TUTORIAL_TOKEN = 'supersecret'


@pytest.mark.config(EATS_COURIER_TUTORIAL_SETTINGS={'url': EATS_TUTORIAL_URL})
@pytest.mark.parametrize(
    'binding,token_resp_code,token_response,expected_code,expected_response',
    [
        pytest.param(
            {
                'taxi_id': PARK_DRIVER_PROFILE_ID,
                'eats_id': '127054',
                'courier_app': 'taximeter',
            },
            200,
            {'token': EATS_TUTORIAL_TOKEN},
            200,
            {'token': EATS_TUTORIAL_TOKEN, 'url': EATS_TUTORIAL_URL},
            id='happy path',
        ),
        pytest.param(
            {'taxi_id': PARK_DRIVER_PROFILE_ID},
            200,
            {'token': EATS_TUTORIAL_TOKEN},
            400,
            {'message': 'tutorial is not available', 'code': 'NOT_AVAILABLE'},
            id='profile is not Eats courier',
        ),
        pytest.param(
            {
                'taxi_id': PARK_DRIVER_PROFILE_ID,
                'eats_id': '127054',
                'courier_app': 'taximeter',
            },
            400,
            {'message': 'not_available', 'status': 'not_availabe'},
            400,
            {'message': 'tutorial is not available', 'code': 'NOT_AVAILABLE'},
            id='could not authorize',
        ),
    ],
)
async def test_eats_tutorial_auth(
        taxi_driver_profile_view,
        mockserver,
        binding,
        token_resp_code,
        token_response,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(EATS_BINDINGS_HANDLER)
    def _mock_eats_bindings(request):
        request_json = json.loads(request.get_data())
        assert PARK_DRIVER_PROFILE_ID in request_json['id_in_set']
        return mockserver.make_response(json={'binding': [binding]})

    @mockserver.json_handler(EATS_SERVICE_TOKEN_HANDLER)
    def _mock_service_token(request):
        return mockserver.make_response(
            json=token_response, status=token_resp_code,
        )

    response = await taxi_driver_profile_view.post(HANDLER, headers=HEADERS)
    assert response.status_code == expected_code
    assert response.json() == expected_response
