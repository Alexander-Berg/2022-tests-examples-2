import base64
import hashlib
import hmac

import pytest

from tests_signal_device_api import common

ENDPOINT = '/api/v1/binary-sign'

VALID_API_KEY = 'BEEF'
VERY_OLD_API_KEY = 'OLDBEEF'
DISABLED_API_KEY = 'DEADBEEF'
MISSING_API_KEY = 'NOBEEF'

VALID_CLIENT_ID = '12345'
INVALID_CLIENT_ID = '!@#$%'

ERROR_CODE_INVALID = 'invalid_api_key_or_client_id'
ERROR_CODE_EXHAUSTED = 'api_key_exhausted_or_outdated'

ERROR_MESSAGE_EMPTY = 'Empty client id or api key was provided'
ERROR_MESSAGE_INVALID = 'Invalid client id or api key was provided'
ERROR_MESSAGE_EXHAUSTED = (
    'API key provided reached its usage limit or is outdated'
)

SALT = 'MTIzNDU2Nzg5MGFiY2RlZg=='
BINARY_HASH = '8sobtsfpB9Btr+Roflefznazfk6Tt2BQItpS5szCb9I='
OK_REQUEST_JSON = {'file_name': 'file_name', 'binary_hash_base64': BINARY_HASH}
VALID_SIGNATURE = (
    's+TqLA/V147oYjUAwqcu05Cer98uTmKl26D/kZce'
    'BLwJILGOT74eHYFWzEHrQPQKkjr6FI0kYRHfcKqD'
    'P7a0whz8GbPf6XBGf7nXtcEyKJkbHwpe9RFVh4VI'
    'Mjsk7kWyLqLlzYegBeFeOmoudcsdrYkt8/rOJpnC'
    'MZArPXBn3WN3liVejQDwBgiCdu/TJHNcrdTA1H19'
    'ngJg/CjSLSmaKoQtf5ltQqJzWW6RZ5cFZuyzZhwn'
    'GDXFcfdVlMxyqUSnQZ6/K8m7Wl2xUXH/QdkQgwFq'
    'CuiJCvya79RkNXe9Yn18gjMee/X8jC+UA1xS1GTs'
    '5MoD0n9Bl63x4CA4bCWTRQ=='
)


def _check_api_key_state(
        pgsql,
        client_id,
        api_key,
        expected_times_used,
        expected_is_active,
        expect_updated,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    api_key_hash = hmac.new(
        bytes(client_id + api_key, 'utf-8'),
        msg=base64.b64decode(SALT),
        digestmod=hashlib.sha256,
    ).hexdigest()
    query_str = (
        'SELECT times_used, is_active, updated_at '
        'FROM signal_device_api.binary_sign_keys '
        'WHERE client_id=\'{}\' AND api_key_hash=\'{}\';'
    ).format(client_id, api_key_hash)
    db.execute(query_str)
    db_result = [x for x in db][0]
    assert db_result[0] == expected_times_used
    assert db_result[1] == expected_is_active
    if expect_updated:
        common.assert_now(db_result[2])


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_ok_and_exhaustion(taxi_signal_device_api, pgsql):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=OK_REQUEST_JSON,
        headers={'X-API-Key': VALID_API_KEY, 'X-Client-ID': VALID_CLIENT_ID},
    )
    _check_api_key_state(
        pgsql, VALID_CLIENT_ID, VALID_API_KEY, 10, False, True,
    )
    _check_api_key_state(
        pgsql, VALID_CLIENT_ID, VERY_OLD_API_KEY, 0, False, True,
    )
    _check_api_key_state(
        pgsql, VALID_CLIENT_ID, DISABLED_API_KEY, 5, False, False,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'signature_base64': VALID_SIGNATURE}
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=OK_REQUEST_JSON,
        headers={'X-API-Key': VALID_API_KEY, 'X-Client-ID': VALID_CLIENT_ID},
    )
    _check_api_key_state(
        pgsql, VALID_CLIENT_ID, VALID_API_KEY, 10, False, False,
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': ERROR_CODE_EXHAUSTED,
        'message': ERROR_MESSAGE_EXHAUSTED,
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'api_key, client_id, error_code, error_msg',
    [
        (
            VALID_API_KEY,
            INVALID_CLIENT_ID,
            ERROR_CODE_INVALID,
            ERROR_MESSAGE_INVALID,
        ),
        (
            DISABLED_API_KEY,
            VALID_CLIENT_ID,
            ERROR_CODE_EXHAUSTED,
            ERROR_MESSAGE_EXHAUSTED,
        ),
        (VALID_API_KEY, '', ERROR_CODE_INVALID, ERROR_MESSAGE_EMPTY),
        ('', VALID_CLIENT_ID, ERROR_CODE_INVALID, ERROR_MESSAGE_EMPTY),
    ],
)
async def test_403(
        taxi_signal_device_api,
        pgsql,
        api_key,
        client_id,
        error_code,
        error_msg,
):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=OK_REQUEST_JSON,
        headers={'X-API-Key': api_key, 'X-Client-ID': client_id},
    )
    assert response.status_code == 403, response.text
    assert response.json() == {'code': error_code, 'message': error_msg}
    _check_api_key_state(pgsql, VALID_CLIENT_ID, VALID_API_KEY, 9, True, False)
    _check_api_key_state(
        pgsql, VALID_CLIENT_ID, VERY_OLD_API_KEY, 0, True, False,
    )
    _check_api_key_state(
        pgsql, VALID_CLIENT_ID, DISABLED_API_KEY, 5, False, False,
    )
