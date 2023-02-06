import datetime

import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/photos/upload'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '45894f24-2f83-466b-91b7-7b37cf905439'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
TAKEN_AT = '2019-04-19T13:40:32Z'
SIZE_BYTES = 333
SIZE_BYTES_OK_BIG = 16000000
SIZE_BYTES_TOO_BIG = 17000000

OK_PARAMS = {
    'device_id': DEVICE_ID,
    'timestamp': '2019-04-19T13:40:00Z',
    'file_id': FILE_ID,
}


@pytest.mark.parametrize('size', [SIZE_BYTES, SIZE_BYTES_OK_BIG])
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok(taxi_signal_device_api, pgsql, mockserver, size):
    @mockserver.handler('/v1/' + DEVICE_ID + '/photos/' + FILE_ID, prefix=True)
    def mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    old_updated_at = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    ).strftime('%Y-%m-%dT%H:%M:%SZ')
    common.add_photo(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        size,
        TAKEN_AT,
        False,
        old_updated_at,
    )
    photo_data = bytes(size)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, photo_data, False,
            ),
        },
        params=params,
        data=photo_data,
    )
    assert response.json() == {}
    assert response.status_code == 200
    assert mock_mds.times_called == 1
    common.check_photo_in_db(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        size,
        TAKEN_AT,
        True,
        old_updated_at,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api, pgsql):
    photo_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        params=params,
        data=photo_data,
    )
    assert response.json() == common.response_400_not_registered(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    photo_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, photo_data, False,
            ),
        },
        params=params,
        data=photo_data,
    )
    assert response.json() == common.response_400_not_alive(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_idempotency(taxi_signal_device_api, pgsql, mockserver):
    @mockserver.handler('/v1/' + DEVICE_ID + '/photos/' + FILE_ID, prefix=True)
    def mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, True,
    )
    photo_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, photo_data, False,
            ),
        },
        params=params,
        data=photo_data,
    )
    assert response.json() == {}
    assert response.status_code == 200
    assert mock_mds.times_called == 0
    common.check_photo_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, True,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_413(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql,
        DEVICE_PRIMARY_KEY,
        FILE_ID,
        SIZE_BYTES_TOO_BIG,
        TAKEN_AT,
        False,
    )
    photo_data = bytes(SIZE_BYTES_TOO_BIG)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, photo_data, False,
            ),
        },
        params=params,
        data=photo_data,
    )
    assert response.content == b'too large request'
    assert response.status_code == 413


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_404(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    photo_data = bytes(SIZE_BYTES)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, photo_data, False,
            ),
        },
        params=params,
        data=photo_data,
    )
    assert response.json() == {
        'code': '404',
        'message': (
            'Photo with file_id '
            + FILE_ID
            + ' has not been requested or approved'
        ),
    }
    assert response.status_code == 404


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_different_size(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, False,
    )
    photo_data = bytes(SIZE_BYTES + 100)
    params = OK_PARAMS
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, params, photo_data, False,
            ),
        },
        params=params,
        data=photo_data,
    )
    assert response.json() == {
        'code': '400',
        'message': (
            'Photo metadata mismatch: size_bytes approved is '
            + str(SIZE_BYTES)
            + ', size_bytes requested is '
            + str(SIZE_BYTES + 100)
        ),
    }
    assert response.status_code == 400
