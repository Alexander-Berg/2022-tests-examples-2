import json

from dateutil import parser
import pytest

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
DRIVER_ID = 'dfa93221ef16b300bda7d41b4bae8d58'

FTS_USAGE_CONFIG_VALUE = {
    'bulk-positions': {'use-gateway': 100, 'use-grpc': 0},
    'bulk-shorttracks': {'use-gateway': 100, 'use-grpc': 0},
    'position': {'use-gateway': 100, 'use-grpc': 0},
    'send-positions': {'use-gateway': 100, 'use-grpc': 0},
    'shorttrack': {'use-gateway': 100, 'use-grpc': 0},
    'track': {'use-gateway': 100, 'use-grpc': 0},
}


async def test_getpos_nopolicy(taxi_geosharing):
    request = {
        'update_last_seen': True,
        'driver_id': DRIVER_ID,
        'user_id': USER_ID,
        'order_source_pos': [37.0, 55.1],
        'driver_pos': [37.0, 55.1],
    }
    response = await taxi_geosharing.post('geosharing/v1/getpos', request)
    expected = {'result': 'no_location'}
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.now('2020-01-24T10:00:00+0000')
@pytest.mark.parametrize(
    'user_pos,accuracy,timestamp,driver_pos,expected_status',
    [
        (
            [37.001, 55.101],
            10,
            '2020-01-24T10:00:00+0000',
            [37.002, 55.102],
            'ok',
        ),
        (
            [37.001, 55.101],
            10,
            '2020-01-24T10:00:00+0000',
            [39.002, 59.102],
            'driver_too_far',
        ),
        (
            [37.001, 55.101],
            200,
            '2020-01-24T10:00:00+0000',
            [37.002, 55.102],
            'passenger_bad_accuracy',
        ),
        (
            [39.001, 59.101],
            10,
            '2020-01-24T10:00:00+0000',
            [37.002, 55.102],
            'passenger_too_far',
        ),
        (
            [37.001, 55.101],
            10,
            '2019-01-24T10:00:00+0000',
            [37.002, 55.102],
            'location_too_old',
        ),  # too old
        (
            'error',
            None,
            None,
            [37.002, 55.102],
            'no_location',
        ),  # bad user-tracker response
    ],
)
@pytest.mark.config(
    GEOSHARING_SYNC_REDIS=True, FTS_USAGE=FTS_USAGE_CONFIG_VALUE,
)
@pytest.mark.experiments3(filename='exp3_geosharing_policy.json')
async def test_getpos(
        taxi_geosharing,
        mockserver,
        redis_store,
        user_pos,
        accuracy,
        timestamp,
        driver_pos,
        expected_status,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/user-tracker/user/position')
    def position_store(request):
        assert request.args['user_id'] == USER_ID
        if user_pos == 'error':
            return mockserver.make_response('InternalServerError', 500)
        ut_response = {'user_id': USER_ID}
        if user_pos is not None:
            ut_response['lon'] = user_pos[0]
            ut_response['lat'] = user_pos[1]
            ut_response['accuracy'] = accuracy
            ut_response['timestamp'] = parser.parse(timestamp).timestamp()
        return ut_response

    # pylint: disable=unused-variable
    @mockserver.json_handler('/internal-trackstory/go-users/position')
    def _mock_internal_trackstory(request):
        if user_pos == 'error':
            return mockserver.make_response('WrongFormat', 400)

        response = {
            'contractor': {'uuid': USER_ID, 'dbid': 'users'},
            'Verified': [],
        }
        if user_pos is not None:
            response['Verified'].append(
                {
                    'timestamp': parser.parse(timestamp).timestamp() * 1000,
                    'sensors': [],
                    'geodata': [
                        {
                            'positions': [
                                {
                                    'position': [user_pos[0], user_pos[1]],
                                    'accuracy': accuracy,
                                },
                            ],
                            'time_shift': 0,
                        },
                    ],
                },
            )
        return [response]

    # pylint: disable=unused-variable
    @mockserver.json_handler('/fleet-tracking-system/v1/position')
    def _mock_fts(request):
        if user_pos == 'error':
            return mockserver.make_response('WrongFormat', 400)

        response = {f'users_{USER_ID}': {'Verified': []}}
        if user_pos is not None:
            response[f'users_{USER_ID}']['Verified'].append(
                {
                    'timestamp': parser.parse(timestamp).timestamp() * 1000,
                    'sensors': {},
                    'geodata': [
                        {
                            'time_shift': 0,
                            'positions': [
                                {
                                    'lon': user_pos[0],
                                    'lat': user_pos[1],
                                    'accuracy': accuracy,
                                },
                            ],
                        },
                    ],
                },
            )
        return response

    request = {
        'update_last_seen': True,
        'driver_id': DRIVER_ID,
        'user_id': USER_ID,
        'order_source_pos': [37.0, 55.1],
        'driver_pos': driver_pos,
    }
    response = await taxi_geosharing.post('geosharing/v1/getpos', request)
    expected = {'result': expected_status}
    if expected_status == 'ok':
        pos = {
            'position': user_pos,
            'accuracy': accuracy,
            'retrieved_at': '2020-01-24T10:00:00+0000',
        }
        expected_position = {
            'position': pos,
            'status': 'ok',
            'seen_at': '2020-01-24T10:00:00+0000',
        }
        expected['user_position'] = pos
        redis_data = redis_store.get('geosharing:seen:' + USER_ID)
        assert json.loads(redis_data) == expected_position

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.now('2020-01-24T10:00:00+0000')
@pytest.mark.parametrize(
    'user_pos,accuracy,timestamp,driver_pos,expected_status',
    [
        (
            [37.001, 55.101],
            10,
            '2020-01-24T10:00:00+0000',
            [37.002, 55.102],
            'ok',
        ),
        (
            [37.001, 55.101],
            10,
            '2020-01-24T10:00:00+0000',
            [39.002, 59.102],
            'driver_too_far',
        ),
        (
            [37.001, 55.101],
            200,
            '2020-01-24T10:00:00+0000',
            [37.002, 55.102],
            'passenger_bad_accuracy',
        ),
        (
            [39.001, 59.101],
            10,
            '2020-01-24T10:00:00+0000',
            [37.002, 55.102],
            'passenger_too_far',
        ),
        (
            [37.001, 55.101],
            10,
            '2019-01-24T10:00:00+0000',
            [37.002, 55.102],
            'location_too_old',
        ),  # too old
        (
            'error',
            None,
            None,
            [37.002, 55.102],
            'no_location',
        ),  # bad user-tracker response
    ],
)
@pytest.mark.config(
    GEOSHARING_SYNC_REDIS=True, FTS_USAGE=FTS_USAGE_CONFIG_VALUE,
)
@pytest.mark.experiments3(filename='exp3_geosharing_policy.json')
async def test_getpos_from_trackstory(
        taxi_geosharing,
        mockserver,
        redis_store,
        user_pos,
        accuracy,
        timestamp,
        driver_pos,
        expected_status,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/internal-trackstory/go-users/position')
    def _mock_internal_trackstory(request):
        if user_pos == 'error':
            return mockserver.make_response('WrongFormat', 400)

        response = {
            'contractor': {'uuid': USER_ID, 'dbid': 'users'},
            'Verified': [],
        }
        if user_pos is not None:
            response['Verified'].append(
                {
                    'timestamp': parser.parse(timestamp).timestamp() * 1000,
                    'sensors': [],
                    'geodata': [
                        {
                            'positions': [
                                {
                                    'position': [user_pos[0], user_pos[1]],
                                    'accuracy': accuracy,
                                },
                            ],
                            'time_shift': 0,
                        },
                    ],
                },
            )
        return [response]

    # pylint: disable=unused-variable
    @mockserver.json_handler('/fleet-tracking-system/v1/position')
    def _mock_fts(request):
        if user_pos == 'error':
            return mockserver.make_response('WrongFormat', 400)

        response = {f'users_{USER_ID}': {'Verified': []}}
        if user_pos is not None:
            response[f'users_{USER_ID}']['Verified'].append(
                {
                    'timestamp': parser.parse(timestamp).timestamp() * 1000,
                    'sensors': {},
                    'geodata': [
                        {
                            'time_shift': 0,
                            'positions': [
                                {
                                    'lon': user_pos[0],
                                    'lat': user_pos[1],
                                    'accuracy': accuracy,
                                },
                            ],
                        },
                    ],
                },
            )
        return response

    request = {
        'update_last_seen': True,
        'driver_id': DRIVER_ID,
        'user_id': USER_ID,
        'order_source_pos': [37.0, 55.1],
        'driver_pos': driver_pos,
    }
    response = await taxi_geosharing.post('geosharing/v1/getpos', request)
    expected = {'result': expected_status}
    if expected_status == 'ok':
        pos = {
            'position': user_pos,
            'accuracy': accuracy,
            'retrieved_at': '2020-01-24T10:00:00+0000',
        }
        expected_position = {
            'position': pos,
            'status': 'ok',
            'seen_at': '2020-01-24T10:00:00+0000',
        }
        expected['user_position'] = pos
        redis_data = redis_store.get('geosharing:seen:' + USER_ID)
        assert json.loads(redis_data) == expected_position

    assert response.status_code == 200
    assert response.json() == expected
