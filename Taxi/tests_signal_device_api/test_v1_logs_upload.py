import datetime

import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/logs/upload'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '6359938a-7861-4266-9e02-6edd1c2138d9'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
SIZE_BYTES = 388
PARAMS = {
    'device_id': DEVICE_ID,
    'timestamp': '2019-04-19T13:40:00Z',
    'file_id': FILE_ID,
}


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok(taxi_signal_device_api, pgsql, load_binary):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    old_updated_at = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    ).strftime('%Y-%m-%dT%H:%M:%SZ')
    common.add_log(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, False, old_updated_at,
    )
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, log_data, False,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {}
    assert response.status_code == 200
    common.check_log_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, True, old_updated_at,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_corrupted_archive(taxi_signal_device_api, pgsql, load_binary):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )

    old_updated_at = (
        datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    ).strftime('%Y-%m-%dT%H:%M:%SZ')
    common.add_log(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, 81920, False, old_updated_at,
    )

    log_data = load_binary('signalq_broken.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, log_data, False,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {
        'code': 'corrupted_archive',
        'message': 'Could not uncompress data',
    }
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api, load_binary):
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {
        'code': '400',
        'message': 'Device with id ' + DEVICE_ID + ' is not registered',
    }
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql, load_binary):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, False)
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, log_data, False,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {
        'code': '400',
        'message': 'Device with id ' + DEVICE_ID + ' is not alive',
    }
    assert response.status_code == 400


@pytest.mark.parametrize(
    'jwt_error, expected_message',
    [
        (common.JwtError.NO_QUERY_HASH, 'Hash was not found for the query'),
        (common.JwtError.NO_BODY_HASH, 'Hash was not found for the body'),
        (common.JwtError.BAD_QUERY_HASH, 'Hash mismatch for the query'),
        (common.JwtError.BAD_BODY_HASH, 'Hash mismatch for the body'),
        (common.JwtError.INVALID_JWT_HEADER, 'Failed to verify JWT'),
        (common.JwtError.INVALID_JWT_STRUCTURE, 'Failed to parse JWT'),
        (
            common.JwtError.INVALID_JWT_SIGNATURE,
            common.INVALID_SIGNATURE_MESSAGE,
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_403_many_cases(
        taxi_signal_device_api,
        pgsql,
        load_binary,
        jwt_error,
        expected_message,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, True)
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_invalid_jwt(
                private_key, ENDPOINT, PARAMS, log_data, jwt_error,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {'code': '403', 'message': expected_message}
    assert response.status_code == 403


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_idempotency(taxi_signal_device_api, pgsql, load_binary):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, True)
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, log_data, False,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {}
    assert response.status_code == 200
    common.check_log_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, True,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_404(taxi_signal_device_api, pgsql, load_binary):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, log_data, False,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {
        'code': '404',
        'message': (
            'Log with file_id '
            + FILE_ID
            + ' has not been requested or approved'
        ),
    }
    assert response.status_code == 404


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_wrong_file_size(taxi_signal_device_api, pgsql, load_binary):
    wrong_size_bytes = SIZE_BYTES + 100
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, wrong_size_bytes, False)
    log_data = load_binary('signalq.log.gz')
    response = await taxi_signal_device_api.put(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, PARAMS, log_data, False,
            ),
        },
        params=PARAMS,
        data=log_data,
    )
    assert response.json() == {
        'code': '400',
        'message': (
            'Approved body size was '
            + str(wrong_size_bytes)
            + ', given body size is '
            + str(SIZE_BYTES)
        ),
    }
    assert response.status_code == 400
