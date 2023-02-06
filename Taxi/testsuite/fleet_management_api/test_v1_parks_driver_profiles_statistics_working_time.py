import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/driver-profiles/statistics/working-time'
ENDPOINT_URL = '/v1/parks/driver-profiles/statistics/working-time'


def err(error_message):
    return utils.format_error(error_message)


@pytest.mark.parametrize(
    'request_json, status_code, response_json',
    [
        ({}, 400, err('query must be present')),
        (
            {
                'query': {
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park must be present'),
        ),
        (
            {
                'query': {
                    'park': {'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.id must be present'),
        ),
        (
            {
                'query': {
                    'park': {'id': 123, 'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.id must be a non-empty utf-8 string without BOM'),
        ),
        (
            {
                'query': {
                    'park': {'id': '', 'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.id must be a non-empty utf-8 string without BOM'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xxx', 'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-05T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            200,
            {
                'time_interval': {
                    'start_at': '2018-12-05T14:00:00+0300',
                    'end_at': '2018-12-05T17:45:00+0045',
                    'subintervals_duration': 21600,
                    'subintervals_count': 1,
                },
                'working_time': [],
            },
        ),
    ],
)
def test_proxy(
        taxi_fleet_management_api,
        mockserver,
        request_json,
        status_code,
        response_json,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == request_json
        return response_json

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert mock_callback.times_called == (1 if status_code == 200 else 0)
    assert response.status_code == status_code
    assert response.json() == response_json
