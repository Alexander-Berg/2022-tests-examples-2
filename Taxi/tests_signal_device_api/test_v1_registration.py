import copy
import re

import pytest

from tests_signal_device_api import common
from tests_signal_device_api import crypto


ENDPOINT = '/v1/registration'

AES_KEY = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEmYB6e5eBFtRajXxCsIDm6AXoL/xN
zLsG2LMul+PWC+fPMA5QnUMpBdk/BsUdqabRzkKkbxO2aXxxwY3xGoC2iw==
-----END PUBLIC KEY-----"""
PUBLIC_KEY_2 = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEFpcGZmJFn6LM2gHX79N42FyJNqoT
+Qof8PFKl5ceujGTb1TcxgpLiThZ9b3Mt5+ObUOJopHWZXW8h57qFtkH/w==
-----END PUBLIC KEY-----

"""
DECLARED_DEVICE_ID = 1
IMEI = '123456789012345'
MAC_WLAN_0 = '38:fe:38:8e:84:e0'
MAC_BLUETOOTH = 'e6:32:23:fc:23:9f'
SERIAL_NUMBER = '1234567890ABC'
HARDWARE_VERSION = '1.0.test'
COMMENT = 'test_comment'
OK_REGISTRATION = {
    'public_key': PUBLIC_KEY,
    'imei': IMEI,
    'mac_wlan0': MAC_WLAN_0,
    'mac_bluetooth': MAC_BLUETOOTH,
    'serial_number': SERIAL_NUMBER,
    'hardware_version': HARDWARE_VERSION,
    'comment': COMMENT,
}
DIFFERENT_REGISTRATION_VALUES = {
    'public_key': PUBLIC_KEY_2,
    'imei': '0' * 15,
    'mac_wlan0': 'aa:' * 5 + 'aa',
    'mac_bluetooth': 'bb:' * 5 + 'bb',
    'hardware_version': 'garbage',
    'comment': 'garbage',
}
VALID_PASSWORD = (
    'amcClw/yzgKHwmypL6BXXF5/INFMZlnWDBVah1YsBUb2jBLWcTB'
    'IMRWEE7L8XLvKBsdg504/t5ZHPht/rsm2VmVTRlpSzhu1k7/IA/6MwkQ='
)
INSERT_DEVICE_TEMPLATE = """
INSERT INTO signal_device_api.devices (
    is_alive,
    declared_device_id,
    public_id,
    public_key,
    imei,
    mac_wlan0,
    mac_bluetooth,
    serial_number,
    hardware_version,
    bluetooth_password,
    user_password,
    wifi_password,
    comment,
    created_at,
    updated_at
)
VALUES (
    '{}',
    1,
    '1234567890',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);"""
TEMPLATE_DEFAULTS = [
    PUBLIC_KEY,
    IMEI,
    MAC_WLAN_0,
    MAC_BLUETOOTH,
    SERIAL_NUMBER,
    HARDWARE_VERSION,
    VALID_PASSWORD,
    VALID_PASSWORD,
    VALID_PASSWORD,
    COMMENT,
]
TEMPLATE_NOT_REGISTERED = TEMPLATE_DEFAULTS.copy()
TEMPLATE_NOT_REGISTERED[0] = ''

INSERT_DEAD_DEVICE = INSERT_DEVICE_TEMPLATE.format('FALSE', *TEMPLATE_DEFAULTS)
INSERT_NOT_REGISTERED_DEVICE = INSERT_DEVICE_TEMPLATE.format(
    'FALSE', *TEMPLATE_NOT_REGISTERED,
)
INSERT_LIVE_DEVICE = INSERT_DEVICE_TEMPLATE.format('TRUE', *TEMPLATE_DEFAULTS)

BASIC_FIELDS = [
    'public_key',
    'hardware_version',
    'imei',
    'serial_number',
    'mac_wlan0',
    'mac_bluetooth',
    'comment',
]
NOW_FIELDS = ['updated_at', 'created_at']
PASSWORD_FIELDS = ['bluetooth_password', 'user_password', 'wifi_password']
FIELDS = (
    ['id', 'is_alive', 'declared_device_id']
    + BASIC_FIELDS
    + NOW_FIELDS
    + PASSWORD_FIELDS
)


def _check_password(password):
    assert re.match(r'([a-z]+\.){5}[a-z]+', password) is not None


