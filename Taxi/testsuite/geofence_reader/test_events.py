import time

import pytest


def remove_noise_fields(d):
    return {
        k: d[k] for k in d if k not in ['event_id', 'zone_id', 'zone_name']
    }


def assert_event_lists_equal(left, rigth, do_assert=True):
    if do_assert:
        assert len(left) == len(rigth)
    else:
        if len(left) != len(rigth):
            return False

    result = True
    lft = [remove_noise_fields(e) for e in left]
    rght = [remove_noise_fields(e) for e in rigth]
    for a, b in zip(lft, rght):
        if do_assert:
            assert a == b
        else:
            result = result and a == b
    return result


def check_event_lists_equal(left, right):
    return assert_event_lists_equal(left, right, False)


def sleep():
    time.sleep(0.4)


@pytest.mark.xfail(reason='Flaky, see TAXIBACKEND-15038')
def test_in_out(taxi_geofence, mockserver, load, db):
    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert response.json() == []

    area = {
        'id': 12,
        'name': 'SVO',
        'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [[[(1, 1), (1, -1), (-1, -1), (-1, 1)]]],
        },
    }
    zone_name = area['name']
    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(zone_name), area,
    )
    assert response.status_code == 200

    sleep()

    response = taxi_geofence.get(
        '/monitoring-areas/{}/state'.format(zone_name),
    )
    assert response.status_code == 200
    assert response.json() == {'events': [], 'last_event_id': '-1'}

    response = taxi_geofence.get('/input/carstates-dump')
    assert response.status_code == 200
    assert response.json() == []

    data = 'timestamp=1\tlon=0.2\tlat=0.2\tuuid=1000\tclid=400\n'
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    sleep()

    event1 = {
        'clid': '400',
        'uuid': '1000',
        'last_update_time': 1,
        'arrival_time': 1,
        'event_type': 'entered',
        'event_id': '1',
        'event_time': 1,
    }
    response = taxi_geofence.get(
        '/monitoring-areas/{}/state'.format(zone_name),
    )
    assert response.status_code == 200
    assert response.json() == {'events': [event1], 'last_event_id': '1'}

    response = taxi_geofence.get('/input/carstates-dump')
    assert response.status_code == 200
    assert_event_lists_equal(response.json(), [event1])

    response = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name), {},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [event1],
        'unread': 0,
        'last_event_id': '1',
    }

    data = 'timestamp=2\tlon=3\tlat=0.2\tuuid=1000\tclid=400\n'
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    sleep()

    event2 = {
        'clid': '400',
        'uuid': '1000',
        'arrival_time': 1,
        'last_update_time': 1,
        'event_type': 'left',
        'event_id': '2',
        'event_time': 2,
    }
    response = taxi_geofence.get(
        '/monitoring-areas/{}/state'.format(zone_name),
    )
    assert response.status_code == 200
    assert response.json() == {'events': [], 'last_event_id': '2'}

    response = taxi_geofence.get('/input/carstates-dump')
    assert response.status_code == 200
    assert_event_lists_equal(response.json(), [event2])

    event3 = {
        'clid': '400',
        'uuid': '1000',
        'last_update_time': 3,
        'arrival_time': 3,
        'event_type': 'entered',
        'event_id': '3',
        'event_time': 3,
    }
    data = 'timestamp=3\tlon=0.2\tlat=0.2\tuuid=1000\tclid=400\n'
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    sleep()

    # no filtering
    response = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name), {},
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 3
    assert response.json()['events'][0] == event1
    assert response.json()['events'][1] == event2
    assert response.json()['events'][2] == event3

    response2 = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name),
        {'range': {'newer_than': '-1'}},
    )
    assert response2.status_code == 200
    assert response2.json() == response.json()

    # limit
    response = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name), {'limit': 1},
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 1
    assert response.json()['events'][0] == event1

    # newer_than
    req = {'range': {'newer_than': event1['event_id']}}
    response = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name), req,
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 2
    assert response.json()['events'][0] == event2
    assert response.json()['events'][1] == event3
    assert response.json()['unread'] == 0

    # newer_than & limit
    response = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name),
        {'range': {'newer_than': event1['event_id']}, 'limit': 1},
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 1
    assert response.json()['events'][0] == event2
    assert response.json()['unread'] == 1

    response = taxi_geofence.delete('/monitoring-areas/{}'.format(zone_name))
    assert response.status_code == 200


