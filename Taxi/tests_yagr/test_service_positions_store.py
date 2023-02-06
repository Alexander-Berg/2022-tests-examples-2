# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521


YAGR_OUTPUT_CHANNEL = 'channel:tracker:position'


@pytest.mark.skip()
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_service_positions_store_negative_speeds(
        taxi_yagr_adv, redis_store, testpoint,
):
    await taxi_yagr_adv.run_periodic_task(
        'driver_positions_redis_writer_publisher',
    )

    redis_listener = redis_store.pubsub()
    _subscribe(redis_listener, YAGR_OUTPUT_CHANNEL)
    _read_all(redis_listener)

    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    data = {
        'clid': '10001',
        'park_id': 'zxcvb',
        'driver_id': 'qwerty',
        'device_id': '0000000000001',
        'source': 'N',
        'points': [
            {
                'lat': 55.720404,
                'lon': 37.523276,
                'angle': 238.4,
                'speed': -7,
                'time': 1516041552,
            },
        ],
    }
    response = await taxi_yagr_adv.post('/service/positions/store', json=data)
    assert response.status_code == 200
    assert response.json() == {}
    data = await testpoint_clid.wait_call()

    # Check here for clid empty field
    assert 'clid=\t' in data['data']['tskv']

    # check after all processing is done
    redis_message = _get_message(redis_listener, redis_store)
    # print(redis_message)
    positions = geobus.deserialize_positions(redis_message['data'])
    no_speed = -1
    assert positions[0]['speed'] == no_speed


@pytest.mark.xfail
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_service_positions_store(
        taxi_yagr_adv, redis_store, mockserver, testpoint,
):
    redis_listener = redis_store.pubsub()
    _subscribe(redis_listener, YAGR_OUTPUT_CHANNEL)
    _read_all(redis_listener)

    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    data = {
        'clid': '10001',
        'park_id': 'zxcvb',
        'driver_id': 'qwerty',
        'device_id': '0000000000001',
        'source': 'N',
        'points': [
            {
                'lat': 55.720404,
                'lon': 37.523276,
                'angle': 238.4,
                'speed': 58.5,
                'time': 1516041552,
            },
            {
                'lat': 55.710404,
                'lon': 37.513276,
                'angle': 238.4,
                'speed': 58.5,
                'time': 1516041551,
            },
            {
                'lat': 55.730404,
                'lon': 37.533276,
                'angle': 238.4,
                'speed': 58.5,
                'time': 1516041553,
            },
        ],
    }
    response = await taxi_yagr_adv.post('/service/positions/store', json=data)
    assert response.status_code == 200
    assert response.json() == {}
    data = await testpoint_clid.wait_call()

    # Check here for clid empty field
    assert 'clid=\t' in data['data']['tskv']

    # check after all processing is done
    redis_message = _get_message(redis_listener, redis_store)
    assert redis_message is not None

    latest = redis_store.get('latest')
    assert latest is not None
    hours_dt = datetime.datetime(
        2019,
        9,
        11,
        13,
        0,
        0,
        tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
    )
    hours_ts = hours_dt.timestamp()
    assert float(latest) == hours_ts

    keys = redis_store.keys('*zxcvb*')
    assert keys == [b'data/zxcvb/qwerty/20190911/10']

    hkeys = redis_store.hkeys(keys[0])
    assert len(hkeys) == 1

    hkey = hkeys[0]
    hours_dt = datetime.datetime(
        2019,
        9,
        11,
        13,
        42,
        15,
        tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
    )
    hours_ts = hours_dt.timestamp()
    assert float(int(hkey) / 1000000) == hours_ts


def _subscribe(listener, channel, try_count=30):
    for _ in range(try_count):
        listener.subscribe(channel)
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'subscribe':
            return
    # failed to subscribe
    assert False


def _get_message(
        listener,
        redis_store,
        retry_channel=None,
        max_tries=30,
        retry_message=None,
):
    # wait while yaga-dispatcher pass messages to output channel
    for _ in range(max_tries):
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'message':
            return message
        if retry_channel is not None and retry_message is not None:
            redis_store.publish(retry_channel, retry_message)
    return None


def _read_all(listener):
    # Get all messages from channel
    for _ in range(3):
        while listener.get_message(timeout=0.2) is not None:
            print('**********')
