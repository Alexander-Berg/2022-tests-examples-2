# pylint: disable=import-error
import datetime
import math

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

TRACKS_CHANNEL = 'channel:yagr:position'
FULL_GEOMETRY_CHANNEL = 'channel:drw:full_geometry_positions'
EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'


def _get_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'timestamp': timestamp,
            'speed': 11.666666666666668,
            'accuracy': 1,
            'source': 'Gps',
        },
    ]
    return geobus.serialize_positions_v2(drivers, now)


def _get_edge_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'timestamp': timestamp * 1000,
        },
    ]
    return geobus.serialize_edge_positions_v2(drivers, now)


def check_raw_point(pos, lat, lon, accuracy, timestamp, speed, direction):
    assert pos['direction'] == direction
    assert pos['lat'] == lat
    assert pos['lon'] == lon
    assert pos['accuracy'] == accuracy
    assert pos['timestamp'] == int(utils.timestamp(timestamp))
    assert math.isclose(pos['speed'], speed, abs_tol=0.00001)


def check_adjusted_point(pos, lat, lon, timestamp, direction):
    assert pos['direction'] == direction
    assert pos['lat'] == lat
    assert pos['lon'] == lon
    assert pos['timestamp'] == int(utils.timestamp(timestamp))


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_not_found(taxi_driver_trackstory_adv):
    request_body = {'driver_id': 'dbid_uuid1', 'type': 'both'}
    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json=request_body,
    )
    assert response.status_code == 404
    data = response.json()
    assert (
        data['message']
        == 'There is no shorttrack for driver with id : dbid_uuid1'
    )


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_raw(
        taxi_driver_trackstory_adv, redis_store, now, testpoint,
):
    driver_id = 'sdbid_uuid_0'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['raw']) == 2
    assert data.get('adjusted') is None

    raw_track = data['raw']
    check_raw_point(
        raw_track[0],
        lat=37.0,
        lon=55.0,
        accuracy=1.0,
        timestamp=timestamp2,
        speed=11.666666666666668,
        direction=45.0,
    )
    check_raw_point(
        raw_track[1],
        lat=37.0,
        lon=55.0,
        accuracy=1.0,
        timestamp=timestamp,
        speed=11.666666666666668,
        direction=45.0,
    )


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/shorttrack': 100})
async def test_usage_internal_trackstory(
        taxi_driver_trackstory_adv, redis_store, mockserver, now, testpoint,
):

    dbid = 'sdbid'
    uuid = 'uuid_0'
    driver_id = dbid + '_' + uuid

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)

    @mockserver.json_handler('/internal-trackstory/taxi/shorttrack')
    def _mock_internal_trackstory(request):
        assert request.query['dbid'] == dbid
        assert request.query['uuid'] == uuid
        return [
            {
                'contractor': {'uuid': uuid, 'dbid': dbid},
                'Verified': [
                    {
                        'timestamp': int(utils.timestamp(timestamp2)) * 1000,
                        'sensors': [],
                        'geodata': [
                            {
                                'positions': [
                                    {
                                        'position': [2.0, 2.0],
                                        'speed': 2.0,
                                        'accuracy': 2.0,
                                        'direction': 2.0,
                                    },
                                ],
                                'time_shift': 0,
                            },
                        ],
                    },
                    {
                        'timestamp': int(utils.timestamp(timestamp)) * 1000,
                        'sensors': [],
                        'geodata': [
                            {
                                'positions': [
                                    {
                                        'position': [1.0, 1.0],
                                        'speed': 1.0,
                                        'accuracy': 1.0,
                                        'direction': 1.0,
                                    },
                                ],
                                'time_shift': 0,
                            },
                        ],
                    },
                ],
            },
        ]

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['raw']) == 2
    assert data.get('adjusted') is None

    raw_track = data['raw']
    check_raw_point(
        raw_track[0],
        lat=2.0,
        lon=2.0,
        accuracy=2.0,
        timestamp=timestamp2,
        speed=2.0,
        direction=2.0,
    )
    check_raw_point(
        raw_track[1],
        lat=1.0,
        lon=1.0,
        accuracy=1.0,
        timestamp=timestamp,
        speed=1.0,
        direction=1.0,
    )


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'full_geometry': {
            'enabled': True,
            'storage': {'max_age_seconds': 150, 'max_points_count': 50},
        },
    },
)
async def test_found_full_geometry(
        taxi_driver_trackstory_adv, redis_store, now, testpoint,
):
    driver_id = 'dbid1_uuid1'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        FULL_GEOMETRY_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        FULL_GEOMETRY_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'full-geometry'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['full_geometry']) == 2
    assert data.get('raw') is None
    assert data.get('adjusted') is None

    full_geometry_track = data['full_geometry']
    check_raw_point(
        full_geometry_track[0],
        lat=37.0,
        lon=55.0,
        accuracy=1.0,
        timestamp=timestamp2,
        speed=11.666666666666668,
        direction=45.0,
    )
    check_raw_point(
        full_geometry_track[1],
        lat=37.0,
        lon=55.0,
        accuracy=1.0,
        timestamp=timestamp,
        speed=11.666666666666668,
        direction=45.0,
    )


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_adjusted(
        taxi_driver_trackstory_adv, redis_store, now, testpoint,
):
    driver_id = 'sdbid_uuid_1'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(driver_id, timestamp)

    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get('raw') is None
    assert len(data['adjusted']) == 2

    adjusted_track = data['adjusted']
    check_adjusted_point(
        adjusted_track[0],
        lat=37.0,
        lon=55.0,
        timestamp=timestamp2,
        direction=0.0,
    )
    check_adjusted_point(
        adjusted_track[1],
        lat=37.0,
        lon=55.0,
        timestamp=timestamp,
        direction=0.0,
    )


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_adjusted_when_merge_raw(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'sdbid_uuid_77'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack',
        json={
            'driver_id': driver_id,
            'type': 'adjusted',
            'merge_last_adjust_with_raw_position': True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['adjusted']) == 1
    assert data.get('raw') is None


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_both(taxi_driver_trackstory_adv, redis_store, now):
    driver_id = 'sdbid_uuid_2'

    # first raw point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second raw point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # first adjusted point
    message = _get_edge_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second adjusted point
    message = _get_edge_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'both'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['raw']) == 2
    assert len(data['adjusted']) == 2


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_both_raw_empty(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'sdbid_uuid_3'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'both'},
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['raw']
    assert len(data['adjusted']) == 2


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_both_adjusted_empty(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'sdbid_uuid_4'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack', json={'driver_id': driver_id, 'type': 'both'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['raw']) == 2
    assert not data['adjusted']


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_bad_type_position(taxi_driver_trackstory, now):
    response = await taxi_driver_trackstory.post(
        'shorttrack', json={'driver_id': 'driver_id', 'type': 'adjusted11'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_no_driver_id(taxi_driver_trackstory, now):
    response = await taxi_driver_trackstory.post(
        'shorttrack', json={'type': 'adjusted'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_both_with_num_positions_limit(
        taxi_driver_trackstory_adv, now,
):
    driver_id = 'sdbid_uuid_5'

    # first raw point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second raw point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # first adjusted point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second adjusted point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack',
        json={'driver_id': driver_id, 'type': 'both', 'num_positions': 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['raw']) == 1
    assert len(data['adjusted']) == 1

    # check that tracks contains most recent point.
    assert data['raw'][0]['timestamp'] == int(utils.timestamp(timestamp))
    assert data['adjusted'][0]['timestamp'] == int(utils.timestamp(timestamp))


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_types_with_num_positions_limit(taxi_driver_trackstory_adv, now):
    driver_id = 'dbid5_uuid5'

    # first raw point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second raw point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # first adjusted point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second adjusted point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack',
        json={
            'driver_id': driver_id,
            'types': ['raw', 'adjusted'],
            'num_positions': 1,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['raw']) == 1
    assert len(data['adjusted']) == 1

    # check that tracks contains most recent point.
    assert data['raw'][0]['timestamp'] == int(utils.timestamp(timestamp))
    assert data['adjusted'][0]['timestamp'] == int(utils.timestamp(timestamp))


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_failed_types(taxi_driver_trackstory_adv, now):
    driver_id = 'dbid6_uuid6'

    # first raw point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # second raw point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    # first adjusted point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(driver_id, timestamp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second adjusted point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(driver_id, timestamp2)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttrack',
        json={'driver_id': driver_id, 'types': ['both'], 'num_positions': 1},
    )
    assert response.status_code == 400
