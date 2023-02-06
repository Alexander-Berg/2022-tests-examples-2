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


def _get_channel_message2(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'timestamp': timestamp - 1,
            'speed': 11.666666666666668,
            'accuracy': 3,
            'source': 'Gps',
        },
        {
            'driver_id': driver_id,
            'position': [54, 36],
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
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'id': driver_id,
        'track': [
            {
                'lat': 37.0,
                'lon': 55.0,
                'timestamp': 1568198475,
                'speed': 11.6,
                'accuracy': 3.0,
                'direction': 45.0,
            },
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/get_track': 100})
async def test_usage_internal_trackstory(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

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
                                'positions': [{'position': [1.0, 1.0]}],
                                'time_shift': 0,
                            },
                        ],
                    },
                ],
            },
        ]

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'id': driver_id,
        'track': [{'lat': 1.0, 'lon': 1.0, 'timestamp': 1568198475}],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_success_with_adjusted_is_null(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    @mockserver.json_handler('/yaga-adjust/adjust/track')
    def _mock_yaga_adjust(request):
        return {
            'positions': [
                {'lat': 0, 'lon': 0, 'is_null': True, 'timestamp': 141111},
            ],
        }

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
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
            'adjust': True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'id': driver_id,
        'track': [
            {
                'lat': 37.0,
                'lon': 55.0,
                'timestamp': 1568198475,
                'speed': 11.6,
                'accuracy': 3.0,
                'direction': 45.0,
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
async def test_get_track_success_with_adjusted(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    @mockserver.json_handler('/yaga-adjust/adjust/track')
    def _mock_yaga_adjust(request):
        return {
            'positions': [
                {
                    'lat': 37,
                    'lon': 57,
                    'is_null': False,
                    'timestamp': 1568198477,
                },
            ],
        }

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
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
            'adjust': True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'id': driver_id,
        'track': [{'lat': 37.0, 'lon': 57.0, 'timestamp': 1568198477}],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_empty(taxi_driver_trackstory_adv):
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {'track': [], 'id': driver_id}


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_from_time(taxi_driver_trackstory_adv):
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T13:42:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 'bad_interval'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_end_time(taxi_driver_trackstory_adv):
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T13:44:15+00:00',
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 'bad_interval'


@pytest.mark.now('2019-09-13T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_bad_request_interval_too_big(
        taxi_driver_trackstory_adv,
):
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-12T13:44:15+00:00',
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 'too_long_interval'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
async def test_get_track_bad_request_start_time_too_low(
        taxi_driver_trackstory_adv,
):
    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2011-10-24T00:00:00+00:00',
            'to_time': '2011-10-24T00:01:00+00:00',
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == 'bad_interval'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(DRIVER_TRACKSTORY_ADJUST_TYPE='snap')
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_adjusted_snap(
        taxi_driver_trackstory_adv, redis_store, mockserver, now,
):
    @mockserver.json_handler('/yaga-adjust/adjust/track')
    def _mock_yaga_adjust(request):
        assert request.query['algorithm'] == 'snap'
        return {
            'positions': [
                {
                    'lat': 37,
                    'lon': 57,
                    'is_null': False,
                    'timestamp': 1568198477,
                },
            ],
        }

    pos_tp = now - datetime.timedelta(minutes=1)
    dbid = 'dbid'
    uuid = 'uuid_13'
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
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
            'adjust': True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'id': driver_id,
        'track': [{'lat': 37.0, 'lon': 57.0, 'timestamp': 1568198477}],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(DRIVER_TRACKSTORY_YDB_ENABLE=False)
async def test_get_track_ydb_disabled(taxi_driver_trackstory_adv, testpoint):
    @testpoint('ydb_read')
    def ydb_read(data):
        pass

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:30:15+00:00',
            'to_time': '2019-09-11T10:15:15+00:00',
        },
    )

    assert response.status_code == 200
    assert ydb_read.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(DRIVER_TRACKSTORY_YDB_ENABLE=True)
async def test_get_track_ydb_empty(taxi_driver_trackstory_adv, testpoint):
    @testpoint('ydb_read')
    def ydb_read(data):
        assert data == []

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:30:15+00:00',
            'to_time': '2019-09-11T10:15:15+00:00',
        },
    )

    assert response.status_code == 200
    assert ydb_read.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.ydb(files=['fill_data.sql'])
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(DRIVER_TRACKSTORY_YDB_ENABLE=True)
async def test_get_track_ydb_one(taxi_driver_trackstory_adv, testpoint):
    @testpoint('ydb_read')
    def ydb_read(data):
        assert data == [
            {
                'lat': 37.0,
                'lon': 55.0,
                'timestamp': 1568196015,
                'speed': 8.88888888888889,
                'direction': 336,
            },
        ]

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:30:15+00:00',
            'to_time': '2019-09-11T10:15:15+00:00',
        },
    )

    assert response.status_code == 200
    assert ydb_read.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.ydb(files=['fill_data.sql'])
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(DRIVER_TRACKSTORY_YDB_ENABLE=True)
async def test_get_track_ydb_none_in_range(
        taxi_driver_trackstory_adv, testpoint,
):
    @testpoint('ydb_read')
    def ydb_read(data):
        assert data == []

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:30:15+00:00',
            'to_time': '2019-09-11T09:35:15+00:00',
        },
    )

    assert response.status_code == 200
    assert ydb_read.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.ydb(files=['fill_data.sql'])
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(DRIVER_TRACKSTORY_YDB_ENABLE=True)
async def test_get_track_ydb_multiple(taxi_driver_trackstory_adv, testpoint):
    @testpoint('ydb_read')
    def ydb_read(data):
        assert data == [
            {
                'lat': 37.0,
                'lon': 55.0,
                'timestamp': 1568196015,
                'speed': 8.88888888888889,
                'direction': 336,
            },
            {
                'lat': 38.0,
                'lon': 56.0,
                'timestamp': 1568197400,
                'speed': 9.166666666666668,
                'direction': 337,
            },
        ]

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:30:15+00:00',
            'to_time': '2019-09-11T10:30:15+00:00',
        },
    )

    assert response.status_code == 200
    assert ydb_read.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.ydb(files=['required_only.sql'])
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(DRIVER_TRACKSTORY_YDB_ENABLE=True)
async def test_get_track_ydb_optionals(taxi_driver_trackstory_adv, testpoint):
    @testpoint('ydb_read')
    def ydb_read(data):
        assert data == [{'lat': 37.0, 'lon': 55.0, 'timestamp': 1568196015}]

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    response = await taxi_driver_trackstory_adv.post(
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:30:15+00:00',
            'to_time': '2019-09-11T10:15:15+00:00',
        },
    )

    assert response.status_code == 200
    assert ydb_read.times_called == 1


