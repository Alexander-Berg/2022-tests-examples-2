import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/photos/metadata'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = 'af0df198-12f2-4712-b37a-c1597f2bac70'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
SIZE_BYTES = 333
TIMESTAMP = '2019-04-19T13:40:00Z'
TAKEN_AT = '2019-04-19T13:40:32Z'

OK_JSON_BODY = {
    'device_id': DEVICE_ID,
    'timestamp': TIMESTAMP,
    'size_bytes': SIZE_BYTES,
    'file_id': FILE_ID,
    'taken_at': TAKEN_AT,
}


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = OK_JSON_BODY
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == {}
    assert response.status_code == 200
    common.check_photo_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        json=OK_JSON_BODY,
    )
    assert response.json() == common.response_400_not_registered(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    json_body = OK_JSON_BODY
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == common.response_400_not_alive(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_403(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, True,
    )
    jwt = common.generate_jwt(private_key, ENDPOINT, {}, OK_JSON_BODY)
    mutated_jwt = jwt[:-8] + 'AAAAAAAA'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={common.JWT_HEADER_NAME: mutated_jwt},
        json=OK_JSON_BODY,
    )
    assert response.json() == common.RESPONSE_403_INVALID_SIGNATURE
    assert response.status_code == 403


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_idempotency(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, False,
    )
    json_body = OK_JSON_BODY
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == {}
    assert response.status_code == 200
    common.check_photo_in_db(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT,
    )


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_already_uploaded(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, True,
    )
    json_body = OK_JSON_BODY
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    taken_at_response = TAKEN_AT.replace('Z', '+0000')
    assert response.json() == {
        'code': '409',
        'message': (
            f'Photo (file_id={FILE_ID}, '
            f'size_bytes={SIZE_BYTES}, '
            f'taken_at={taken_at_response}) has already been uploaded'
        ),
    }
    assert response.status_code == 409


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
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_different_metadata(
        taxi_signal_device_api,
        pgsql,
        other_size_bytes,
        other_taken_at,
        description_postfix,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_photo(
        pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, TAKEN_AT, False,
    )
    json_body = {
        'device_id': DEVICE_ID,
        'timestamp': TIMESTAMP,
        'size_bytes': other_size_bytes,
        'file_id': FILE_ID,
        'taken_at': other_taken_at,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == {
        'code': '409',
        'message': 'Metadata mismatch: ' + description_postfix,
    }
    assert response.status_code == 409
