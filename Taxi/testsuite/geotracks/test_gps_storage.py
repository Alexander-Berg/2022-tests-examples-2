import calendar
import datetime
import json
import time

import pytest

from taxi_tests import utils


# test that it returns a correct error code in case some(or all)
# params are missing
def test_noparams(taxi_geotracks):
    response = taxi_geotracks.get('gps-storage/set')
    assert response.status_code == 400


# test if it can handle unabridged queries from gps/set
# though most of the params are ignored, it should find everyting it needs in
#  this query
# note the usage of db and driverId parameters
def test_params_gps_set(taxi_geotracks):
    response = taxi_geotracks.get(
        'gps-storage/set?proxy_block_id=default&device_id=868359027690032&'
        'session=ec3c1728ecb24513835856aa2f2587ae'
        '&db=49817b28801f4350b6b9d8855fd398d7&'
        'driverId=7b243a6dab0c4750a886c902122885a4&provider=gps&'
        'lat=55.045795&lon=82.90258999999999&angel=61.22&accuracy=2.6'
        '&altitude=137.3&speed=0&timeGpsOrig=1503511094000&'
        'timeSystemOrig=1503511056908&timeSystemSync=1503511106341&cost=86.0&'
        'deviceId=868359027690032&wifi=false&isBad=false&'
        'isFake=false&status=2&'
        'order=b03a46c9c9bf41bd8d9029b40b70e54c&orderStatus=5'
        '&orderType=2&isHomeEnabled=false',
    )
    assert response.status_code == 200
    assert response.text == '{"result":"OK"}'


# test that a minimal set of parameters is enough
def test_params_min(taxi_geotracks, redis_store):
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=49817b28801f4350b6b9d8855fd398d7'
        '&driver_id=7b243a6dab0c4750a886c902122885a4'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200
    assert response.text == '{"result":"OK"}'
    assert len(redis_store.keys('*7b243a6dab0c4750a886c902122885a4*')) == 1


@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_set_from_the_past(taxi_geotracks, redis_store):
    t = datetime.datetime(2017, 9, 30, 9, 30, 0)
    strt = str(int(time.mktime(t.timetuple())))
    redis_store.delete('latest')
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=fff'
        '&driver_id=fff'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0&time=' + strt,
    )

    assert response.status_code == 200
    assert redis_store.get('latest') is not None
    assert isinstance(redis_store.get('latest'), bytes)

    t2 = datetime.datetime(2016, 9, 30, 9, 30, 0)
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=fff'
        '&driver_id=fff'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0&time=' + str(int(time.mktime(t2.timetuple()))),
    )

    assert response.status_code == 400
    hour_dt = datetime.datetime(2017, 9, 30, 9, 0, 0)
    hour_ts = time.mktime(hour_dt.timetuple())
    assert float(redis_store.get('latest')) == hour_ts


@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_set_from_the_future(taxi_geotracks, redis_store):
    t = datetime.datetime(2018, 9, 30, 9, 30, 0)
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=fff'
        '&driver_id=fff'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0&time=' + str(int(time.mktime(t.timetuple()))),
    )
    assert response.status_code == 400


@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_set_from_near_future(taxi_geotracks, redis_store):
    t = datetime.datetime(2017, 9, 30, 9, 40, 0)
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=fff'
        '&driver_id=fff'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0&time=' + str(int(time.mktime(t.timetuple()))),
    )
    assert response.status_code == 200


def test_read_no_params(taxi_geotracks, redis_store, mockserver):
    response = taxi_geotracks.get(
        'gps-storage/get?' '&driver_id=42' '&last=10',  # no db_id
    )
    assert response.status_code != 200

    response = taxi_geotracks.get(
        'gps-storage/get?' '&db_id=0' '&last=10',  # no driver_id
    )
    assert response.status_code != 200

    response = taxi_geotracks.get(
        'gps-storage/get?' '&db_id=0' '&driver_id=42',  # no from/to
    )
    assert response.status_code != 200


