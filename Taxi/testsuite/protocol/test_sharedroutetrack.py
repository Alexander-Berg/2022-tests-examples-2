from datetime import datetime
import json
import math

import pytest
import pytz


@pytest.mark.now('2017-01-01T12:00:00+0000')
def test_history(taxi_protocol, mockserver, load_json):

    shorttrack = load_json('shorttrack.json')

    @mockserver.json_handler('/tracker/shorttrack')
    def mock_shorttrack(request):
        return shorttrack

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': 'key_taxi_waiting',
        'timestamp': '2017-01-01T00:00:00.000Z',
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)

    assert response.status_code == 200
    resp = response.json()

    _check_track(
        resp['track'],
        [_to_sharedroutepoint(i) for i in shorttrack['positions']],
    )
    assert resp['driver'] == _to_sharedroutepoint(shorttrack['positions'][0])


@pytest.mark.now('2017-01-01T12:00:00+0000')
@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
def test_history_driver_trackstory(taxi_protocol, mockserver, load_json):

    shorttrack = load_json('shorttrack.json')

    @mockserver.json_handler('/driver_trackstory/shorttrack')
    def mock_shorttrack(request):
        return {'adjusted': shorttrack['positions'][::-1]}

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': 'key_taxi_waiting',
        'timestamp': '2017-01-01T00:00:00.000Z',
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)

    assert response.status_code == 200
    resp = response.json()

    _check_track(
        resp['track'],
        [_to_sharedroutepoint(i) for i in shorttrack['positions']],
    )
    assert resp['driver'] == _to_sharedroutepoint(shorttrack['positions'][0])


@pytest.mark.now('2017-01-01T12:00:00+0000')
@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
def test_history_driver_trackstory_404(taxi_protocol, mockserver, load_json):
    @mockserver.json_handler('/driver_trackstory/shorttrack')
    def mock_shorttrack(request):
        return mockserver.make_response(status=404)

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': 'key_taxi_waiting',
        'timestamp': '2017-01-01T00:00:00.000Z',
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)

    assert response.status_code == 304


@pytest.mark.parametrize(
    'order_key, client_driver_index, track_indexes,'
    'completed_route_indexes, intended_route_indexes',
    [
        ('key_taxi_complete', 1, [], [4, 3, 2, 1], []),
        ('key_taxi_cancelled', 1, [], [], []),
        ('key_taxi_transporting', 2, [0, 1, 2], [4, 3, 2, 1, 0], [2]),
        ('key_taxi_waiting', 3, [0, 1, 2, 3], [], [0, 1, 2]),
    ],
)
@pytest.mark.now('2017-01-01T00:00:00+0000')
def test_fullroute(
        taxi_protocol,
        mockserver,
        load_json,
        order_key,
        client_driver_index,
        track_indexes,
        completed_route_indexes,
        intended_route_indexes,
):

    shorttrack = load_json('shorttrack.json')
    route = load_json('route.json')

    @mockserver.json_handler('/tracker/position')
    def mock_get_position(request):
        return shorttrack['positions'][0]

    @mockserver.json_handler('/tracker/shorttrack')
    def mock_shorttrack(request):
        return shorttrack

    @mockserver.json_handler('/geotracks/gps-storage/get')
    def mock_geotracks(request):
        body = json.loads(list(request.form.keys())[0])
        track = []
        for p in shorttrack['positions'][::-1]:
            if (
                    p['timestamp'] >= body['params'][0]['from']
                    and p['timestamp'] <= body['params'][0]['to']
            ):
                track.append(_to_geotrackpoint(p))
        return {'tracks': [{'req_id': 0, 'track': track}]}

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        body = json.loads(list(request.form.keys())[0])
        path = [
            [
                shorttrack['positions'][0]['lon'],
                shorttrack['positions'][0]['lat'],
            ],
        ]
        path.extend(body['path'])
        return {
            'duration': 100,
            'smooth_duration': 99,
            'distance': 100,
            'driver_position': path[0],
            'path': path,
        }

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': order_key,
        'timestamp': _to_timestamp(
            shorttrack['positions'][client_driver_index]['timestamp'],
        ),
        'use_full_route': True,
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)

    if order_key == 'key_taxi_cancelled':
        assert response.status_code == 204
        return

    assert response.status_code == 200
    resp = response.json()

    if len(track_indexes):
        _check_track(
            resp['track'],
            [
                _to_sharedroutepoint(shorttrack['positions'][i])
                for i in track_indexes
            ],
        )
        assert resp['driver'] == _to_sharedroutepoint(
            shorttrack['positions'][track_indexes[0]],
        )
    else:
        assert 'track' not in resp
        assert 'driver' not in resp

    if len(completed_route_indexes):
        assert resp['completed_route'] == [
            _to_routepoint(shorttrack['positions'][i])
            for i in completed_route_indexes
        ]
    else:
        assert 'complete_route' not in resp

    if len(intended_route_indexes):
        intended_route = [
            _to_routepoint(shorttrack['positions'][track_indexes[0]]),
        ]
        intended_route.extend([route[i] for i in intended_route_indexes])
        assert resp['intended_route'] == intended_route
    else:
        assert 'intended_route' not in resp
        assert 'intended_duration' not in resp
        assert 'intended_distance' not in resp


