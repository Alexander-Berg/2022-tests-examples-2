import copy
import datetime

import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/files/upload'

AES_KEY = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
SERIAL_NUMBER = '1234567890ABC'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
TAKEN_AT = '2019-04-19T13:40:32Z'
SIZE_BYTES = 333
SIZE_BYTES_OK_BIG = 16000000
SIZE_BYTES_TOO_BIG = 17000000

OK_PARAMS = {
    'serial_number': SERIAL_NUMBER,
    'timestamp': '2019-04-19T13:40:00Z',
    'file_id': FILE_ID,
}


@pytest.mark.parametrize('size', [SIZE_BYTES, SIZE_BYTES_OK_BIG])
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_ok(taxi_signal_device_api, pgsql, mockserver, size):
    @mockserver.handler(
        '/v1/' + SERIAL_NUMBER + '/files/' + FILE_ID, prefix=True,
    )
    def mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    old_updated_at = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    ).strftime('%Y-%m-%dT%H:%M:%SZ')
    common.add_file(
        pgsql, SERIAL_NUMBER, FILE_ID, size, TAKEN_AT, False, old_updated_at,
    )
    file_data = bytes(size)
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, OK_PARAMS, file_data, False,
            ),
        },
        params=OK_PARAMS,
        data=file_data,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert mock_mds.times_called == 1
    common.check_file_in_db(
        pgsql, SERIAL_NUMBER, FILE_ID, size, TAKEN_AT, True, old_updated_at,
    )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_large(taxi_signal_device_api, pgsql, mockserver):
    file_data = bytes(SIZE_BYTES_TOO_BIG)
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, OK_PARAMS, file_data, False,
            ),
        },
        params=OK_PARAMS,
        data=file_data,
    )
    assert response.status_code == 413
    assert response.content == b'too large request'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_invalid_serial_number(taxi_signal_device_api, pgsql):
    file_data = bytes(SIZE_BYTES)
    invalid_serial_number = '1234567890ABA'
    params = copy.deepcopy(OK_PARAMS)
    params['serial_number'] = invalid_serial_number
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, params, file_data, False,
            ),
        },
        params=params,
        data=file_data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            f'Device with serial_number {invalid_serial_number} not found'
        ),
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_incorrect_aes(taxi_signal_device_api, pgsql):
    file_data = bytes(SIZE_BYTES)
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY[:-2], OK_PARAMS, file_data, False,
            ),
        },
        params=OK_PARAMS,
        data=file_data,
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Failed to verify JWT',
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_404(taxi_signal_device_api, pgsql):
    file_data = bytes(SIZE_BYTES)
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, OK_PARAMS, file_data, False,
            ),
        },
        params=OK_PARAMS,
        data=file_data,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': (
            'File with file_id '
            + FILE_ID
            + ' has not been requested or approved'
        ),
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_different_size(taxi_signal_device_api, pgsql):
    common.add_file(pgsql, SERIAL_NUMBER, FILE_ID, SIZE_BYTES, TAKEN_AT, False)
    file_data = bytes(SIZE_BYTES + 100)
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, OK_PARAMS, file_data, False,
            ),
        },
        params=OK_PARAMS,
        data=file_data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'File metadata mismatch: size_bytes approved is '
            + str(SIZE_BYTES)
            + ', size_bytes requested is '
            + str(SIZE_BYTES + 100)
        ),
    }