# test that we can read what we wrote
@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_read(taxi_geotracks, redis_store, mockserver):
    # setup
    params = {
        'lat': 55.045795,
        'lon': 82.90258999999999,
        'bearing': 61.22,
        'status': 4,
        'order_status': 5,
    }
    taxi_geotracks.get(
        'gps-storage/set?'
        '&db=0'
        '&driverId=42'
        '&lat={lat}&lon={lon}&bearing={bearing}'
        '&status={status}&order_status={order_status}'
        '&speed=0'.format(**params),
    )
    # perform get
    response = taxi_geotracks.get(
        'gps-storage/get?' '&db_id=0' '&driver_id=42' '&last=10&verbose=1',
        # note that we must use such a value of 'last' so we don't need to
        # read from mds
    )
    assert response.status_code == 200
    js = json.loads(response.text)
    assert js['track'] is not None
    assert len(js['track']) == 1
    item = js['track'][0]

    eps = 1e-5  # note that there is the internal rep is 32-bit float

    assert abs(item['bearing'] - params['bearing']) < eps
    assert item['end'] is not None
    assert item['point'] is not None
    assert abs(item['point'][0] - params['lon']) < eps
    assert abs(item['point'][1] - params['lat']) < eps
    assert item['speed'] is not None
    assert item['timestamp'] is not None
    assert int(item['status']) == params['status']
    assert int(item['order_status']) == params['order_status']


def test_read2(taxi_geotracks, mockserver, redis_store):
    # setup
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=42'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200

    now = datetime.datetime.utcnow()
    date = (now - datetime.timedelta(days=1)).strftime('%Y%m%d')

    stats = {'s3_calls': 0}

    # mock the list operation
    # it returns that there is one item available in mds in the current data
    # namely data/0/42/${date}/0
    # and nothing (and no valid xml) for every other date
    # so we test here that
    # 1. correct xml gets parsed, the item from the xml gets requested
    # 2. if ListBucketResult is not a valid xml, we just consider it empty
    @mockserver.handler('/s3mds/')
    def mock_geotracks_list(request):
        if request.method == 'GET' and request.args['prefix'].endswith(date):
            resp = (
                '<ListBucketResult >'
                '<Name>testsuite</Name>'
                '<Prefix>data/0/42/{0}</Prefix>'
                '<Contents>'
                '<Key>data/0/42/{0}/0</Key>'
                '<Size>2184</Size></Contents></ListBucketResult>'
            )
            return mockserver.make_response(resp.format(date), 200)
        return mockserver.make_response('', 200)

    # checks that the item from mock_geotracks_list gets requested
    @mockserver.handler('/s3mds/data/0/42/' + date + '/0')
    def mock_geotracks(request):
        stats['s3_calls'] += 1
        return mockserver.make_response('', 200)

    # perform get
    response = taxi_geotracks.get(
        'gps-storage/get?'
        '&db_id=0'
        '&driver_id=42'
        '&last=172800',  # more than fits to redis, more than one day
    )

    assert response.status_code == 200
    js = json.loads(response.text)

    # should have only one item because mds mock returns rubbish
    # tests also that nothing fails in case of mds errors or data corruption
    assert js['track'] is not None
    assert len(js['track']) == 1
    item = js['track'][0]
    assert item['bearing'] is not None
    assert item['end'] is not None
    assert item['point'] is not None
    assert item['speed'] is not None
    assert item['timestamp'] is not None
    assert stats['s3_calls'] == 1


def test_stat(taxi_geotracks):
    response = taxi_geotracks.get('stats')
    assert response.status_code == 200
    js = json.loads(response.text)  # should not raise
    assert js is not None


@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_read3(taxi_geotracks, redis_store, mockserver):
    # setup
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=42'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200

    # perform get
    response = taxi_geotracks.get(
        'gps-storage/get?' '&db_id=0' '&driver_id=42' '&last=60',
        # note that we must use such a value of 'last' so we don't need to
        # read from mds
    )
    assert response.status_code == 200
    js = json.loads(response.text)
    assert js['track'] is not None
    assert len(js['track']) == 1


