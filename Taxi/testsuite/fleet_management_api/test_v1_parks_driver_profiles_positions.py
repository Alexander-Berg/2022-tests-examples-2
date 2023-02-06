import json

import pytest

from taxi_tests.utils import ordered_object

from . import auth

MOCK_DP_URL = '/driver_protocol/service/driver/status/list'
MOCK_DRIVER_TRACKSTORY_URL = '/driver_trackstory/park_drivers'
ENDPOINT_URL = '/v1/parks/driver-profiles/positions'


def make_request(statuses):
    return {
        'query': {
            'park': {'id': '123', 'driver_profile': {'status': statuses}},
        },
    }


@pytest.mark.parametrize(
    'dp_request,dp_response,driver_trackstory_response,'
    'request_data,expected_response',
    [
        (
            {
                'park_id': '123',
                'statuses': ['free', 'offline', 'in_order_busy'],
            },
            {
                'statuses': [
                    {
                        'driver_id': 'driver_id1',
                        'payment_type': 'online',
                        'status': 'offline',
                        'status_updated_at': '2018-12-17T00:10:00.42538Z',
                    },
                    {
                        'driver_id': 'driver_id2',
                        'payment_type': 'cash',
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:02.42538Z',
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'driver_id': 'driver_id1',
                        'position': {
                            'direction': 0,
                            'lat': 55.7,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                    {
                        'driver_id': 'driver_id3',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.5,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                    {
                        'driver_id': 'driver_id4',
                        'position': {
                            'direction': 0,
                            'lat': 55.5,
                            'lon': 37.4,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                ],
            },
            make_request(['free', 'offline', 'in_order_busy']),
            {
                'positions': [
                    {
                        'position': {
                            'lat': 55.7,
                            'lon': 37.6,
                            'last_moved_at': '2018-12-24T14:12:41+0000',
                        },
                        'driver_profile': {
                            'id': 'driver_id1',
                            'payment_type': 'online',
                            'status': 'offline',
                            'status_updated_at': '2018-12-17T00:10:00+0000',
                        },
                    },
                ],
            },
        ),
        (
            {
                'park_id': '123',
                'statuses': ['busy', 'free', 'in_order_busy', 'in_order_free'],
            },
            {
                'statuses': [
                    {
                        'driver_id': 'driver_id1',
                        'payment_type': 'none',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                        'status': 'free',
                    },
                    {
                        'driver_id': 'driver_id2',
                        'payment_type': 'none',
                        'status_updated_at': '2018-12-17T00:00:04.425380Z',
                        'status': 'in_order_free',
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'driver_id': 'driver_id1',
                        'position': {
                            'direction': 0,
                            'lat': 55.7,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                    {
                        'driver_id': 'driver_id3',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.5,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                ],
            },
            make_request([]),
            {
                'positions': [
                    {
                        'position': {
                            'lat': 55.7,
                            'lon': 37.6,
                            'last_moved_at': '2018-12-24T14:12:41+0000',
                        },
                        'driver_profile': {
                            'id': 'driver_id1',
                            'payment_type': 'none',
                            'status': 'free',
                            'status_updated_at': '2018-12-17T00:00:02+0000',
                        },
                    },
                ],
            },
        ),
        (
            {'park_id': '123', 'statuses': ['free', 'in_order_free']},
            {
                'statuses': [
                    {
                        'driver_id': 'driver_id1',
                        'payment_type': 'none',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                        'status': 'free',
                    },
                    {'driver_id': 'driver_id2', 'error': 'driver_not_found'},
                ],
            },
            {
                'drivers': [
                    {
                        'driver_id': 'driver_id3',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.5,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                ],
            },
            make_request(['free', 'in_order_free']),
            {'positions': []},
        ),
        (
            {'park_id': '123', 'statuses': ['free']},
            {
                'statuses': [
                    {
                        'driver_id': 'driver_id1',
                        'payment_type': 'none',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                        'status': 'free',
                        'last_name': 'last',
                        'first_name': 'first',
                        'middle_name': 'middle',
                        'phones': ['+7123', '+7456'],
                        'car_brand': 'skoda',
                        'car_model': 'rapid',
                        'car_number': '12235',
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'driver_id': 'driver_id1',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.5,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                ],
            },
            make_request(['free']),
            {
                'positions': [
                    {
                        'driver_profile': {
                            'id': 'driver_id1',
                            'payment_type': 'none',
                            'status': 'free',
                            'status_updated_at': '2018-12-17T00:00:02+0000',
                            'last_name': 'last',
                            'first_name': 'first',
                            'middle_name': 'middle',
                            'phones': ['+7123', '+7456'],
                        },
                        'car': {
                            'brand': 'skoda',
                            'model': 'rapid',
                            'normalized_number': '12235',
                        },
                        'position': {
                            'lat': 55.6,
                            'lon': 37.5,
                            'last_moved_at': '2018-12-24T14:12:41+0000',
                        },
                    },
                ],
            },
        ),
        # work_rule_id and callsign
        (
            {'park_id': '123', 'statuses': ['free']},
            {
                'statuses': [
                    {
                        'driver_id': 'driver_id1',
                        'status': 'free',
                        'work_rule_id': '100500',
                        'car_callsign': 'sokol',
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'driver_id': 'driver_id1',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.5,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                ],
            },
            make_request(['free']),
            {
                'positions': [
                    {
                        'driver_profile': {
                            'id': 'driver_id1',
                            'status': 'free',
                            'work_rule_id': '100500',
                        },
                        'car': {'callsign': 'sokol'},
                        'position': {
                            'lat': 55.6,
                            'lon': 37.5,
                            'last_moved_at': '2018-12-24T14:12:41+0000',
                        },
                    },
                ],
            },
        ),
        # don`t return positions of drivers with unmatched statuses
        (
            {'park_id': '123', 'statuses': ['free']},
            {'statuses': []},
            {
                'drivers': [
                    {
                        'driver_id': 'driver_id1',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.5,
                            'speed': 0,
                            'timestamp': 1545660761,
                        },
                    },
                ],
            },
            make_request(['free']),
            {'positions': []},
        ),
        # don`t return drivers without position
        (
            {'park_id': '123', 'statuses': ['free']},
            {'statuses': [{'driver_id': 'driver_id1', 'status': 'free'}]},
            {'drivers': []},
            make_request(['free']),
            {'positions': []},
        ),
    ],
)
def test_ok(
        taxi_fleet_management_api,
        mockserver,
        dp_request,
        dp_response,
        driver_trackstory_response,
        request_data,
        expected_response,
):
    @mockserver.json_handler(MOCK_DP_URL)
    def mock_dp_callback(request):
        ordered_object.assert_eq(
            json.loads(request.get_data()), dp_request, ['statuses'],
        )
        return dp_response

    @mockserver.json_handler(MOCK_DRIVER_TRACKSTORY_URL)
    def mock_driver_trackstory_callback(request):
        assert json.loads(request.get_data()) == {'park_id': '123'}
        return driver_trackstory_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_data),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert mock_dp_callback.has_calls
    assert mock_driver_trackstory_callback.has_calls
