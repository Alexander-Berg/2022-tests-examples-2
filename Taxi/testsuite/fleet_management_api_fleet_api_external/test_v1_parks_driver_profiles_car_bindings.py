import json

import pytest

from fleet_management_api import utils
from fleet_management_api.test_v1_parks_driver_profiles_car_bindings import (
    ENDPOINT_URL,
)
from fleet_management_api.test_v1_parks_driver_profiles_car_bindings import (
    MOCK_URL,
)
from fleet_management_api.test_v1_parks_driver_profiles_car_bindings import (
    PARAMS,
)
from fleet_management_api.test_v1_parks_driver_profiles_car_bindings import (
    RESPONSE,
)
from . import auth


AUTH_HEADERS = {**auth.HEADERS, **utils.X_REAL_IP_HEADERS}
MOCK_AUTH_HEADERS = {
    'X-Fleet-API-Client-ID': auth.CLIENT_ID,
    'X-Fleet-API-Key-ID': str(auth.KEY_ID),
    **utils.X_REAL_IP_HEADERS,
}


@pytest.mark.parametrize('status', [200, 201])
def test_put_ok(taxi_fleet_api_external, mockserver, status):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(json.dumps(RESPONSE), status)

    response = taxi_fleet_api_external.put(
        ENDPOINT_URL, headers=AUTH_HEADERS, params=PARAMS,
    )

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'PUT'
    assert mock_request.args.to_dict() == PARAMS
    utils.check_headers(mock_request.headers, MOCK_AUTH_HEADERS)

    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE


def test_delete_ok(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return RESPONSE

    response = taxi_fleet_api_external.delete(
        ENDPOINT_URL, headers=AUTH_HEADERS, params=PARAMS,
    )

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'DELETE'
    assert mock_request.args.to_dict() == PARAMS
    utils.check_headers(mock_request.headers, MOCK_AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json() == RESPONSE
