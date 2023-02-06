# pylint: disable=import-error
import math

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

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


def _get_edge_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'timestamp': timestamp * 1000,  # milliseconds
        },
    ]
    return geobus.serialize_edge_positions_v2(drivers, now)


async def test_not_found(taxi_driver_trackstory):
    request_body = {'driver_ids': ['dbid_uuid']}
    response = await taxi_driver_trackstory.post(
        'positions', json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['results']


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_raw_two_drivers(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'dbid_uuid_1'
    message = _get_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    driver_id2 = 'dbid_uuid_2'
    message2 = _get_channel_message(driver_id2, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message2,
    )

    response = await taxi_driver_trackstory_adv.post(
        'positions',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    item = data['results'][0]
    assert item['type'] == 'raw'
    assert item['driver_id'] == 'dbid_uuid_1'

    pos = item['position']
    assert pos['direction'] == 45.0
    assert pos['lat'] == 37.0
    assert pos['lon'] == 55.0
    assert pos['accuracy'] == 1.0
    assert pos['timestamp'] == 1552003200
    assert math.isclose(pos['speed'], 11.666666666666668, abs_tol=0.00001)

    item = data['results'][1]
    assert item['type'] == 'raw'
    assert item['driver_id'] == 'dbid_uuid_2'

    pos = item['position']
    assert pos['direction'] == 45.0
    assert pos['lat'] == 37.0
    assert pos['lon'] == 55.0
    assert pos['accuracy'] == 1.0
    assert pos['timestamp'] == 1552003200
    assert math.isclose(pos['speed'], 11.666666666666668, abs_tol=0.00001)


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/positions': 100})
async def test_usage_internal_trackstory(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    dbid = 'dbid'
    uuid1 = 'uuid1'
    uuid2 = 'uuid2'
    driver_id = dbid + '_' + uuid1
    driver_id2 = uuid2

    @mockserver.json_handler('/internal-trackstory/taxi/bulk/positions')
    def _mock_internal_trackstory(request):
        body = request.json
        assert body['contractor_ids'][0]['uuid'] == uuid1
        assert body['contractor_ids'][0]['dbid'] == dbid
        assert body['contractor_ids'][1]['uuid'] == uuid2
        return [
            {
                'contractor': {'uuid': uuid1, 'dbid': dbid},
                'Verified': [
                    {
                        'timestamp': 1552003222000,
                        'sensors': [],
                        'geodata': [
                            {
                                'positions': [{'position': [1.0, 1.0]}],
                                'time_shift': 0,
                            },
                        ],
                    },
                ],
                'Adjusted': [],
            },
            {
                'contractor': {'uuid': uuid2},
                'Verified': [
                    {
                        'timestamp': 1552003222000,
                        'sensors': [],
                        'geodata': [
                            {
                                'positions': [{'position': [2.0, 2.0]}],
                                'time_shift': 0,
                            },
                        ],
                    },
                ],
                'Adjusted': [
                    {
                        'timestamp': 1552003222000,
                        'sensors': [],
                        'geodata': [
                            {
                                'positions': [{'position': [3.0, 3.0]}],
                                'time_shift': 0,
                            },
                        ],
                    },
                ],
            },
        ]

    response = await taxi_driver_trackstory_adv.post(
        'positions',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    item = data['results'][0]
    assert item['type'] == 'raw'
    assert item['driver_id'] == 'dbid_uuid1'

    pos = item['position']
    assert pos['lat'] == 1.0
    assert pos['lon'] == 1.0
    assert pos['timestamp'] == 1552003222

    item = data['results'][1]
    assert item['type'] == 'raw'
    assert item['driver_id'] == 'uuid2'

    pos = item['position']
    assert pos['lat'] == 2.0
    assert pos['lon'] == 2.0
    assert pos['timestamp'] == 1552003222

    response = await taxi_driver_trackstory_adv.post(
        'positions',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    item = data['results'][0]
    assert item['type'] == 'raw'
    assert item['driver_id'] == 'dbid_uuid1'

    pos = item['position']
    assert pos['lat'] == 1.0
    assert pos['lon'] == 1.0
    assert pos['timestamp'] == 1552003222

    item = data['results'][1]
    assert item['type'] == 'adjusted'
    assert item['driver_id'] == 'uuid2'

    pos = item['position']
    assert pos['lat'] == 3.0
    assert pos['lon'] == 3.0
    assert pos['timestamp'] == 1552003222


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_one_driver_adjusted(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'dbid_uuid_1'
    message = _get_edge_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    driver_id2 = 'dbid_uuid_2'
    response = await taxi_driver_trackstory_adv.post(
        'positions',
        json={'driver_ids': [driver_id, driver_id2], 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    item = data['results'][0]
    assert item['type'] == 'adjusted'
    assert item['driver_id'] == 'dbid_uuid_1'

    pos = item['position']
    assert pos['lat'] == 37.0
    assert pos['lon'] == 55.0
    assert pos['direction'] == 0.0
    assert pos['timestamp'] == 1552003200


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_driver_adjusted_by_default(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'dbid_uuid_24'
    message = _get_edge_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'positions', json={'driver_ids': [driver_id]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    item = data['results'][0]
    assert item['type'] == 'adjusted'
    assert item['driver_id'] == driver_id

    pos = item['position']
    assert pos['lat'] == 37.0
    assert pos['lon'] == 55.0
    assert pos['direction'] == 0.0
    assert pos['timestamp'] == 1552003200


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_bad_type_position(taxi_driver_trackstory, redis_store, now):
    response = await taxi_driver_trackstory.post(
        'positions', json={'driver_id': 'driver_id', 'type': 'adjusted11'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_no_driver_ids(taxi_driver_trackstory, redis_store, now):
    response = await taxi_driver_trackstory.post(
        'positions', json={'type': 'adjusted'},
    )
    assert response.status_code == 400
