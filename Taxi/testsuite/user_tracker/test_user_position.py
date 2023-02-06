import pytest

from .user_tracker_tools import defer_wait_for_async_write  # used in fixtures


assert defer_wait_for_async_write  # supressing 'imported but unused'


def test_no_position(taxi_user_tracker):
    response = taxi_user_tracker.get('/user/position?user_id=super-man')
    assert response.status_code == 200
    assert response.json() == {'user_id': 'super-man'}


def test_bad_request(taxi_user_tracker):
    response = taxi_user_tracker.get('/user/position?driver_id=ololo')
    assert response.status_code == 400


@pytest.mark.parametrize(
    'params',
    [
        {},
        {'user_id': 'super-man'},
        {'user_id': 'super-man', 'lon': 3.14},
        {'user_id': 'super-man', 'lon': 3.14, 'lat': 2.72},
        {'user_id': 'super-man', 'lon': 3.14, 'accuracy': 14},
        {
            'user_id': 'super-man',
            'lon': 3.14,
            'lat': 2.72,
            'accuracy': 14,
            'timestamp': 1,
        },
    ],
)
def test_bad_store_request(taxi_user_tracker, params):
    response = taxi_user_tracker.post('/user/position/store', params=params)
    assert response.status_code == 400


@pytest.mark.parametrize('sync', [0, 1])
def test_store_request(taxi_user_tracker, sync):
    response = taxi_user_tracker.post(
        '/user/position/store',
        params={
            'user_id': 'super-man',
            'lon': 3.14,
            'lat': 2.72,
            'accuracy': 14,
            'sync': sync,
        },
    )
    assert response.status_code == 200


def test_store_and_get_request(taxi_user_tracker):
    response = taxi_user_tracker.post(
        '/user/position/store',
        params={
            'user_id': 'super-man',
            'lon': 12.0,
            'lat': 13.0,
            'accuracy': 14,
            'sync': 1,
        },
    )
    assert response.status_code == 200

    response = taxi_user_tracker.get('/user/position?user_id=super-man')
    assert response.status_code == 200
    data = response.json()
    assert 'timestamp' in data
    del data['timestamp']
    assert data == {
        'user_id': 'super-man',
        'lon': 12.0,
        'lat': 13.0,
        'accuracy': 14,
    }


@pytest.mark.now('2018-07-04T15:02:00Z')
@pytest.mark.config(USER_TRACKER_GEOHISTORY_ENABLE=True)
@pytest.mark.usefixtures('defer_wait_for_async_write')
def test_async_store_to_geotracks(taxi_user_tracker, redis_store):
    response = taxi_user_tracker.post(
        '/user/position/store',
        params={
            'user_id': 'spider-man',
            'lon': 12.0,
            'lat': 13.0,
            'accuracy': 14,
            'sync': 1,
            'timestamp': 1530716400,
        },
    )
    assert response.status_code == 200

    assert redis_store.hget(b'history:20180704:15:spider-man', '1530716400')
