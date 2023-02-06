import copy

import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/videos/metadata'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '13c140cb-7dde-499c-be6e-57c010a45299'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
SIZE_BYTES = 300
STARTED_AT = '2019-04-19T13:40:00Z'
FINISHED_AT = '2019-04-19T13:45:00Z'

UPLOAD_STATUS = {
    'upload_status': {
        'offset_bytes': 0,
        'recommended_chunk_size': common.RECOMMENDED_CHUNK_SIZE,
        'sleep_for_ms': 0,
        'status': 'IN_PROGRESS',
        'total_bytes': SIZE_BYTES,
    },
}

OK_JSON = {
    'device_id': DEVICE_ID,
    'timestamp': '2019-04-19T13:40:00Z',
    'size_bytes': SIZE_BYTES,
    'file_id': FILE_ID,
    'started_at': STARTED_AT,
}


def select_video(pgsql, fields, device_id, file_id):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} FROM signal_device_api.videos '
        'WHERE device_id=\'{}\' AND file_id=\'{}\''.format(
            ','.join(fields), device_id, file_id,
        ),
    )
    db_videos = list(db)
    assert len(db_videos) == 1, db_videos
    return {k: v for (k, v) in zip(fields, db_videos[0])}


def check_video_in_db(pgsql, device_id, file_id, **kwargs):
    db_result = select_video(pgsql, kwargs.keys(), device_id, file_id)
    for field in kwargs:
        common.check_field(field, db_result[field], kwargs[field])


@pytest.mark.parametrize('finished_at', [None, FINISHED_AT])
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_no_chunks(taxi_signal_device_api, pgsql, finished_at):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = copy.deepcopy(OK_JSON)
    if finished_at:
        json_body['finished_at'] = finished_at
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == UPLOAD_STATUS
    assert response.status_code == 200
    check_video_in_db(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        size_bytes=SIZE_BYTES,
        started_at=STARTED_AT,
        finished_at=finished_at,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        json=OK_JSON,
    )
    assert response.json() == common.response_400_not_registered(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, OK_JSON,
            ),
        },
        json=OK_JSON,
    )
    assert response.json() == common.response_400_not_alive(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.parametrize('finished_at', [None, FINISHED_AT])
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_no_chunks_idempotency(
        taxi_signal_device_api, pgsql, finished_at,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = copy.deepcopy(OK_JSON)
    if finished_at:
        json_body['finished_at'] = finished_at
    common.add_video(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        SIZE_BYTES,
        True,
        STARTED_AT,
        finished_at,
    )
    print(finished_at)
    print(json_body)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == UPLOAD_STATUS
    assert response.status_code == 200
    check_video_in_db(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        size_bytes=SIZE_BYTES,
        started_at=STARTED_AT,
        finished_at=finished_at,
    )


@pytest.mark.parametrize(
    'other_size_bytes, other_started_at, '
    'other_finished_at, description_postfix',
    [
        (SIZE_BYTES + 100, STARTED_AT, FINISHED_AT, 'size_bytes'),
        (
            SIZE_BYTES,
            STARTED_AT.replace('2019', '2020'),
            FINISHED_AT,
            'started_at',
        ),
        (
            SIZE_BYTES - 1,
            STARTED_AT.replace('2019', '2018'),
            FINISHED_AT,
            'size_bytes, started_at',
        ),
        (
            SIZE_BYTES,
            STARTED_AT,
            FINISHED_AT.replace('2019', '2018'),
            'finished_at',
        ),
        (
            SIZE_BYTES - 2,
            STARTED_AT,
            FINISHED_AT.replace('2019', '2018'),
            'size_bytes, finished_at',
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_different_metadata_no_chunks(
        taxi_signal_device_api,
        pgsql,
        other_size_bytes,
        other_started_at,
        other_finished_at,
        description_postfix,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = OK_JSON
    json_body['finished_at'] = FINISHED_AT
    await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    json_body_2 = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:40:00Z',
        'size_bytes': other_size_bytes,
        'file_id': FILE_ID,
        'started_at': other_started_at,
        'finished_at': other_finished_at,
    }
    response_409 = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body_2,
            ),
        },
        json=json_body_2,
    )
    assert response_409.json() == {
        'code': 'DifferentMetadata',
        'message': 'Video metadata mismatch: ' + description_postfix,
        'upload_status': UPLOAD_STATUS['upload_status'],
    }
    assert response_409.status_code == 409