def _select_device(pgsql, public_id):
    assert public_id is not None
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} from signal_device_api.devices '
        'WHERE public_id=\'{}\''.format(','.join(FIELDS), public_id),
    )
    db_devices = list(db)
    assert len(db_devices) == 1, db_devices
    return {k: v for (k, v) in zip(FIELDS, db_devices[0])}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'additional_query, is_serial_lower, is_serial_number_declared, '
    'expected_device_id',
    [
        (INSERT_NOT_REGISTERED_DEVICE, False, True, 1),
        (INSERT_LIVE_DEVICE, False, True, 1),
    ],
)
async def test_200(
        taxi_signal_device_api,
        pgsql,
        additional_query,
        is_serial_lower,
        is_serial_number_declared,
        expected_device_id,
):
    if additional_query:
        with pgsql['signal_device_api_meta_db'].cursor() as cursor:
            cursor.execute(additional_query)

    request_json = copy.deepcopy(OK_REGISTRATION)
    original_serial_number = request_json['serial_number']
    if is_serial_number_declared:
        with pgsql['signal_device_api_meta_db'].cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO signal_device_api.declared_serial_numbers
                    (serial_number)
                VALUES ('{original_serial_number}');
                """,
            )

    serial_number = request_json['serial_number']
    if is_serial_lower:
        request_json['serial_number'] = request_json['serial_number'].lower()
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 200, response.text
    common.check_alr_inserted(
        pgsql,
        serial_number=serial_number,
        field_affected='v1_registration_at',
    )
    response_json = response.json()
    device = _select_device(pgsql, response_json.get('device_id'))
    assert device.get('declared_device_id') == DECLARED_DEVICE_ID
    for field in BASIC_FIELDS:
        if is_serial_lower and field == 'serial_number':
            assert device.get(field) == request_json.get(field).upper()
        else:
            assert device.get(field) == request_json.get(field)
    for password_field in PASSWORD_FIELDS:
        password = response_json.get(password_field)
        _check_password(password)
        assert crypto.decode_password(device[password_field]) == password
    for now_field in NOW_FIELDS:
        common.assert_now(device.get(now_field))
    assert device.get('id') == expected_device_id

    with pgsql['signal_device_api_meta_db'].cursor() as cursor:
        cursor.execute(
            'SELECT serial_number '
            'FROM signal_device_api.declared_serial_numbers',
        )
        serial_numbers = list(cursor)
        assert len(serial_numbers) == 1
        assert serial_numbers[0][0] == original_serial_number


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_403_dead_device(taxi_signal_device_api, pgsql):
    with pgsql['signal_device_api_meta_db'].cursor() as cursor:
        cursor.execute(INSERT_DEAD_DEVICE)

    request_json = copy.deepcopy(OK_REGISTRATION)

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'device with serial number 1234567890ABC is not alive',
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'is_serial_lower, is_serial_number_declared',
    [(True, True), (False, True)],
)
async def test_500(
        taxi_signal_device_api,
        pgsql,
        is_serial_lower,
        is_serial_number_declared,
):
    request_json = copy.deepcopy(OK_REGISTRATION)
    original_serial_number = request_json['serial_number']
    if is_serial_number_declared:
        with pgsql['signal_device_api_meta_db'].cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO signal_device_api.declared_serial_numbers
                    (serial_number)
                VALUES ('{original_serial_number}');
                """,
            )

    if is_serial_lower:
        request_json['serial_number'] = request_json['serial_number'].lower()
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 500, response.text


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_200_public_key_trim(taxi_signal_device_api, pgsql):
    with pgsql['signal_device_api_meta_db'].cursor() as cursor:
        cursor.execute(
            INSERT_NOT_REGISTERED_DEVICE.replace(
                PUBLIC_KEY, PUBLIC_KEY + '\n',
            ),
        )
    request_json = copy.deepcopy(OK_REGISTRATION)

    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    device = _select_device(pgsql, response_json.get('device_id'))
    assert device.get('declared_device_id') == DECLARED_DEVICE_ID
    for field in BASIC_FIELDS:
        assert device.get(field) == request_json.get(field)
    for password_field in PASSWORD_FIELDS:
        password = response_json.get(password_field)
        _check_password(password)
        assert crypto.decode_password(device[password_field]) == password
    for now_field in NOW_FIELDS:
        common.assert_now(device.get(now_field))


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'jwt_token, err_msg',
    [
        (
            common.generate_jwt_aes(ENDPOINT, AES_KEY, {}, OK_REGISTRATION)[
                :-1
            ]
            + 'A',
            'Failed to verify JWT',
        ),
        (
            common.generate_jwt_aes(
                ENDPOINT, AES_KEY[:-1] + 'A', {}, OK_REGISTRATION,
            ),
            'Failed to verify JWT',
        ),
        (
            common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {'key': 'garbage'}, OK_REGISTRATION,
            ),
            'Hash mismatch for the query',
        ),
        (
            common.generate_jwt_aes(
                ENDPOINT,
                AES_KEY,
                {},
                {**copy.deepcopy(OK_REGISTRATION), **{'key': 'garbage'}},
            ),
            'Hash mismatch for the body',
        ),
    ],
)
async def test_403_crypto_error(taxi_signal_device_api, jwt_token, err_msg):
    response = await taxi_signal_device_api.post(
        ENDPOINT, json=OK_REGISTRATION, headers={'X-JWT-Signature': jwt_token},
    )
    assert response.status_code == 403, response.text
    assert response.json() == {'code': '403', 'message': err_msg}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_404(taxi_signal_device_api):
    request_json = copy.deepcopy(OK_REGISTRATION)
    missing_serial = '1' * 16
    request_json['serial_number'] = missing_serial
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': '404',
        'message': 'Device with serial number {} has not been declared'.format(
            missing_serial,
        ),
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'request_json',
    [
        {
            **copy.deepcopy(OK_REGISTRATION),
            **{key: DIFFERENT_REGISTRATION_VALUES[key]},
        }
        for key in DIFFERENT_REGISTRATION_VALUES
    ],
)
async def test_409(taxi_signal_device_api, pgsql, request_json):
    with pgsql['signal_device_api_meta_db'].cursor() as cursor:
        cursor.execute(INSERT_LIVE_DEVICE)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': '409',
        'message': (
            'Device has already been registered with different parameters'
        ),
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'incorrect_public_key', ['', 'not_public_key', PUBLIC_KEY + 'sx'],
)
async def test_incorrect_public_key(
        taxi_signal_device_api, pgsql, incorrect_public_key,
):
    request_json = copy.deepcopy(OK_REGISTRATION)
    request_json['public_key'] = incorrect_public_key
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == 400, response.text