@pytest.mark.config(SHARED_ROUTE_TRACK_USE_DRW=100)
@pytest.mark.parametrize(
    'order_key, client_driver_index, track_indexes,'
    'completed_route_indexes, intended_route_indexes',
    [
        ('key_taxi_complete', 1, [], [4, 3, 2, 1], []),
        ('key_taxi_cancelled', 1, [], [], []),
        ('key_taxi_transporting', 2, [0, 1, 2], [4, 3, 2, 1, 0], [2]),
        ('key_taxi_waiting', 3, [0, 1, 2, 3], [], [0, 1, 2]),
    ],
)
@pytest.mark.now('2017-01-01T00:00:00+0000')
def test_fullroute_with_drw(
        taxi_protocol,
        mockserver,
        load_json,
        order_key,
        client_driver_index,
        track_indexes,
        completed_route_indexes,
        intended_route_indexes,
):

    shorttrack = load_json('shorttrack.json')
    route = load_json('route.json')

    @mockserver.json_handler('/tracker/position')
    def mock_get_position(request):
        return shorttrack['positions'][0]

    @mockserver.json_handler('/tracker/shorttrack')
    def mock_shorttrack(request):
        return shorttrack

    @mockserver.json_handler('/geotracks/gps-storage/get')
    def mock_geotracks(request):
        body = json.loads(list(request.form.keys())[0])
        track = []
        for p in shorttrack['positions'][::-1]:
            if (
                    p['timestamp'] >= body['params'][0]['from']
                    and p['timestamp'] <= body['params'][0]['to']
            ):
                track.append(_to_geotrackpoint(p))
        return {'tracks': [{'req_id': 0, 'track': track}]}

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        del request
        assert False

    @mockserver.json_handler('/driver_route_responder/timeleft')
    def mock_drw_timeleft(request):
        path = [
            [
                shorttrack['positions'][0]['lon'],
                shorttrack['positions'][0]['lat'],
            ],
        ]
        # drw know about statuses and destination points
        path.extend([route[i] for i in intended_route_indexes])
        return {
            'time_left': 99,
            'distance_left': 100,
            'position': path[0],
            'destination': path[-1],
            'tracking_type': 'route_tracking',
            'route': path,
        }

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': order_key,
        'timestamp': _to_timestamp(
            shorttrack['positions'][client_driver_index]['timestamp'],
        ),
        'use_full_route': True,
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)

    if order_key == 'key_taxi_cancelled':
        assert response.status_code == 204
        return

    assert response.status_code == 200
    resp = response.json()

    if len(track_indexes):
        _check_track(
            resp['track'],
            [
                _to_sharedroutepoint(shorttrack['positions'][i])
                for i in track_indexes
            ],
        )
        assert resp['driver'] == _to_sharedroutepoint(
            shorttrack['positions'][track_indexes[0]],
        )
    else:
        assert 'track' not in resp
        assert 'driver' not in resp

    if len(completed_route_indexes):
        assert resp['completed_route'] == [
            _to_routepoint(shorttrack['positions'][i])
            for i in completed_route_indexes
        ]
    else:
        assert 'complete_route' not in resp

    if len(intended_route_indexes):
        intended_route = [
            _to_routepoint(shorttrack['positions'][track_indexes[0]]),
        ]
        intended_route.extend([route[i] for i in intended_route_indexes])
        assert resp['intended_route'] == intended_route
    else:
        assert 'intended_route' not in resp
        assert 'intended_duration' not in resp
        assert 'intended_distance' not in resp


