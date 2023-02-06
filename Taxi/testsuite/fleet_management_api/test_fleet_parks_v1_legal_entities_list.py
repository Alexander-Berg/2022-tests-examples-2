import json

import pytest

from . import auth

MOCK_URL = '/parks/legal-entities/list'
ENDPOINT_URL = '/fleet/api/v1/parks/legal-entities/list'


PARKS_RESPONSE = {'has_more': False, 'legal_entities': [{'id': '111'}]}


SEARCH_REQUEST_PARAMS = [
    (
        {
            'query': {
                'legal_entity': {'id': ['1'], 'registration_number': ['2']},
            },
            'offset': 0,
        },
        {'has_more': False, 'legal_entities': [{'id': '111'}]},
    ),
    ({}, {'has_more': False, 'legal_entities': [{'id': '111'}]}),
]


@pytest.mark.parametrize(
    ['request_body', 'expected_response'], SEARCH_REQUEST_PARAMS,
)
def test_ok(
        taxi_fleet_management_api, mockserver, request_body, expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data(cache=True)  # call get_data to save body in request
        return PARKS_RESPONSE

    headers = auth.HEADERS
    headers.update({'X-Park-ID': 'xxx'})
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=headers, data=json.dumps(request_body),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']

    parks_search_request = request_body
    parks_search_request.setdefault('query', {}).update(
        {'park': {'id': ['xxx']}},
    )
    assert json.loads(mock_request.get_data()) == parks_search_request
    assert response.json() == expected_response
