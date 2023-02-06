import json

from . import auth
from . import utils

"""
Testsuite uses its own nginx config, so we test that
request to PUT /personal-patch is proxied to PATCH /personal
"""
MOCK_URL = '/parks/driver-profiles/personal'
ENDPOINT_URL = '/v1/parks/driver-profiles/personal-patch'

BODY = {  # type: ignore
    'driver_profile': {},
}


def test_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return BODY

    response = taxi_fleet_management_api.put(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params={'park_id': '1', 'id': '2'},
        json=BODY,
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'PATCH'
    assert mock_request.args.to_dict() == {'park_id': '1', 'id': '2'}
    assert json.loads(mock_request.get_data()) == BODY
    utils.check_headers(mock_request.headers, utils.X_REAL_IP_HEADERS)
    auth.check_user_ticket_headers(mock_request.headers)
    assert response.json() == BODY
