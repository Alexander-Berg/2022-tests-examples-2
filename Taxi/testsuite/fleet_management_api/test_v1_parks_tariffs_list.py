import json

from . import auth
from . import utils


MOCK_URL = '/driver_work_rules/v1/tariffs/list'
ENDPOINT_URL = '/v1/parks/tariffs/list'


OK_REQUEST = {'query': {'park': {'id': 'my_park_id'}}}

BAD_REQUEST = {'query': {'park': {'id': ''}}}

OK_RESPONSE = {
    'tariffs': [
        {
            'name': 'abc',
            'id': 'tariff_id_322',
            'folder_name': 'my_tariffs',
            'folder_id': 'folder_id_322',
        },
    ],
}


def test_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return OK_RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert response.status_code == 200
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    mock_req_json = json.loads(mock_request.get_data())
    assert mock_req_json == OK_REQUEST
    assert response.json() == OK_RESPONSE


def test_dwr_internal_error(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response('some internal error', 500)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 500
    assert response.json() == utils.INTERNAL_ERROR


def test_fleet_api_bad_request(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(BAD_REQUEST),
    )
    error_json = {
        'message': (
            'query.park.id must be a non-empty utf-8 string without BOM'
        ),
    }

    assert mock_callback.times_called == 0
    assert response.status_code == 400
    assert response.json() == error_json


def test_dwr_bad_request(taxi_fleet_management_api, mockserver):
    message = 'bad request'
    error_code = 400

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps({'message': message, 'code': str(error_code)}),
            error_code,
        )

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(OK_REQUEST),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == error_code
    assert response.json() == utils.format_error(message)
