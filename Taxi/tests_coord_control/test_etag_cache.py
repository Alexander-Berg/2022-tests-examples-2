# pylint: disable=import-error,no-name-in-module
import datetime

from fbs.models.etag_cache import Response
import pytest

from geobus_tools import geobus  # noqa: F401 C5521

PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
CHANNEL_NAME = 'channel:yagr:signal_v2'
TOTAL_CHUNKS = 3
PERFORMERS_COUNT = 10


def _deserialize_message(fbs_data):
    ret = {'array': []}
    response = Response.Response.GetRootAsResponse(fbs_data, 0)
    for i in range(response.EtagsLength()):
        performer_etag = response.Etags(i)
        ret['array'].append(
            {
                'performer_id': performer_etag.PerformerId(),
                'etag': performer_etag.Etag(),
            },
        )
    ret['chunk_number'] = response.ChunkNumber()
    ret['total_chunks'] = response.TotalChunks()
    return ret


def _sample_message_with_driver_id(driver_id, messages):
    for item in messages:
        item['driver_id'] = driver_id
    return messages


async def _publish_message(
        message,
        taxi_coord_control,
        mocked_time,
        redis_store,
        performer_from_pubsub_received,
        shift_min,
):
    await taxi_coord_control.tests_control(invalidate_caches=False)
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)
    assert (await performer_from_pubsub_received.wait_call())[
        'data'
    ] == message[0]['driver_id']

    mocked_time.sleep(shift_min * 60)
    await taxi_coord_control.tests_control(invalidate_caches=False)


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_etag_cache_incremental(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')
    now = datetime.datetime.now()
    mocked_time.set(now - datetime.timedelta(minutes=10))

    for i in range(3):
        await _publish_message(
            _sample_message_with_driver_id(f'dbid_uuid_{i}', messages),
            taxi_coord_control,
            mocked_time,
            redis_store,
            performer_from_pubsub_received,
            2,
        )

    response = await taxi_coord_control.get(
        f'etag-cache/incremental',
        params={
            'last_update': (now - datetime.timedelta(minutes=9)).strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
        },
    )
    assert response.status_code == 200
    data = _deserialize_message(response.content)
    assert len(data['array']) == 2

    response = await taxi_coord_control.get(
        f'etag-cache/incremental',
        params={
            'last_update': (now - datetime.timedelta(minutes=7)).strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
        },
    )
    assert response.status_code == 200
    data = _deserialize_message(response.content)
    assert len(data['array']) == 1


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    COORD_CONTROL_ETAGS_FETCHING_SETTINGS={
        'setting_type': 'chunks_number',
        'chunks_number': TOTAL_CHUNKS,
    },
)
async def test_etag_cache_full(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    for i in range(PERFORMERS_COUNT):
        await _publish_message(
            _sample_message_with_driver_id(f'dbid_uuid_{i}', messages),
            taxi_coord_control,
            mocked_time,
            redis_store,
            performer_from_pubsub_received,
            0,
        )

    response = await taxi_coord_control.get('etag-cache/full')
    assert response.status_code == 200
    data = _deserialize_message(response.content)
    performers_count = len(data['array'])

    assert data['total_chunks'] == 3
    assert data['chunk_number'] == 0

    for _ in range(1, TOTAL_CHUNKS):
        response = await taxi_coord_control.get(
            'etag-cache/full',
            params={
                'chunk_number': data['chunk_number'] + 1,
                'total_chunks': data['total_chunks'],
            },
        )
        assert response.status_code == 200
        data = _deserialize_message(response.content)
        performers_count += len(data['array'])

    assert performers_count == PERFORMERS_COUNT


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    COORD_CONTROL_ETAGS_FETCHING_SETTINGS={
        'setting_type': 'chunks_number',
        'chunks_number': TOTAL_CHUNKS,
    },
    COORD_CONTROL_SEND_STRATEGY_ONLY_IN_BAD_ZONES=True,
)
async def test_etag_cache_full_in_bad_zone(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    for i in range(PERFORMERS_COUNT):
        await _publish_message(
            _sample_message_with_driver_id(f'dbid_uuid_{i}', messages),
            taxi_coord_control,
            mocked_time,
            redis_store,
            performer_from_pubsub_received,
            0,
        )

    response = await taxi_coord_control.get('etag-cache/full')
    assert response.status_code == 200
    data = _deserialize_message(response.content)
    assert not data['array']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    COORD_CONTROL_ETAGS_FETCHING_SETTINGS={
        'setting_type': 'chunks_number',
        'chunks_number': TOTAL_CHUNKS,
    },
)
async def test_etag_cache_alive_timeout(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    now = datetime.datetime.now()
    mocked_time.set(now)
    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    for i in range(2):
        await _publish_message(
            _sample_message_with_driver_id(f'dbid_uuid_{i}', messages),
            taxi_coord_control,
            mocked_time,
            redis_store,
            performer_from_pubsub_received,
            0,
        )

    mocked_time.set(now + datetime.timedelta(minutes=10))

    response = await taxi_coord_control.get('etag-cache/full')
    assert response.status_code == 200
    data = _deserialize_message(response.content)

    assert not data['array']

    response = await taxi_coord_control.get(
        f'etag-cache/incremental',
        params={
            'last_update': (now - datetime.timedelta(minutes=7)).strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
        },
    )
    assert response.status_code == 200
    data = _deserialize_message(response.content)
    assert len(data['array']) == 2
    for performer_etag in data['array']:
        assert performer_etag['etag'] is None
