# encoding=utf-8
import random
import re

import dateutil.parser
import pytest

from tests_signal_device_registration_api import crypto


ENDPOINT = '/v1/devices/registration'

BASIC_FIELDS = [
    'public_key',
    'hardware_version',
    'imei',
    'serial_number',
    'total_ram_bytes',
    'comment',
]
NOW_FIELDS = ['updated_at', 'created_at']
PASSWORD_FIELDS = ['bluetooth_password', 'user_password', 'wifi_password']
MAC_FIELDS = ['mac_wlan0', 'mac_eth0', 'mac_usb_modem']
FIELDS = (
    ['id', 'is_alive']
    + BASIC_FIELDS
    + NOW_FIELDS
    + PASSWORD_FIELDS
    + MAC_FIELDS
)

NOW = '2019-12-13T18:01:00+03:00'

# openssl ecparam -genkey -name prime256v1 | openssl ec -pubout
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEFTrwi4xkz0nc0YMZenXFTudcRznC
iTv4/bdLIxzpCxmqfPn84g+i9tzh1phs9uRN3EkzjeqsQgE2bHMAItC/4A==
-----END PUBLIC KEY-----"""
ANOTHER_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAErl86UkyTGjQ7s8WwfyGPoxHD2vMx
+a9t/f8IIL2v2adl480M1oQGra0O1YAdiwFSQANaJ6s2qqQmU96RJvb5Mg==
-----END PUBLIC KEY-----"""


def generate_mac():
    return '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def generate_version():
    return '{:1d}.{:03d}'.format(random.randint(1, 9), random.randint(0, 999))


def generate_imei():
    return '{:015d}'.format(random.randint(10 ** 14, 10 ** 15 - 1))


def generate_serial():
    return '{:010x}'.format(random.randint(10 ** 10, 10 ** 15 - 1))


def generate_total_ram_bytes():
    return random.randint(1048576, 1048576 * 6)  # 1 to 6 GiB


def generate_registration_request():
    return {
        'mac_address': {
            'wlan0': generate_mac(),
            'eth0': generate_mac(),
            'usb_modem': generate_mac(),
        },
        'public_key': PUBLIC_KEY,
        'hardware_version': generate_version(),
        'imei': generate_imei(),
        'serial_number': generate_serial(),
        'total_ram_bytes': generate_total_ram_bytes(),
        'comment': 'комментарий',
    }


def check_password(password):
    assert re.match(r'([a-z]+\.){5}[a-z]+', password) is not None


def select_device(pgsql, public_id):
    assert public_id is not None
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} from signal_device_api.devices '
        'WHERE public_id=\'{}\''.format(','.join(FIELDS), public_id),
    )
    db_devices = list(db)
    assert len(db_devices) == 1, db_devices
    return {k: v for (k, v) in zip(FIELDS, db_devices[0])}


def kill_device(pgsql, public_id):
    assert public_id is not None
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'UPDATE signal_device_api.devices SET is_alive = FALSE '
        'WHERE public_id=\'{}\''.format(public_id),
    )


@pytest.mark.now(NOW)
async def test_ok(taxi_signal_device_registration_api, pgsql):
    request_json = generate_registration_request()
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 200

    response_json = response.json()
    device = select_device(pgsql, response_json.get('device_id'))

    assert device.get('id') is not None
    assert device.get('is_alive')

    for field in BASIC_FIELDS:
        if field == 'serial_number':
            assert device.get(field) == request_json.get(field).upper()
        else:
            assert device.get(field) == request_json.get(field)

    mac_address = request_json.get('mac_address')
    for mac_field in MAC_FIELDS:
        assert device.get(mac_field) == mac_address.get(mac_field[4:])

    for password_field in PASSWORD_FIELDS:
        password = response_json.get(password_field)
        check_password(password)
        assert crypto.decode_password(device[password_field]) == password

    for now_field in NOW_FIELDS:
        assert device.get(now_field) == dateutil.parser.parse(NOW)


@pytest.mark.parametrize(
    'mac_address',
    [
        ({'wlan0': '90:a7:78:d1:ad:fa', 'eth0': '90:a7:78:d1:ad:fa'}),
        ({'wlan0': '00:70:49:1a:89:ab', 'usb_modem': '00:70:49:1a:89:ab'}),
        (
            {
                'wlan0': '8e:44:c2:ea:36:4c',
                'eth0': 'a3:0e:05:42:34:8e',
                'usb_modem': 'a3:0e:05:42:34:8e',
            }
        ),
    ],
)
async def test_duplicate_mac(taxi_signal_device_registration_api, mac_address):
    request_json = generate_registration_request()
    request_json['mac_address'] = mac_address
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'mac_address must contain different addresses',
    }


async def test_invalid_public_key(taxi_signal_device_registration_api):
    request_json = generate_registration_request()
    request_json['public_key'] = 'trash'
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 400
    assert response.json().get('code') == '400'
    assert response.json().get('message').startswith('invalid public_key: ')


async def test_idempotency(taxi_signal_device_registration_api, pgsql):
    request_json = generate_registration_request()

    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 200

    response_json = response.json()
    device_id = response_json.get('device_id')
    device = select_device(pgsql, device_id)

    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == response_json
    assert select_device(pgsql, device_id) == device


async def test_ignore_dead(taxi_signal_device_registration_api, pgsql):
    request_json = generate_registration_request()

    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 200

    device_id = response.json().get('device_id')
    kill_device(pgsql, device_id)

    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 200
    assert response.json().get('device_id') != device_id


async def test_kill(taxi_signal_device_registration_api, pgsql):
    request_json = generate_registration_request()
    response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )
    assert response.status_code == 200
    device_id = response.json().get('device_id')
    assert device_id is not None

    device = select_device(pgsql, device_id)
    assert device.get('is_alive')

    request_json['public_key'] = ANOTHER_PUBLIC_KEY
    another_response = await taxi_signal_device_registration_api.post(
        ENDPOINT, json=request_json,
    )

    assert another_response.status_code == 200
    another_device_id = another_response.json().get('device_id')
    assert another_device_id is not None
    assert another_device_id != device_id

    device = select_device(pgsql, device_id)
    assert not device.get('is_alive')