@pytest.mark.now('2017-09-30T12:30:00+0300')
@pytest.mark.config(GEOTRACKS_READER_MAX_DURATION_REQUEST_TIME_HOURS=1)
@pytest.mark.parametrize(
    'from_ut, to_ut, code',
    [
        (1506763740, 1506763800, 200),
        (1506750000, 1506763800, 400),
        (1506763740, 1506778000, 200),
        (1506750000, 1506778000, 400),
        (1506778000, 1506779000, 400),
    ],
)
def test_read4(taxi_geotracks, redis_store, mockserver, from_ut, to_ut, code):
    # setup
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=42'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200

    response = taxi_geotracks.get(
        'gps-storage/get?'
        '&db_id=0'
        '&driver_id=42'
        '&from={}&to={}'.format(from_ut, to_ut),
    )
    assert response.status_code == code


@pytest.mark.now('2011-10-25T00:02:00+0000')
@pytest.mark.config(GEOTRACKS_READER_MAX_DURATION_REQUEST_TIME_HOURS=1)
@pytest.mark.parametrize(
    'from_ut, to_ut, code', [(1319400700, 1319500920, 200)],
)
def test_read5(taxi_geotracks, redis_store, mockserver, from_ut, to_ut, code):
    # setup
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=42'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200

    response = taxi_geotracks.get(
        'gps-storage/get?'
        '&db_id=0'
        '&driver_id=42'
        '&from={}&to={}'.format(from_ut, to_ut),
    )
    assert response.status_code == code


@pytest.mark.now('2017-09-30T12:30:00+0300')
@pytest.mark.config(GEOTRACKS_READER_MAX_DURATION_REQUEST_TIME_HOURS=1)
@pytest.mark.parametrize('time,code', [(100, 200), (8000, 400)])
def test_read6(taxi_geotracks, redis_store, mockserver, time, code):
    # setup
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=42'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200

    response = taxi_geotracks.get(
        'gps-storage/get?' '&db_id=0' '&driver_id=42' '&last={}'.format(time),
    )
    assert response.status_code == code


@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_read_multi_wrong_params(taxi_geotracks, redis_store, mockserver):
    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json', json={},
    )
    assert response.status_code == 400

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json', json={'params': []},
    )
    assert response.status_code == 200

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json', json={'params': [{}]},
    )
    assert response.status_code == 200
    assert 'error' in json.loads(response.text)['tracks'][0]

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={'params': [{'last': 60, 'driver_id': '43'}]},
    )
    assert response.status_code == 200
    assert 'error' in json.loads(response.text)['tracks'][0]

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={'params': [{'last': 60, 'db_id': '0'}]},
    )
    assert response.status_code == 200
    assert 'error' in json.loads(response.text)['tracks'][0]

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={'params': [{'driver_id': '43', 'db_id': '0'}]},
    )
    assert response.status_code == 200
    assert 'error' in json.loads(response.text)['tracks'][0]

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={'params': [{'from': 42, 'driver_id': '43', 'db_id': '0'}]},
    )
    assert response.status_code == 200
    assert 'error' in json.loads(response.text)['tracks'][0]

    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={
            'params': [
                {'from': '42', 'to': 43, 'driver_id': '43', 'db_id': '0'},
            ],
        },
    )
    assert response.status_code == 200
    assert 'error' in json.loads(response.text)['tracks'][0]


