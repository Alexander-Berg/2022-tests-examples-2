import json

import pytest

from fleet_management_api import utils
from . import auth


MOCK_URL = '/parks/texts'
ENDPOINT_URL = '/v1/parks/texts'
PARK_ID = 'texts_park'
OK_PARAMS = {'park_id': PARK_ID, 'text_type': 'terms'}


@pytest.fixture
def parks_texts(mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {'text': 'длинный текст'}

    return mock_callback


@pytest.mark.parametrize(
    'absent_header', [auth.API_KEY_HEADER, auth.CLIENT_ID_HEADER],
)
def test_absent_header(taxi_fleet_api_external, api_keys, absent_header):
    headers = auth.HEADERS.copy()
    headers.pop(absent_header)
    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=headers,
    )

    assert api_keys.times_called == 0
    assert response.status_code == 401
    assert response.json() == utils.format_error(
        f'header {absent_header} must not be empty',
    )


def test_ok(taxi_fleet_api_external, api_keys, parks_texts):
    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 200
    assert parks_texts.times_called == 1
    assert api_keys.times_called == 1
    auth_request = json.loads(api_keys.next_call()['request'].get_data())
    assert auth_request['entity_id'] == PARK_ID
    assert auth_request['permission_ids'] == ['fleet-api:v1-parks-texts:GET']


def test_forbiden(taxi_fleet_api_external, mockserver):
    forbidden_message = 'access denied'

    @mockserver.json_handler(auth.API_KEYS_MOCK_URL)
    def api_keys_mock_callback(request):
        response_json = {'code': '403', 'message': forbidden_message}
        return mockserver.make_response(json.dumps(response_json), 403)

    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 403
    assert response.json() == utils.format_error(forbidden_message)
    assert api_keys_mock_callback.times_called == 1


@pytest.mark.parametrize('status_code', [400, 401, 404, 500, 503])
def test_internal_error(taxi_fleet_api_external, mockserver, status_code):
    @mockserver.json_handler(auth.API_KEYS_MOCK_URL)
    def api_keys_mock_callback(request):
        response_json = {'code': f'{status_code}', 'message': f'{status_code}'}
        return mockserver.make_response(json.dumps(response_json), status_code)

    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, params=OK_PARAMS, headers=auth.HEADERS,
    )

    assert response.status_code == 500
    assert response.json() == utils.INTERNAL_ERROR
    assert api_keys_mock_callback.times_called == 1