@pytest.mark.parametrize(
    'order_key, client_driver_index, track_indexes,'
    'completed_route_indexes, intended_route_indexes',
    [
        ('key_taxi_transporting', 2, [0, 1, 2], [4, 3, 2, 1, 0], [2]),
        ('key_taxi_waiting', 3, [0, 1, 2, 3], [], [0, 1, 2]),
    ],
)
@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
@pytest.mark.now('2017-01-01T00:00:00+0000')
def test_fullroute_driver_trackstory(
        taxi_protocol,
        mockserver,
        load_json,
        order_key,
        client_driver_index,
        track_indexes,
        completed_route_indexes,
        intended_route_indexes,
):

    shorttrack = load_json('shorttrack.json')
    route = load_json('route.json')

    @mockserver.json_handler('/driver_trackstory/position')
    def mock_get_position(request):
        return {'position': shorttrack['positions'][0], 'type': 'raw'}

    @mockserver.json_handler('/geotracks/gps-storage/get')
    def mock_geotracks(request):
        body = json.loads(list(request.form.keys())[0])
        track = []
        for p in shorttrack['positions'][::-1]:
            if (
                    p['timestamp'] >= body['params'][0]['from']
                    and p['timestamp'] <= body['params'][0]['to']
            ):
                track.append(_to_geotrackpoint(p))
        return {'tracks': [{'req_id': 0, 'track': track}]}

    @mockserver.json_handler('/tracker/smooth-routing')
    def mock_smooth_routing(request):
        body = json.loads(list(request.form.keys())[0])
        path = [
            [
                shorttrack['positions'][0]['lon'],
                shorttrack['positions'][0]['lat'],
            ],
        ]
        path.extend(body['path'])
        return {
            'duration': 100,
            'smooth_duration': 99,
            'distance': 100,
            'driver_position': path[0],
            'path': path,
        }

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': order_key,
        'timestamp': _to_timestamp(
            shorttrack['positions'][client_driver_index]['timestamp'],
        ),
        'use_full_route': True,
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)

    if order_key == 'key_taxi_cancelled':
        assert response.status_code == 204
        return

    assert response.status_code == 200
    resp = response.json()

    if len(track_indexes):
        _check_track(
            resp['track'],
            [
                _to_sharedroutepoint(shorttrack['positions'][i])
                for i in track_indexes
            ],
        )
        assert resp['driver'] == _to_sharedroutepoint(
            shorttrack['positions'][track_indexes[0]],
        )
    else:
        assert 'track' not in resp
        assert 'driver' not in resp

    if len(completed_route_indexes):
        assert resp['completed_route'] == [
            _to_routepoint(shorttrack['positions'][i])
            for i in completed_route_indexes
        ]
    else:
        assert 'complete_route' not in resp

    if len(intended_route_indexes):
        intended_route = [
            _to_routepoint(shorttrack['positions'][track_indexes[0]]),
        ]
        intended_route.extend([route[i] for i in intended_route_indexes])
        assert resp['intended_route'] == intended_route
    else:
        assert 'intended_route' not in resp
        assert 'intended_duration' not in resp
        assert 'intended_distance' not in resp


@pytest.mark.config(USE_DRIVER_TRACKSTORY_PERCENT=100)
@pytest.mark.now('2017-01-01T00:00:00+0000')
def test_position_404(taxi_protocol, mockserver, load_json):
    @mockserver.json_handler('/driver_trackstory/position')
    def mock_get_position(request):
        return mockserver.make_response(
            json.dumps({'message': 'Something bad happened'}), 404,
        )

    request = {
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'key': 'key_taxi_transporting',
        'timestamp': '2017-01-01T00:00:00.000Z',
        'use_full_route': True,
    }

    response = taxi_protocol.post('3.0/sharedroutetrack', request)
    assert response.status_code == 404


def _to_geotrackpoint(shorttrackpoint):
    return {
        'timestamp': shorttrackpoint['timestamp'],
        'bearing': shorttrackpoint['direction'],
        'point': [shorttrackpoint['lon'], shorttrackpoint['lat']],
        'speed': shorttrackpoint['speed'],
    }


def _to_timestamp(unixtime):
    tz = pytz.timezone('Europe/Moscow')
    isoformat = '%Y-%m-%dT%H:%M:%S.%f%z'
    return datetime.fromtimestamp(unixtime, tz).strftime(isoformat)


def _to_sharedroutepoint(shorttrackpoint):
    return {
        'timestamp': _to_timestamp(shorttrackpoint['timestamp']),
        'direction': shorttrackpoint['direction'],
        'speed': shorttrackpoint['speed'],
        'coordinates': [shorttrackpoint['lon'], shorttrackpoint['lat']],
    }


def _to_routepoint(shorttrackpoint):
    return [shorttrackpoint['lon'], shorttrackpoint['lat']]


def _check_track(resp_track, sample_track):
    assert len(resp_track) == len(sample_track)
    resp_track = resp_track[::-1]
    sample_track = sample_track[::-1]
    for i in range(len(resp_track)):
        assert resp_track[i]['timestamp'] == sample_track[i]['timestamp']
        assert resp_track[i]['speed'] == sample_track[i]['speed']
        assert resp_track[i]['coordinates'] == sample_track[i]['coordinates']
        if i != len(resp_track) - 1:
            sample_dir = _get_direction(
                sample_track[i]['coordinates'],
                sample_track[i + 1]['coordinates'],
            )
        assert math.fabs(resp_track[i]['direction'] - sample_dir) < 0.1


def _get_direction(point1, point2):
    mpoint1 = _geo_to_merc(point1)
    mpoint2 = _geo_to_merc(point2)
    ang = (
        90.0
        - math.atan2(mpoint2[1] - mpoint1[1], mpoint2[0] - mpoint1[0])
        * 180.0
        / math.pi
    )
    if ang < 0.0:
        ang += 360.0
    return ang


def _geo_to_merc(point):
    EarthEccentricity = 0.0818191908426
    EarthEllipsoid_a = 6_378_137.0
    lon = point[0] * math.pi / 180.0
    lat = point[1] * math.pi / 180.0
    esinLat = EarthEccentricity * math.sin(lat)
    tan_tmp = math.tan(math.pi / 4.0 + lat / 2.0)
    pow_tmp = pow(
        math.tan(math.pi / 4.0 + math.asin(esinLat) / 2.0), EarthEccentricity,
    )
    x = EarthEllipsoid_a * lon
    y = EarthEllipsoid_a * math.log(tan_tmp / pow_tmp)
    return [x, y]