@pytest.mark.config(TRACKSTORY_READ_PIPELINE_MDS=True)
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
async def test_get_track_internal_mds(
        taxi_driver_trackstory_adv, redis_store, now, mockserver,
):
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
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
        },
    )

    assert response.status_code == 200
    data = response.json()
    await _mock_internal_mds.wait_call()

    assert data == {'id': driver_id, 'track': []}


def _get_bucket(request):
    url = request.url
    return re.match('http://([a-zA-Z-]+).', url).group(1)


def _get_prefix(request):
    return '/'.join(request.path.split('/')[2:-4])


@pytest.mark.config(TRACKSTORY_READ_PIPELINE_MDS=True)
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.parametrize(
    'date,expected_buckets,expected_prefixes',
    [
        # request after split date
        ('2019-09-11T00:40:15+00:00', {'internal-trackstory'}, {'data/taxi'}),
        # request before split date
        ('2019-09-12T00:40:15+00:00', {'geotracks'}, {'data'}),
        # request contains split date
        (
            '2019-09-11T10:00:00+00:00',
            {'internal-trackstory', 'geotracks'},
            {'data', 'data/taxi'},
        ),
    ],
)
async def test_get_track_internal_mds_legacy_crutch(
        taxi_driver_trackstory_adv,
        redis_store,
        now,
        mockserver,
        taxi_config,
        date,
        expected_buckets,
        expected_prefixes,
):
    taxi_config.set_values({'TRACKSTORY_LEGACY_MDS_SETTINGS': {'taxi': date}})

    buckets = set()
    prefixes = set()

    # Test that with TRACKSTORY_READ_PIPELINE_MDS config internal-trackstory
    # bucket used
    @mockserver.handler('/mds-s3/', prefix=True)
    def _mock_internal_mds(request):
        bucket = _get_bucket(request)
        prefix = _get_prefix(request)
        buckets.add(bucket)
        prefixes.add(prefix)
        return mockserver.make_response(status=404)

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
        'get_track',
        json={
            'id': driver_id,
            'from_time': '2019-09-11T09:40:15+00:00',
            'to_time': '2019-09-11T10:42:15+00:00',
        },
    )

    assert response.status_code == 200
    data = response.json()
    await _mock_internal_mds.wait_call()
    assert data == {'id': driver_id, 'track': []}

    assert buckets == expected_buckets
    assert prefixes == expected_prefixes
