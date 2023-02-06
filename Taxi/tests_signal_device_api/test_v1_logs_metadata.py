import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/logs/metadata'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = 'af0df198-12f2-4712-b37a-c1597f2bac70'
FILE_ID = '4701c649-384b-499a-850b-c1900a0b0d49'
SIZE_BYTES = 300

OK_JSON_BODY = {
    'device_id': DEVICE_ID,
    'timestamp': '2019-04-19T13:40:00Z',
    'size_bytes': SIZE_BYTES,
    'file_id': FILE_ID,
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
    common.check_log_in_db(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES)


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
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, True)
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
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, False)
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
    common.check_log_in_db(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES)


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_already_uploaded(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    common.add_log(pgsql, DEVICE_PRIMARY_KEY, FILE_ID, SIZE_BYTES, True)
    json_body = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:40:00Z',
        'size_bytes': SIZE_BYTES,
        'file_id': FILE_ID,
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
        'message': (
            f'Log (file_id={FILE_ID}, size_bytes={SIZE_BYTES})'
            + ' has already been uploaded'
        ),
    }
    assert response.status_code == 409
