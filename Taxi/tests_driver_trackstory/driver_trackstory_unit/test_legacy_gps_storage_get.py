# pylint: disable=import-error
import datetime
import re
import time

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils


TRACKS_CHANNEL = 'channel:yagr:position'


def _get_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'timestamp': timestamp,
            'speed': 11.666666666666668,
            'accuracy': 3,
            'source': 'Gps',
        },
    ]
    return geobus.serialize_positions_v2(drivers, now)


async def _wait_message_received(
        taxi_driver_trackstory_adv,
        redis_store,
        retry_channel=None,
        max_tries=30,
        retry_message=None,
):
    # wait while track-geobus-saver component receives message
    for _ in range(max_tries):
        keys = redis_store.keys()
        print(keys)
        if len(keys) > 1:
            return
        if retry_channel is not None and retry_message is not None:
            await taxi_driver_trackstory_adv.sync_send_to_channel(
                retry_channel, retry_message, 2,
            )
        time.sleep(0.2)

    # if failed to receive message
    assert False


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_success(taxi_driver_trackstory_adv, redis_store, now):
    pos_tp = now - datetime.timedelta(minutes=1)
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    message = _get_channel_message(driver_id, pos_tp)

    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )
    await _wait_message_received(
        taxi_driver_trackstory_adv,
        redis_store,
        retry_channel=TRACKS_CHANNEL,
        retry_message=message,
    )

    assert redis_store.keys()

    response = await taxi_driver_trackstory_adv.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1568194815,
            'to': 1568198535,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'track': [
            {
                'point': [55.0, 37.0],
                'timestamp': 1568198475,
                'speed': 11.6,
                'bearing': 45.0,
            },
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/legacy/gps-storage/get': 100},
)
async def test_get_track_internal_trackstory(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    dbid = 'dbid'
    uuid = 'uuid_7'

    @mockserver.json_handler('/internal-trackstory/taxi/track')
    def _mock_internal_trackstory(request):
        assert request.query['dbid'] == dbid
        assert request.query['uuid'] == uuid
        return [
            {
                'contractor': {'uuid': uuid, 'dbid': dbid},
                'Verified': [
                    {
                        'timestamp': 1568198475000,
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
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1568194815,
            'to': 1568198535,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'track': [
            {
                'point': [1.0, 1.0],
                'timestamp': 1568198475,
                'speed': 1.0,
                'bearing': 1.0,
            },
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_success_multiple(
        taxi_driver_trackstory_adv, redis_store, now,
):
    pos_tp = now - datetime.timedelta(minutes=1)
    dbid = 'dbid'
    uuid = 'uuid_7'
    uuid2 = 'uuid_8'
    driver_id = dbid + '_' + uuid
    message = _get_channel_message(driver_id, pos_tp)

    await taxi_driver_trackstory_adv.sync_send_to_channel(
        TRACKS_CHANNEL, message,
    )
    await _wait_message_received(
        taxi_driver_trackstory_adv,
        redis_store,
        retry_channel=TRACKS_CHANNEL,
        retry_message=message,
    )

    assert redis_store.keys()

    response = await taxi_driver_trackstory_adv.post(
        'legacy/gps-storage/get',
        params={'request_type': 'json'},
        json={
            'params': [
                {
                    'db_id': dbid,
                    'driver_id': uuid,
                    'from': 1568194815,
                    'to': 1568198535,
                    'req_id': 1,
                },
                {
                    'db_id': dbid,
                    'driver_id': uuid2,
                    'from': 1568194815,
                    'to': 1568198535,
                    'req_id': 2,
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'tracks': [
            {
                'db_id': dbid,
                'driver_id': uuid,
                'req_id': 1,
                'track': [
                    {
                        'point': [55.0, 37.0],
                        'timestamp': 1568198475,
                        'speed': 11.6,
                        'bearing': 45.0,
                    },
                ],
            },
            {'db_id': dbid, 'driver_id': uuid2, 'req_id': 2, 'track': []},
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/legacy/gps-storage/get': 100},
)
async def test_get_track_internal_trackstory_multiple(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    dbid = 'dbid'
    uuid = 'uuid_7'
    uuid2 = 'uuid_8'

    @mockserver.json_handler('/internal-trackstory/taxi/track')
    def _mock_internal_trackstory(request):
        assert request.query['dbid'] == dbid
        if request.query['uuid'] == uuid:
            return [
                {
                    'contractor': {'uuid': uuid, 'dbid': dbid},
                    'Verified': [
                        {
                            'timestamp': 1568198475000,
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

        return [{'contractor': {'uuid': uuid2, 'dbid': dbid}}]

    response = await taxi_driver_trackstory_adv.post(
        'legacy/gps-storage/get',
        params={'request_type': 'json'},
        json={
            'params': [
                {
                    'db_id': dbid,
                    'driver_id': uuid,
                    'from': 1568194815,
                    'to': 1568198535,
                    'req_id': 1,
                },
                {
                    'db_id': dbid,
                    'driver_id': uuid2,
                    'from': 1568194815,
                    'to': 1568198535,
                    'req_id': 2,
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'tracks': [
            {
                'db_id': dbid,
                'driver_id': uuid,
                'req_id': 1,
                'track': [
                    {
                        'point': [1.0, 1.0],
                        'timestamp': 1568198475,
                        'speed': 1.0,
                        'bearing': 1.0,
                    },
                ],
            },
            {'db_id': dbid, 'driver_id': uuid2, 'req_id': 2, 'track': []},
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_empty(taxi_driver_trackstory):
    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1568194815,
            'to': 1568198535,
        },
    )

    assert response.status_code == 200
    assert response.content == b'{"track":[]}'


@pytest.mark.config(TRACKSTORY_READ_PIPELINE_MDS=True)
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_internal_mds(taxi_driver_trackstory, mockserver):
    # Test that with TRACKSTORY_READ_PIPELINE_MDS config internal-trackstory
    # bucket used
    @mockserver.handler('/mds-s3/', prefix=True)
    def _mock_internal_mds(request):
        url = request.url
        bucket = re.match('http://([a-zA-Z-]+).', url).group(1)
        assert bucket == 'internal-trackstory'
        assert request.path.split('/')[
            :-2
        ] == '/mds-s3/data/taxi/dbid/uuid_7'.split('/')
        return mockserver.make_response(status=404)

    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1568194815,
            'to': 1568198535,
        },
    )

    assert response.status_code == 200
    assert response.content == b'{"track":[]}'
    await _mock_internal_mds.wait_call()


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_from_time(taxi_driver_trackstory):
    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1568209335,
            'to': 1568209335,
        },
    )

    assert response.status_code == 400


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_from_time_multiple(
        taxi_driver_trackstory_adv,
):
    dbid = 'dbid'
    uuid = 'uuid_7'

    response = await taxi_driver_trackstory_adv.post(
        'legacy/gps-storage/get',
        params={'request_type': 'json'},
        json={
            'params': [
                {
                    'db_id': dbid,
                    'driver_id': uuid,
                    'from': 1568209335,
                    'to': 1568209335,
                    'req_id': 1,
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'tracks': [
            {
                'db_id': dbid,
                'driver_id': uuid,
                'req_id': 1,
                'error': (
                    'failed to check request times: End time of interval'
                    ' have to be less than now.'
                ),
            },
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_end_time(taxi_driver_trackstory):
    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from_time': 1568194815,
            'to_time': 1568209455,
        },
    )

    assert response.status_code == 400


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_interval_too_big(taxi_driver_trackstory):
    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from_time': 1568169675,
            'to_time': 1568209455,
        },
    )

    assert response.status_code == 400


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
async def test_get_track_bad_request_start_time_too_low(
        taxi_driver_trackstory,
):
    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1319414400,
            'to_time': 1319414460,
        },
    )

    assert response.status_code == 400


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
async def test_get_track_start_time_equal_to_finish_time(
        taxi_driver_trackstory,
):
    dbid = 'dbid'
    uuid = 'uuid_7'
    response = await taxi_driver_trackstory.post(
        'legacy/gps-storage/get',
        params={
            'db_id': dbid,
            'driver_id': uuid,
            'from': 1419500800,
            'to': 1419500800,
        },
    )

    assert response.status_code == 200
