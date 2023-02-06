# encoding=utf-8
import json

import pytest

from fleet_management_api import utils
from . import auth


MOCK_URL = '/driver_work_rules/v1/work-rules/list'
ENDPOINT_URL = '/v1/parks/driver-work-rules'
PARK_ID = 'extra_super_park_id'
DEFAULT_PARAMS = {'park_id': PARK_ID}


def test_bad_request(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_api_external.get(ENDPOINT_URL, headers=auth.HEADERS)

    assert mock_callback.times_called == 0
    assert response.status_code == 400
    assert response.json() == utils.format_error(
        'parameter park_id must be set',
    )


def test_driver_work_rules_internal_error(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response('some internal error', 500)

    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=DEFAULT_PARAMS,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 500
    assert response.json() == utils.INTERNAL_ERROR


@pytest.mark.parametrize(
    'driver_work_rules_response, fleet_api_response',
    [
        ({'work_rules': []}, {'rules': []}),
        (
            {
                'work_rules': [
                    {
                        'commission_for_subvention_percent': '1.2345',
                        'commission_for_workshift_percent': '5.4321',
                        'id': 'extra_super_rule_id',
                        'is_commission_for_orders_cancelled_by_client_'
                        'enabled': True,
                        'is_commission_if_platform_commission_is_null_'
                        'enabled': True,
                        'is_driver_fix_enabled': False,
                        'is_dynamic_platform_commission_enabled': True,
                        'is_enabled': True,
                        'is_workshift_enabled': True,
                        'name': 'Яндекс',
                        'subtype': 'selfreg',
                        'type': 'park',
                    },
                ],
            },
            {
                'rules': [
                    {
                        'id': 'extra_super_rule_id',
                        'name': 'Яндекс',
                        'is_enabled': True,
                    },
                ],
            },
        ),
    ],
)
def test_ok(
        taxi_fleet_api_external,
        mockserver,
        driver_work_rules_response,
        fleet_api_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return driver_work_rules_response

    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=DEFAULT_PARAMS,
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200
    assert response.json() == fleet_api_response


@pytest.mark.parametrize(
    'driver_work_rules_response',
    [json.dumps({}), json.dumps({'work_rules': {}})],
)
def test_internal_error(
        taxi_fleet_api_external, mockserver, driver_work_rules_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(driver_work_rules_response, 200)

    response = taxi_fleet_api_external.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=DEFAULT_PARAMS,
    )

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert json.loads(mock_request.get_data()) == {
        'query': {'park': {'id': PARK_ID}},
    }
    assert response.status_code == 500
    assert response.json() == utils.INTERNAL_ERROR
