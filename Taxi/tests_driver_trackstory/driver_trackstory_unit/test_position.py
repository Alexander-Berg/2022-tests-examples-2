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
            'speed': 42.0,
        },
    ]
    return geobus.serialize_edge_positions_v2(drivers, now)


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_not_found(taxi_driver_trackstory):
    request_body = {'driver_id': 'dbid_uuid'}
    response = await taxi_driver_trackstory.post('position', json=request_body)
    assert response.status_code == 404
    data = response.json()
    assert (
        data['message']
        == 'There is no shorttrack for driver with id : dbid_uuid'
    )


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_raw(taxi_driver_trackstory_adv, now):
    driver_id = 'dbid_uuid_0'
    message = _get_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'position', json={'driver_id': driver_id, 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['position']['direction'] == 45.0
    assert data['position']['lat'] == 37.0
    assert data['position']['lon'] == 55.0
    assert data['position']['accuracy'] == 1.0
    assert data['position']['timestamp'] == 1552003200
    assert math.isclose(
        data['position']['speed'], 11.666666666666668, abs_tol=0.00001,
    )
    assert data['type'] == 'raw'


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/position': 100})
async def test_usage_internal_trackstory(
        taxi_driver_trackstory_adv, mockserver, now,
):
    dbid = 'dbid'
    uuid = 'uuid_0'
    driver_id = dbid + '_' + uuid

    @mockserver.json_handler('/internal-trackstory/taxi/position')
    def _mock_internal_trackstory(request):
        assert request.query['dbid'] == dbid
        assert request.query['uuid'] == uuid
        return [
            {
                'contractor': {'uuid': uuid, 'dbid': dbid},
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
            },
        ]

    response = await taxi_driver_trackstory_adv.post(
        'position', json={'driver_id': driver_id, 'type': 'raw'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['position']['lat'] == 1.0
    assert data['position']['lon'] == 1.0
    assert data['position']['timestamp'] == 1552003222
    assert data['type'] == 'raw'

    response = await taxi_driver_trackstory_adv.post(
        'position', json={'driver_id': driver_id, 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['position']['lat'] == 1.0
    assert data['position']['lon'] == 1.0
    assert data['position']['timestamp'] == 1552003222
    assert data['type'] == 'raw'


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_raw_for_adjusted(taxi_driver_trackstory_adv, now):
    driver_id = 'dbid_uuid_1'
    message = _get_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'position', json={'driver_id': driver_id, 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['position']['direction'] == 45.0
    assert data['position']['lat'] == 37.0
    assert data['position']['lon'] == 55.0
    assert data['position']['accuracy'] == 1.0
    assert data['position']['timestamp'] == 1552003200
    assert math.isclose(
        data['position']['speed'], 11.666666666666668, abs_tol=0.00001,
    )
    assert data['type'] == 'raw'


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_adjusted(taxi_driver_trackstory_adv, now):
    driver_id = 'dbid_uuid_2'
    message = _get_edge_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'position', json={'driver_id': driver_id, 'type': 'adjusted'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['position']['lat'] == 37.0
    assert data['position']['lon'] == 55.0
    assert data['position']['direction'] == 0.0
    assert data['position']['timestamp'] == 1552003200
    assert math.isclose(data['position']['speed'], 42.0, abs_tol=0.00001)
    assert data['type'] == 'adjusted'


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_found_adjusted_by_default(
        taxi_driver_trackstory_adv, redis_store, now,
):
    driver_id = 'dbid_uuid_23'
    message = _get_edge_channel_message(driver_id, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        EDGE_TRACKS_CHANNEL, message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'position', json={'driver_id': driver_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['position']['lat'] == 37.0
    assert data['position']['lon'] == 55.0
    assert data['position']['direction'] == 0.0
    assert data['position']['timestamp'] == 1552003200
    assert data['type'] == 'adjusted'


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_bad_type_position(taxi_driver_trackstory, redis_store, now):
    response = await taxi_driver_trackstory.post(
        'position', json={'driver_id': 'driver_id', 'type': 'adjusted11'},
    )
    assert response.status_code == 400


@pytest.mark.now('2019-03-08T00:00:00Z')
async def test_no_driver_id(taxi_driver_trackstory, redis_store, now):
    response = await taxi_driver_trackstory.post(
        'position', json={'type': 'adjusted'},
    )
    assert response.status_code == 400
