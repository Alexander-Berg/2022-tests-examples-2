import json

from fleet_management_api import utils
from . import auth

MOCK_URL = '/parks/driver-profiles/retrieve'
ENDPOINT_URL = '/v1/parks/driver-profiles/retrieve'


def test_ok(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {}

    request_json = {
        'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
        'fields': {
            'account': utils.ACCOUNT_FIELDS,
            'car': utils.CAR_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'rating': utils.RATING_FIELDS,
            'driver_categories': utils.DRIVER_CATEGORIES_FIELDS,
            'driver_metrics': utils.DRIVER_METRICS_FIELDS,
            'taximeter_disable_status': utils.TAXIMETER_DISABLE_STATUS_FIELDS,
        },
    }

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data())['fields'] == {
        'account': utils.EXTERNAL_ACCOUNT_FIELDS,
        'car': utils.EXTERNAL_CAR_FIELDS,
        'driver_profile': utils.EXTERNAL_DRIVER_PROFILE_FIELDS,
        'current_status': utils.EXTERNAL_CURRENT_STATUS_FIELDS,
        'taximeter_disable_status': (
            utils.EXTERNAL_TAXIMETER_DISABLE_STATUS_FIELDS
        ),
    }


def test_set_config(taxi_fleet_api_external, mockserver, config):
    REQUEST_JSON = {
        'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
        'fields': {'account': utils.EXTERNAL_ACCOUNT_FIELDS},
    }
    CATEGORIES = ['econom', 'comfort']

    config.set_values(
        dict(
            FLEET_API_CAR_CATEGORIES={
                'internal_categories': [],
                'external_categories': CATEGORIES,
            },
        ),
    )

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {}

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(REQUEST_JSON),
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(
        mock_json_request, categories=CATEGORIES,
    )
    assert mock_json_request == REQUEST_JSON
