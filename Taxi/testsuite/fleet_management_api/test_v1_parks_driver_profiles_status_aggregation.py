import json

import pytest

from . import auth

ENDPOINT_URL = 'v1/parks/driver-profiles/status/aggregation'
MOCK_URL = '/driver_protocol/service/driver/status/list'


@pytest.mark.parametrize(
    'request_body, response_body',
    [
        (
            # empty request
            {},
            {'message': 'json is not a string. Type: 0'},
        ),
        (
            # no park_id
            {'statuses': ['free']},
            {'message': 'json is not a string. Type: 0'},
        ),
        (
            # empty park_id
            {'park_id': '', 'statuses': ['free']},
            {'message': 'Park id must not be empty'},
        ),
        (
            # offline
            {
                'park_id': 'extra_super_park_id',
                'statuses': ['free', 'offline'],
            },
            {'message': 'Offline status is not acceptable'},
        ),
    ],
)
def test_bad_request(
        taxi_fleet_management_api, mockserver, request_body, response_body,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, json=request_body,
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0
    assert response.json() == response_body


@pytest.mark.parametrize(
    'request_body, dp_request, dp_response, response_body',
    [
        (
            {
                'park_id': 'extra_super_park_id',
                'statuses': ['free', 'in_order_busy'],
            },
            {
                'park_id': 'extra_super_park_id',
                'statuses': ['free', 'in_order_busy'],
            },
            {
                'statuses': [
                    {
                        'driver_id': 'extra_super_driver_id1',
                        'payment_type': 'cash',
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                    },
                    {
                        'driver_id': 'extra_super_driver_id2',
                        'payment_type': 'none',
                        'status': 'in_order_busy',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                    {
                        'driver_id': 'extra_super_driver_id3',
                        'payment_type': 'online',
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                ],
            },
            {
                'statuses': [
                    {'count': 1, 'status': 'in_order_busy'},
                    {'count': 2, 'status': 'free'},
                ],
            },
        ),
        (
            {'park_id': 'extra_super_park_id'},
            {
                'park_id': 'extra_super_park_id',
                'statuses': ['busy', 'free', 'in_order_free', 'in_order_busy'],
            },
            {
                'statuses': [
                    {
                        'driver_id': 'extra_super_driver_id1',
                        'payment_type': 'cash',
                        'status': 'busy',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                    },
                    {
                        'driver_id': 'extra_super_driver_id2',
                        'payment_type': 'cash',
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                    },
                    {
                        'driver_id': 'extra_super_driver_id3',
                        'payment_type': 'none',
                        'status': 'in_order_busy',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                    {
                        'driver_id': 'extra_super_driver_id4',
                        'payment_type': 'none',
                        'status': 'in_order_free',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                    {
                        'driver_id': 'extra_super_driver_id5',
                        'payment_type': 'online',
                        'status': 'offline',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                ],
            },
            {
                'statuses': [
                    {'count': 1, 'status': 'in_order_busy'},
                    {'count': 1, 'status': 'busy'},
                    {'count': 1, 'status': 'in_order_free'},
                    {'count': 1, 'status': 'free'},
                ],
            },
        ),
    ],
)
def test_ok(
        taxi_fleet_management_api,
        mockserver,
        request_body,
        dp_request,
        dp_response,
        response_body,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        assert json.loads(request.get_data()) == dp_request
        return dp_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == response_body