@pytest.mark.now('2017-09-30T12:30:00+0300')
def test_read_multi(taxi_geotracks, redis_store, mockserver):
    # setup
    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=42'
        '&lat=55.045795&lon=82.90258999999999&angel=61.22'
        '&speed=0',
    )
    assert response.status_code == 200

    response = taxi_geotracks.get(
        'gps-storage/set?'
        '&db_id=0'
        '&driver_id=43'
        '&lat=65.045795&lon=72.90258999999999&angel=1.22'
        '&speed=10',
    )
    assert response.status_code == 200

    # perform get
    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={
            'params': [
                {'last': 60, 'driver_id': '43', 'db_id': '0'},
                {'last': 60, 'driver_id': '42', 'db_id': '0'},
            ],
        },
    )

    def find_driver_result(js, driver_id):
        for x in js:
            if x['driver_id'] == driver_id:
                return x
        return None

    assert response.status_code == 200
    js = json.loads(response.text)
    assert js['tracks'] is not None
    assert len(js['tracks']) == 2
    assert find_driver_result(js['tracks'], '42') is not None
    assert find_driver_result(js['tracks'], '43') is not None

    # empty mds
    @mockserver.handler('/s3mds/')
    def mock_geotracks_list(request):
        return mockserver.make_response('', 200)

    @mockserver.handler('/s3mds/data/0/---/20170930/9')
    def mock_geotracks(request):
        return mockserver.make_response('', 200)

    # one existing and one non-existing driver
    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={
            'params': [
                {'last': 60, 'driver_id': '43', 'db_id': '0'},
                {'last': 60, 'driver_id': '---', 'db_id': '0'},
            ],
        },
    )

    assert response.status_code == 200
    js = json.loads(response.text)
    assert js['tracks'] is not None
    assert len(js['tracks']) == 2
    assert find_driver_result(js['tracks'], '43') is not None
    driver_ne = find_driver_result(js['tracks'], '---')
    assert driver_ne is not None
    assert len(driver_ne['track']) == 0

    # one good request, one malformed
    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={
            'params': [
                {'last': 60, 'driver_id': '43', 'db_id': '0'},
                {'from': 2, 'to': 1, 'driver_id': '42', 'db_id': '0'},
            ],
        },
    )

    assert response.status_code == 200
    js = json.loads(response.text)
    assert js['tracks'] is not None
    assert len(js['tracks']) == 2
    assert find_driver_result(js['tracks'], '43') is not None
    driver_ne = find_driver_result(js['tracks'], '42')
    assert driver_ne is not None
    assert 'track' not in driver_ne
    assert len(driver_ne['error']) != 0

    # use from and to
    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json',
        json={
            'params': [
                {
                    'from': 1506763740,
                    'to': 1506763800,
                    'driver_id': '43',
                    'db_id': '0',
                },
            ],
        },
    )

    assert response.status_code == 200
    js = json.loads(response.text)
    assert js['tracks'] is not None
    assert len(js['tracks']) == 1
    assert find_driver_result(js['tracks'], '43') is not None


@pytest.mark.now('2017-09-30T12:30:00+0300')
@pytest.mark.config(
    GEOTRACKS_ARCHIVER_SIMPLIFY_EPSILON=0.0001,
    GEOTRACKS_WRITER_GPS_STORAGE_SET_REDIS_COMMAND_CONTROL={
        'max_retries': 5,
        'timeout_single_ms': 1000,
        'timeout_all_ms': 5000,
    },
)
def test_read_adjust(
        taxi_geotracks, redis_store, mockserver, load_binary, load_json,
):
    @mockserver.handler('/s3mds/')
    def mock_geotracks_list(request):
        return mockserver.make_response('', 200)

    track = load_json('track_orig.json')
    i = 0
    t = datetime.datetime(2017, 9, 30, 9, 30, 0)
    for x in track:
        t = datetime.datetime(2017, 9, 30, 9, 30, 0)
        t += datetime.timedelta(seconds=i)
        taxi_geotracks.post('tests/control', {'now': utils.timestring(t)})

        ll_str = '&lat=%s&lon=%s' % (x['lat'], x['lon'])
        response = taxi_geotracks.get(
            'gps-storage/set?'
            '&db_id=0'
            '&driver_id=42' + ll_str + '&speed=0&angel=0',
        )
        assert response.status_code == 200
        i += 1
    to = calendar.timegm(t.utctimetuple())
    response = taxi_geotracks.post(
        'gps-storage/get?request_type=json&preprocess=6',
        json={
            'params': [
                {
                    'from': 1506763740,
                    'to': to,
                    'driver_id': '42',
                    'db_id': '0',
                    'preprocess': 6,
                },
            ],
        },
    )

    assert response.status_code == 200
    js = json.loads(response.text)['tracks']
    for x in js[0]['track']:
        assert int(x['timestamp']) != 0
        assert float(x['point'][0]) != 0.0
        assert float(x['point'][1]) != 0.0
    # TODO: return checking after implementation of repair track
    # assert len(js[0]['track']) == 72
