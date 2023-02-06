import copy

import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/files/metadata'

AES_KEY = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
SERIAL_NUMBER = '1234567890ABC'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
SIZE_BYTES = 333
TIMESTAMP = '2019-04-19T13:40:00Z'
TAKEN_AT = '2019-04-19T13:40:32Z'

JSON_BODY = {
    'serial_number': SERIAL_NUMBER,
    'timestamp': TIMESTAMP,
    'size_bytes': SIZE_BYTES,
    'file_id': FILE_ID,
    'taken_at': TAKEN_AT,
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_ok(taxi_signal_device_api, pgsql):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, JSON_BODY,
            ),
        },
        json=JSON_BODY,
    )
    assert response.status_code == 200
    assert response.json() == {}
    common.check_file_in_db(
        pgsql, SERIAL_NUMBER, FILE_ID, SIZE_BYTES, TAKEN_AT,
    )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_file_info(taxi_signal_device_api, pgsql):
    json_body = copy.deepcopy(JSON_BODY)
    json_body['file_info'] = 'description'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200
    assert response.json() == {}
    common.check_file_in_db(
        pgsql,
        SERIAL_NUMBER,
        FILE_ID,
        SIZE_BYTES,
        TAKEN_AT,
        file_info='description',
    )


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_invalid_serial_number(taxi_signal_device_api, pgsql):
    invalid_serial_number = '1234567890ABA'
    json_body = copy.deepcopy(JSON_BODY)
    json_body['serial_number'] = invalid_serial_number
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, json_body,
            ),
        },
        json=json_body,
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
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY[:-2], {}, JSON_BODY,
            ),
        },
        json=JSON_BODY,
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Failed to verify JWT',
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_already_uploaded(taxi_signal_device_api, pgsql):
    common.add_file(pgsql, SERIAL_NUMBER, FILE_ID, SIZE_BYTES, TAKEN_AT, True)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, JSON_BODY,
            ),
        },
        json=JSON_BODY,
    )
    taken_at_response = TAKEN_AT.replace('Z', '+0000')
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': (
            f'File (file_id={FILE_ID}, '
            f'size_bytes={SIZE_BYTES}, '
            f'taken_at={taken_at_response}) has already been uploaded'
        ),
    }


@pytest.mark.parametrize(
    'other_size_bytes, other_taken_at, description_postfix',
    [
        (
            SIZE_BYTES + 100,
            TAKEN_AT,
            'size_bytes approved is '
            + str(SIZE_BYTES)
            + ', size_bytes requested is '
            + str(SIZE_BYTES + 100),
        ),
        (
            SIZE_BYTES,
            TAKEN_AT.replace('2019', '2020'),
            'taken_at approved is '
            + TAKEN_AT.replace('Z', '+0000')
            + ', taken_at requested is '
            + TAKEN_AT.replace('2019', '2020').replace('Z', '+0000'),
        ),
        (
            SIZE_BYTES - 1,
            TAKEN_AT.replace('2019', '2018'),
            'size_bytes approved is '
            + str(SIZE_BYTES)
            + ', size_bytes requested is '
            + str(SIZE_BYTES - 1)
            + ' and '
            + 'taken_at approved is '
            + TAKEN_AT.replace('Z', '+0000')
            + ', taken_at requested is '
            + TAKEN_AT.replace('2019', '2018').replace('Z', '+0000'),
        ),
    ],
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_different_metadata(
        taxi_signal_device_api,
        pgsql,
        other_size_bytes,
        other_taken_at,
        description_postfix,
):
    common.add_file(pgsql, SERIAL_NUMBER, FILE_ID, SIZE_BYTES, TAKEN_AT, False)
    json_body = {
        'serial_number': SERIAL_NUMBER,
        'timestamp': TIMESTAMP,
        'size_bytes': other_size_bytes,
        'file_id': FILE_ID,
        'taken_at': other_taken_at,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'Metadata mismatch: ' + description_postfix,
    }
