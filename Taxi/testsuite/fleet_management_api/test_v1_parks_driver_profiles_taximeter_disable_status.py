import json

import pytest
import werkzeug

from . import auth
from . import utils

MOCK_URL = '/parks/driver-profiles/taximeter-disable-status'
ENDPOINT_URL = '/v1/parks/driver-profiles/taximeter-disable-status'

BODY = {'disabled': True, 'disable_message': 'doesnt matter'}


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

    assert response.status_code == 200
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'PUT'
    assert mock_request.args.to_dict() == {'park_id': '1', 'id': '2'}
    assert json.loads(mock_request.get_data()) == BODY
    auth.check_user_ticket_headers(mock_request.headers)
    assert response.json() == BODY


@pytest.mark.parametrize(
    'params_json,error_text',
    [
        ({'id': '228'}, 'parameter park_id must be set'),
        ({'park_id': 228}, 'parameter id must be set'),
    ],
)
def test_bad_request(
        taxi_fleet_management_api, mockserver, params_json, error_text,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.put(
        ENDPOINT_URL, headers=auth.HEADERS, params=params_json, json=BODY,
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0
    assert response.json() == utils.format_error(error_text)


def test_parks_error(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return werkzeug.Response(
            json.dumps(utils.format_parks_error('text', 'code')), 400,
        )

    response = taxi_fleet_management_api.put(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        params={'park_id': '1', 'id': '2'},
        json=BODY,
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 1
    assert response.json() == utils.format_error('text', 'code')
