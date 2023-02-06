import json

from . import auth
from . import utils

MOCK_URL = '/parks/legal-entities/list'
ENDPOINT_URL = '/v1/parks/legal-entities/list'

SEARCH_REQUEST = {
    'query': {
        'park': {'id': ['xxx']},
        'legal_entity': {'id': ['1'], 'registration_number': ['2']},
    },
    'offset': 0,
}
RESPONSE = {'has_more': False, 'legal_entities': [{'id': '111'}]}


def test_ok(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data(cache=True)  # call get_data to save body in request
        return RESPONSE

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(SEARCH_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert json.loads(mock_request.get_data()) == SEARCH_REQUEST
    assert response.json() == RESPONSE


def test_bad_request(taxi_fleet_management_api, mockserver):
    request_json = {'query': {'park': {'id': ['park_1', 'park_2']}}}
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    error_message = 'query.park.id must contain exactly one park id'
    assert response.status_code == 400, response.text
    assert response.json() == utils.format_error(error_message)
