import json
import uuid

from . import auth
from . import utils


MOCK_URL = '/parks/driver-profiles/create'
ENDPOINT_URL = '/v1/parks/driver-profiles/create'

BODY: dict = {'driver_profile': {}}


def test_ok(taxi_fleet_management_api, mockserver):
    idempotency_token = uuid.uuid1().hex

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return BODY

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers={**auth.HEADERS, 'X-Idempotency-Token': idempotency_token},
        params={'park_id': '1'},
        json=BODY,
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert mock_request.args.to_dict() == {'park_id': '1'}
    assert json.loads(mock_request.get_data()) == BODY
    auth.check_user_ticket_headers(mock_request.headers)
    assert mock_request.headers['X-Idempotency-Token'] == idempotency_token
    assert response.json() == BODY


def test_error_pass(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps(utils.format_parks_error('text', 'code')), 400,
        )

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, params={'park_id': '1'}, json={},
    )

    assert response.status_code == 400, response.text
    assert mock_callback.times_called == 1
    assert response.json() == utils.format_error('text', 'code')
