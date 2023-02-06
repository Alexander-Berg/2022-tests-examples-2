import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/videos/upload'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '45894f24-2f83-466b-91b7-7b37cf905439'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
SIZE_BYTES = 300
SIZE_BYTES_OK_BIG = 15000000
SIZE_BYTES_TOO_BIG = 17000000
STARTED_AT = '2019-04-19T13:42:00Z'
FINISHED_AT = '2019-04-19T13:49:00Z'

OK_PARAMS = {
    'device_id': DEVICE_ID,
    'timestamp': '2019-04-19T13:40:00Z',
    'file_id': FILE_ID,
    'offset_bytes': 0,
}


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_S3_MDS_URL_SETTINGS_V2={
        'binaries_bucket_name': 'sda-binaries',
        'photos_bucket_name': 'sda-photos',
        'video_partitions_bucket_name': 'sda-video-partitions',
        'videos_bucket_name': 'sda-videos',
        'files_bucket_name': 'sda-files',
        'url': 's3.mock.net',
    },
    S3_REQUEST_RETRIES=1,
    S3_REQUEST_TIMEOUT=3000,
    SIGNAL_DEVICE_API_VIDEOS_DIRECT_UPLOAD_SETTINGS={
        'is_one_chunk_direct_upload_enabled': True,
        'need_presigned_url': True,
    },
)
@pytest.mark.parametrize(
    'size, finished_at',
    [(SIZE_BYTES, None), (SIZE_BYTES_OK_BIG, FINISHED_AT)],
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_single_upload(
        taxi_signal_device_api, pgsql, mockserver, size, finished_at,
):
    @mockserver.handler(
        '/v1/' + DEVICE_ID + '/videos/partitions/' + FILE_ID, prefix=True,
    )
    def mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    @mockserver.handler('/v1/' + DEVICE_ID + '/' + FILE_ID, prefix=True)
    def mock_videos_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_video(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        size,
        False,
        STARTED_AT,
        finished_at,
    )
    video_data = bytes(size)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, video_data, False,
            ),
        },
        params=params,
        data=video_data,
    )
    assert response.json() == {'upload_status': {'status': 'FINISHED'}}
    assert response.status_code == 200
    assert mock_mds.times_called == 1
    assert mock_videos_mds.times_called == 1
    common.check_video_chunk_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, size, 0, 'concatenated',
    )
    common.check_video_in_db(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, size)


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_S3_MDS_URL_SETTINGS_V2={
        'binaries_bucket_name': 'sda-binaries',
        'photos_bucket_name': 'sda-photos',
        'video_partitions_bucket_name': 'sda-video-partitions',
        'videos_bucket_name': 'sda-videos',
        'files_bucket_name': 'sda-files',
        'url': 's3.mock.net',
    },
    S3_REQUEST_RETRIES=1,
    S3_REQUEST_TIMEOUT=3000,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_multiple_uploads(taxi_signal_device_api, pgsql, mockserver):
    @mockserver.handler(
        '/v1/' + DEVICE_ID + '/videos/partitions/' + FILE_ID, prefix=True,
    )
    def mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_video(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        SIZE_BYTES,
        False,
        STARTED_AT,
        None,
    )
    size_1 = 100
    video_data_1 = bytes(100)
    params_1 = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params_1, video_data_1, False,
            ),
        },
        params=params_1,
        data=video_data_1,
    )
    assert response.json() == {
        'upload_status': {
            'offset_bytes': size_1,
            'recommended_chunk_size': common.RECOMMENDED_CHUNK_SIZE,
            'sleep_for_ms': 0,
            'status': 'IN_PROGRESS',
            'total_bytes': 300,
        },
    }
    assert response.status_code == 200
    common.check_video_chunk_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, size_1, 0,
    )
    assert mock_mds.times_called == 1
    size_2 = 105
    video_data_2 = bytes(size_2)
    params_2 = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:40:00Z',
        'file_id': FILE_ID,
        'offset_bytes': size_1,
    }
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params_2, video_data_2, False,
            ),
        },
        params=params_2,
        data=video_data_2,
    )
    assert response.json() == {
        'upload_status': {
            'offset_bytes': size_1 + size_2,
            'recommended_chunk_size': common.RECOMMENDED_CHUNK_SIZE,
            'sleep_for_ms': 0,
            'status': 'IN_PROGRESS',
            'total_bytes': 300,
        },
    }
    assert response.status_code == 200
    common.check_video_chunk_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, size_2, size_1,
    )
    assert mock_mds.times_called == 2
    video_data_3 = bytes(SIZE_BYTES - size_1 - size_2)
    params_3 = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:40:00Z',
        'file_id': FILE_ID,
        'offset_bytes': size_1 + size_2,
    }
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params_3, video_data_3, False,
            ),
        },
        params=params_3,
        data=video_data_3,
    )
    assert response.json() == {'upload_status': {'status': 'FINISHED'}}
    assert response.status_code == 200
    common.check_video_chunk_in_db(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        SIZE_BYTES - size_1 - size_2,
        size_1 + size_2,
    )
    assert mock_mds.times_called == 3


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api, pgsql):
    video_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        params=params,
        data=video_data,
    )
    assert response.json() == common.response_400_not_registered(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    video_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, video_data, False,
            ),
        },
        params=params,
        data=video_data,
    )
    assert response.json() == common.response_400_not_alive(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_413(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_video(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        SIZE_BYTES_TOO_BIG,
        False,
        STARTED_AT,
        None,
    )
    video_data = bytes(SIZE_BYTES_TOO_BIG)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, video_data, False,
            ),
        },
        params=params,
        data=video_data,
    )
    assert response.content == b'too large request'
    assert response.status_code == 413


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_404(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    video_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, video_data, False,
            ),
        },
        params=params,
        data=video_data,
    )
    assert response.json() == {
        'code': '404',
        'message': (
            'Video with file_id '
            + FILE_ID
            + ' has not been requested or approved'
            ' for device_id ' + DEVICE_ID
        ),
    }
    assert response.status_code == 404
