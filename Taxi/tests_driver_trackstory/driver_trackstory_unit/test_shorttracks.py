# pylint: disable=import-error
import datetime
import math

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

from tests_driver_trackstory.driver_trackstory_unit import fbs_convertation

TRACKS_CHANNEL = 'channel:yagr:position'
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


def _get_edge_channel_message(driver_id, now, lon=55, lat=37):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [lon, lat],
            'timestamp': timestamp * 1000,  # milliseconds
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


async def test_not_found(taxi_driver_trackstory):
    request_body = {'driver_ids': ['dbid_uuid1'], 'type': 'both'}
    response = await taxi_driver_trackstory.post(
        'shorttracks', json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['dbid_uuid1'] == {'raw': [], 'adjusted': []}


async def test_not_found_fbs(taxi_driver_trackstory):
    request_body = {'driver_ids': ['dbid_uuid1'], 'type': 'both'}
    response = await taxi_driver_trackstory.post(
        'v2/shorttracks', json=request_body,
    )
    assert response.status_code == 200
    data = fbs_convertation.convert_fbs_to_local_repr(response.content)
    assert data['dbid_uuid1'] == {
        'raw': [],
        'adjusted': [],
        'alternatives': [],
    }


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_raw_fbs(taxi_driver_trackstory_adv, now):
    prefix = 'fbs_raw_'
    driver_id = prefix + 'adbid_uuid_0'
    driver_id2 = prefix + 'adbid_uuid_1'

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
        'v2/shorttracks',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'raw'},
    )
    assert response.status_code == 200

    data = fbs_convertation.convert_fbs_to_local_repr(response.content)
    assert len(data[driver_id]['raw']) == 2
    assert not data[driver_id]['adjusted']
    assert not data[driver_id2]['raw']
    assert not data[driver_id2]['adjusted']

    raw_track = data[driver_id]['raw']
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
@pytest.mark.config(
    PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/v2/shorttracks': 100},
)
async def test_usage_internal_trackstory_fbs(
        taxi_driver_trackstory_adv, mockserver, now,
):
    dbid = 'dbid'
    uuid1 = 'uuid1'
    uuid2 = 'uuid2'
    driver_id = dbid + '_' + uuid1
    driver_id2 = dbid + '_' + uuid2

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)

    @mockserver.json_handler('/internal-trackstory/taxi/bulk/shorttracks')
    def _mock_internal_trackstory(request):
        body = request.json
        assert body['contractor_ids'][0]['uuid'] == uuid1
        assert body['contractor_ids'][0]['dbid'] == dbid
        assert body['contractor_ids'][1]['uuid'] == uuid2
        assert body['contractor_ids'][1]['dbid'] == dbid
        return [
            {
                'contractor': {'uuid': uuid1, 'dbid': dbid},
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
            {'contractor': {'uuid': uuid2, 'dbid': dbid}},
        ]

    response = await taxi_driver_trackstory_adv.post(
        'v2/shorttracks',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'raw'},
    )
    assert response.status_code == 200

    data = fbs_convertation.convert_fbs_to_local_repr(response.content)
    assert len(data[driver_id]['raw']) == 2
    assert not data[driver_id]['adjusted']
    assert not data[driver_id2]['raw']
    assert not data[driver_id2]['adjusted']

    raw_track = data[driver_id]['raw']
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
async def test_found_raw(taxi_driver_trackstory_adv, now):
    driver_id = 'adbid_uuid_0'
    driver_id2 = 'adbid_uuid_1'

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
        'shorttracks',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data[driver_id]['raw']) == 2
    assert data[driver_id].get('adjusted') is None
    assert not data[driver_id2]['raw']
    assert data[driver_id2].get('adjusted') is None

    raw_track = data[driver_id]['raw']
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
@pytest.mark.config(PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/shorttracks': 100})
async def test_usage_internal_trackstory(
        taxi_driver_trackstory_adv, mockserver, now,
):
    dbid = 'adbid'
    uuid1 = 'uuid1'
    uuid2 = 'uuid2'
    driver_id = dbid + '_' + uuid1
    driver_id2 = dbid + '_' + uuid2

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)

    @mockserver.json_handler('/internal-trackstory/taxi/bulk/shorttracks')
    def _mock_internal_trackstory(request):
        return [
            {
                'contractor': {'uuid': uuid1, 'dbid': dbid},
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
            {'contractor': {'uuid': uuid2, 'dbid': dbid}},
        ]

    response = await taxi_driver_trackstory_adv.post(
        'shorttracks',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data[driver_id]['raw']) == 2
    assert data[driver_id].get('adjusted') is None
    assert not data[driver_id2]['raw']
    assert data[driver_id2].get('adjusted') is None

    raw_track = data[driver_id]['raw']
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
async def test_found_adjusted_fbs(taxi_driver_trackstory_adv, now):
    prefix = 'adjusted_fbs'
    driver_id = prefix + 'adbid_uuid_1'

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
        'v2/shorttracks', json={'driver_ids': [driver_id], 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = fbs_convertation.convert_fbs_to_local_repr(response.content)
    assert not data[driver_id]['raw']
    assert len(data[driver_id]['adjusted']) == 2

    adjusted_track = data[driver_id]['adjusted']
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
async def test_found_adjusted(taxi_driver_trackstory_adv, now):
    driver_id = 'adbid_uuid_1'

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
        'shorttracks', json={'driver_ids': [driver_id], 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data[driver_id].get('raw') is None
    assert len(data[driver_id]['adjusted']) == 2

    adjusted_track = data[driver_id]['adjusted']
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
async def test_found_both_fbs(taxi_driver_trackstory_adv, now):
    driver_id = 'adbid_uuid_2'

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
        'v2/shorttracks', json={'driver_ids': [driver_id], 'type': 'both'},
    )
    assert response.status_code == 200
    data = fbs_convertation.convert_fbs_to_local_repr(response.content)
    assert len(data[driver_id]['raw']) == 2
    assert len(data[driver_id]['adjusted']) == 2


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_both(taxi_driver_trackstory_adv, now):
    driver_id = 'adbid_uuid_2'

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
        'shorttracks', json={'driver_ids': [driver_id], 'type': 'both'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data[driver_id]['raw']) == 2
    assert len(data[driver_id]['adjusted']) == 2


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_closest_distance_fbs(taxi_driver_trackstory_adv, now):
    driver_id = 'testfilter_closestdistance'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(
        driver_id, timestamp, lon=55.0, lat=37.0,
    )
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(
        driver_id, timestamp2, lon=56.0, lat=38.0,
    )
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # third point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(
        driver_id, timestamp2, lon=57.0, lat=39.0,
    )
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'v2/shorttracks', json={'driver_ids': [driver_id], 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = fbs_convertation.convert_fbs_to_local_repr(response.content)
    assert data[driver_id]['raw'] == []
    # there should be 2 points, because clostest distance threshold is really
    # high
    assert len(data[driver_id]['adjusted']) == 2


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_closest_distance(taxi_driver_trackstory_adv, now):
    driver_id = 'testfilter_closestdistance'

    # first point
    timestamp = now - datetime.timedelta(seconds=30)
    message = _get_edge_channel_message(
        driver_id, timestamp, lon=55.0, lat=37.0,
    )
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # second point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(
        driver_id, timestamp2, lon=56.0, lat=38.0,
    )
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    # third point
    timestamp2 = now - datetime.timedelta(seconds=45)
    message = _get_edge_channel_message(
        driver_id, timestamp2, lon=57.0, lat=39.0,
    )
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'shorttracks', json={'driver_ids': [driver_id], 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data[driver_id].get('raw') is None
    # there should be 2 points, because clostest distance threshold is really
    # high
    assert len(data[driver_id]['adjusted']) == 2


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_bad_type_position_fbs(taxi_driver_trackstory):
    response = await taxi_driver_trackstory.post(
        'v2/shorttracks',
        json={'driver_ids': ['driver_id'], 'type': 'adjusted11'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_bad_type_position(taxi_driver_trackstory):
    response = await taxi_driver_trackstory.post(
        'shorttracks',
        json={'driver_ids': ['driver_id'], 'type': 'adjusted11'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_no_driver_ids_fbs(taxi_driver_trackstory, redis_store, now):
    response = await taxi_driver_trackstory.post(
        'v2/shorttracks', json={'type': 'adjusted'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_no_driver_ids(taxi_driver_trackstory):
    response = await taxi_driver_trackstory.post(
        'shorttracks', json={'type': 'adjusted'},
    )
    assert response.status_code == 400