def test_outdated(taxi_geofence, mockserver, load, db):
    area = {
        'id': 123,
        'name': 'SVU',
        'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [[[(1, 1), (1, -1), (-1, -1), (-1, 1)]]],
        },
    }
    zone_name = area['name']
    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(zone_name), area,
    )
    assert response.status_code == 200

    sleep()

    data = '\n'.join(
        [
            'timestamp=3\tlon=0.2\tlat=0.2\tuuid=1001\tclid=400',
            'timestamp=2\tlon=3\tlat=0.2\tuuid=1001\tclid=400',
        ],
    )
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    sleep()

    event1 = {
        'clid': '400',
        'uuid': '1001',
        'last_update_time': 3,
        'arrival_time': 3,
        'event_type': 'entered',
        'event_id': '4',
        'event_time': 3,
    }
    response = taxi_geofence.post(
        '/monitoring-areas/{}/events-history'.format(zone_name), {},
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 1
    assert_event_lists_equal(response.json()['events'], [event1])

    response = taxi_geofence.delete('/monitoring-areas/{}'.format(zone_name))
    assert response.status_code == 200


@pytest.mark.config(
    GEOFENCE_INPUT_CHECK_INTERVAL_SEC=1,
    GEOFENCE_INPUT_CAR_LOST_TIMEOUT_SEC_BY_ZONE={'__default__': 2},
)
def test_driver_lost(taxi_geofence):
    area = {
        'name': 'SVE',
        'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [[[(1, 1), (1, -1), (-1, -1), (-1, 1)]]],
        },
    }
    zone_name = area['name']
    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(zone_name), area,
    )
    assert response.status_code == 200

    sleep()

    data = '\n'.join(['timestamp=20\tlon=0.2\tlat=0.2\tuuid=1002\tclid=400'])
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    data = '\n'.join(['timestamp=40\tlon=0.2\tlat=10\tuuid=1003\tclid=400'])
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    event1 = {
        'clid': '400',
        'uuid': '1002',
        'last_update_time': 20,
        'arrival_time': 20,
        'event_type': 'entered',
        'event_id': '5',
        'event_time': 20,
    }
    event2 = {
        'clid': '400',
        'uuid': '1002',
        'arrival_time': 20,
        'last_update_time': 20,
        'last_seen_time': 20,
        'event_type': 'lost',
        'event_id': '6',
        'event_time': 40,
    }
    for i in range(10):
        sleep()
        response = taxi_geofence.post(
            '/monitoring-areas/{}/events-history'.format(zone_name), {},
        )
        assert response.status_code == 200
        if check_event_lists_equal(
                response.json()['events'], [event1, event2],
        ):
            break
    assert_event_lists_equal(response.json()['events'], [event1, event2])


@pytest.mark.config(
    GEOFENCE_INPUT_CHECK_INTERVAL_SEC=1,
    GEOFENCE_INPUT_CAR_LOST_TIMEOUT_SEC_BY_ZONE={'__default__': 1},
)
def test_last_update_time(taxi_geofence):
    area = {
        'name': 'SVA',
        'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [[[(1, 1), (1, -1), (-1, -1), (-1, 1)]]],
        },
    }
    zone_name = area['name']
    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(zone_name), area,
    )
    assert response.status_code == 200

    sleep()
    data = '\n'.join(['timestamp=42\tlon=0.2\tlat=0.2\tuuid=1002\tclid=400'])
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    sleep()
    sleep()
    data = '\n'.join(['timestamp=44\tlon=0.2\tlat=0.2\tuuid=1002\tclid=400'])
    response = taxi_geofence.post('/input/positions', data=data)
    assert response.status_code == 200

    event1 = {
        'clid': '400',
        'uuid': '1002',
        'last_update_time': 44,
        'arrival_time': 42,
        'event_type': 'entered',
        'event_id': '9',
        'event_time': 42,
    }
    # Updated time is stored in DB with a delay, wait for some time
    for i in range(10):
        sleep()
        response = taxi_geofence.post(
            '/monitoring-areas/{}/events-history'.format(zone_name), {},
        )
        assert response.status_code == 200
        if check_event_lists_equal(response.json()['events'], [event1]):
            break
    assert_event_lists_equal(response.json()['events'], [event1])

    event_id = response.json()['events'][0]['event_id']

    response = taxi_geofence.get(
        '/monitoring-areas/{}/state'.format(zone_name),
    )
    assert response.status_code == 200
    assert_event_lists_equal(response.json()['events'], [event1])
    assert response.json()['last_event_id'] == event_id


@pytest.mark.config(
    GEOFENCE_INPUT_CHECK_INTERVAL_SEC=1,
    GEOFENCE_INPUT_CAR_LOST_TIMEOUT_SEC_BY_ZONE={'__default__': 1},
)
def test_update_no_duplicates(taxi_geofence, db, testpoint):
    @testpoint('store_carzone_events')
    def wait_store_carzone_events(data):
        pass

    area = {
        'name': 'SVI',
        'geometry': {
            'type': 'MultiPolygon',
            'coordinates': [[[(1, 1), (1, -1), (-1, -1), (-1, 1)]]],
        },
    }
    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(area['name']), area,
    )
    assert response.status_code == 200
    sleep()

    position_data_template = (
        'timestamp={}\tlon=0.2\tlat=0.2\tuuid=1002\tclid=400'
    )
    for i in range(42, 46):
        data = '\n'.join([position_data_template.format(i)])
        response = taxi_geofence.post('/input/positions', data=data)
        assert response.status_code == 200
        wait_store_carzone_events.wait_call()

    events = db.geofence_events.find()
    drivers_updates = {}
    for event in events:
        if event['uuid'] not in drivers_updates:
            drivers_updates[event['uuid']] = 0
        if event['event_type'] == 'update':
            drivers_updates[event['uuid']] += 1
    for uuid in drivers_updates:
        assert drivers_updates[uuid] <= 1
