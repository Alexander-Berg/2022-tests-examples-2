import json

import pytest

from fleet_management_api import utils
from . import auth


MOCK_URL = '/parks/cars/list'
ENDPOINT_URL = '/v1/parks/cars/list'
PARK_ID = 'park_X'


@pytest.mark.parametrize(
    'request_fields,expected_parks_request_fields',
    [
        (None, {'car': utils.EXTERNAL_CAR_FIELDS}),
        ({'car': utils.CAR_FIELDS}, {'car': utils.EXTERNAL_CAR_FIELDS}),
    ],
)
def test_fields(
        taxi_fleet_api_external,
        mockserver,
        request_fields,
        expected_parks_request_fields,
):
    ok_response = {
        'offset': 0,
        'total': 0,
        'cars': [],
        'parks': [{'id': PARK_ID}],
    }

    json_request = {'query': {'park': {'id': PARK_ID}}}

    if request_fields:
        json_request['fields'] = request_fields

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(json_request),
    )

    assert response.status_code == 200, response.text
    assert response.json() == ok_response

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request == {
        'query': {'park': {'id': PARK_ID}},
        'fields': expected_parks_request_fields,
        'limit': 1000,
    }
