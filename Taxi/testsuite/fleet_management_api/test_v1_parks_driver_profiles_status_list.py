import json

from . import auth

MOCK_URL = '/driver_protocol/service/driver/status/list'


def test_post_ok(taxi_fleet_management_api, mockserver):
    mockdata = {
        'park_id': 'zzz',
        'driver_profiles': [{'driver_id': 'xxx'}, {'driver_id': 'yyy'}],
        'statuses': ['free'],
    }

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        assert json.loads(request.get_data()) == mockdata
        return {}

    response = taxi_fleet_management_api.post(
        'v1/parks/driver-profiles/status/list',
        headers=auth.HEADERS,
        data=json.dumps(mockdata),
    )

    assert response.status_code == 200


def test_empty_request(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        'v1/parks/driver-profiles/status/list',
        headers=auth.HEADERS,
        data=json.dumps({}),
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0


def test_no_park_id(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        'v1/parks/driver-profiles/status/list',
        headers=auth.HEADERS,
        data=json.dumps(
            {
                'driver_profiles': [
                    {'driver_id': 'xxx'},
                    {'driver_id': 'yyy'},
                ],
                'statuses': ['free'],
            },
        ),
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0


def test_no_driver_profiles(taxi_fleet_management_api, mockserver):
    mockdata = {'park_id': 'zzz', 'statuses': ['free']}

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        assert json.loads(request.get_data()) == mockdata
        return {}

    response = taxi_fleet_management_api.post(
        'v1/parks/driver-profiles/status/list',
        headers=auth.HEADERS,
        data=json.dumps(mockdata),
    )

    assert response.status_code == 200


def test_no_statuses(taxi_fleet_management_api, mockserver):
    mockdata = {'park_id': 'zzz', 'driver_profiles': [{'driver_id': 'xxx'}]}

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        assert json.loads(request.get_data()) == mockdata
        return {}

    response = taxi_fleet_management_api.post(
        'v1/parks/driver-profiles/status/list',
        headers=auth.HEADERS,
        data=json.dumps(mockdata),
    )

    assert response.status_code == 200


def test_wrong_driver_profiles(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        'v1/parks/driver-profiles/status/list',
        headers=auth.HEADERS,
        data=json.dumps(
            {'park_id': 'zzz', 'driver_profiles': [{'wtf': 'ftw'}]},
        ),
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0
